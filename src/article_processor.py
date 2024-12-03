import os
import logging
import tkinter as tk
from tkinter import filedialog
import glob
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import time
import random
from enum import Enum
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import pickle

from .file_handler import FileHandler
from .html_validator import HTMLValidator
from .validator import Validator
from .config import MAX_TOKENS, PROMPT

logger = logging.getLogger(__name__)

class APIErrorType(Enum):
    RATE_LIMIT = "rate_limit"
    CONTEXT_LENGTH = "context_length"
    INVALID_REQUEST = "invalid_request"
    AUTH_ERROR = "auth_error"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

@dataclass
class APIError:
    type: APIErrorType
    message: str
    retryable: bool
    retry_after: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

class APIErrorHandler:
    """Klasa obsługująca błędy API."""
    
    ERROR_PATTERNS = {
        "rate limit": APIErrorType.RATE_LIMIT,
        "too many requests": APIErrorType.RATE_LIMIT,
        "context length": APIErrorType.CONTEXT_LENGTH,
        "maximum context length": APIErrorType.CONTEXT_LENGTH,
        "invalid request": APIErrorType.INVALID_REQUEST,
        "unauthorized": APIErrorType.AUTH_ERROR,
        "authentication failed": APIErrorType.AUTH_ERROR,
        "internal server error": APIErrorType.SERVER_ERROR,
        "service unavailable": APIErrorType.SERVER_ERROR,
        "timeout": APIErrorType.TIMEOUT,
        "deadline exceeded": APIErrorType.TIMEOUT
    }
    
    @classmethod
    def classify_error(cls, error: Exception) -> APIError:
        """Klasyfikuje błąd API na podstawie komunikatu."""
        error_message = str(error).lower()
        
        # Sprawdź znane wzorce błędów
        for pattern, error_type in cls.ERROR_PATTERNS.items():
            if pattern in error_message:
                retryable = error_type in [
                    APIErrorType.RATE_LIMIT,
                    APIErrorType.SERVER_ERROR,
                    APIErrorType.TIMEOUT
                ]
                
                # Próba wydobycia czasu oczekiwania dla rate limit
                retry_after = None
                if error_type == APIErrorType.RATE_LIMIT:
                    import re
                    retry_match = re.search(r"retry after (\d+)", error_message)
                    if retry_match:
                        retry_after = int(retry_match.group(1))
                    else:
                        retry_after = 60  # domyślne opóźnienie dla rate limit
                
                return APIError(
                    type=error_type,
                    message=str(error),
                    retryable=retryable,
                    retry_after=retry_after
                )
        
        # Nieznany błąd
        return APIError(
            type=APIErrorType.UNKNOWN,
            message=str(error),
            retryable=False
        )

class ResponseCache:
    """Klasa obsługująca buforowanie odpowiedzi API."""
    
    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            # Użyj katalogu .cache w katalogu projektu
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cache_dir = os.path.join(project_dir, '.cache')
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        
        # Wyczyść cache przy starcie
        self.clear()
        
    def clear(self):
        """Czyści cache."""
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob('*.pkl'):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Nie można usunąć pliku cache {cache_file}: {e}")
        
    def _get_cache_key(self, prompt: str) -> str:
        """Generuje klucz cache na podstawie promptu."""
        return hashlib.md5(prompt.encode()).hexdigest()
        
    def _get_cache_path(self, cache_key: str) -> Path:
        """Zwraca ścieżkę do pliku cache."""
        return self.cache_dir / f"{cache_key}.pkl"
        
    def get(self, prompt: str) -> Optional[str]:
        """Pobiera odpowiedź z cache."""
        cache_key = self._get_cache_key(prompt)
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            with self._lock:
                try:
                    with cache_path.open('rb') as f:
                        cached_data = pickle.load(f)
                        logger.debug(f"Znaleziono w cache: {cache_key}")
                        return cached_data['response']
                except Exception as e:
                    logger.warning(f"Błąd odczytu cache: {str(e)}")
                    return None
        return None
        
    def set(self, prompt: str, response: str) -> None:
        """Zapisuje odpowiedź do cache."""
        cache_key = self._get_cache_key(prompt)
        cache_path = self._get_cache_path(cache_key)
        
        with self._lock:
            try:
                cached_data = {
                    'prompt': prompt,
                    'response': response,
                    'timestamp': time.time()
                }
                with cache_path.open('wb') as f:
                    pickle.dump(cached_data, f)
                logger.debug(f"Zapisano w cache: {cache_key}")
            except Exception as e:
                logger.warning(f"Błąd zapisu cache: {str(e)}")

# Klasa odpowiedzialna za przetwarzanie artykułów
# Funkcjonalności:
# - Komunikacja z API Groq
# - Buforowanie odpowiedzi
# - Wielowątkowe przetwarzanie dużych plików
# - Walidacja HTML
# - Obsługa błędów API
class ArticleProcessor:
    """Główna klasa przetwarzająca artykuły."""
    
    def __init__(self, max_workers: int = 3):
        """Inicjalizuje obiekt ArticleProcessor.
        
        Args:
            max_workers: Maksymalna liczba wątków do przetwarzania plików
        """
        self._initialize_api()
        self.file_handler = FileHandler()
        self.html_validator = HTMLValidator()
        self.cache = ResponseCache()
        self.max_workers = max_workers
        self._lock = threading.Lock()
        
    def _initialize_api(self) -> None:
        """Inicjalizuje połączenie z API."""
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Nie znaleziono GROQ_API_KEY w zmiennych środowiskowych")
            
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            model_name="llama3-70b-8192"
        )
        
    def _validate_content_size(self, content: str) -> None:
        """
        Sprawdza czy zawartość nie przekracza limitów.
        
        Args:
            content: Tekst do sprawdzenia
            
        Raises:
            ValueError: Gdy tekst jest za krótki lub przekracza limit
        """
        if not content or len(content.strip()) < 10:
            raise ValueError("Tekst jest za krótki (minimum 10 znaków)")
            
        # Sprawdź maksymalny rozmiar pliku z konfiguracji
        max_size = int(os.getenv('MAX_FILE_SIZE_MB', 10)) * 1024 * 1024  # MB na bajty
        if len(content.encode('utf-8')) > max_size:
            raise ValueError(f"Tekst przekracza maksymalny rozmiar {max_size/1024/1024}MB")
            
        # Dodatkowa walidacja bezpieczeństwa
        if any(suspicious in content.lower() for suspicious in ['<script', 'javascript:', 'data:']):
            raise ValueError("Wykryto potencjalnie niebezpieczną zawartość")
            
    def _split_large_content(self, content: str) -> List[str]:
        """
        Dzieli duży tekst na mniejsze części do przetworzenia.
        
        Args:
            content: Tekst do podziału
            
        Returns:
            List[str]: Lista mniejszych fragmentów tekstu
        """
        # Maksymalna liczba tokenów na część (z marginesem bezpieczeństwa)
        max_tokens_per_chunk = 6000  # llama3-70b-8192 ma limit 8192, zostawiamy miejsce na prompt
        
        # Przybliżona liczba tokenów (zakładamy średnio 4 znaki na token)
        tokens_per_char = 0.25
        estimated_tokens = len(content) * tokens_per_char
        
        if estimated_tokens <= max_tokens_per_chunk:
            return [content]
            
        # Podziel na akapity
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph_tokens = len(paragraph) * tokens_per_char
            
            if current_length + paragraph_tokens > max_tokens_per_chunk and current_chunk:
                # Zapisz aktualny chunk i zacznij nowy
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_length = paragraph_tokens
            else:
                current_chunk.append(paragraph)
                current_length += paragraph_tokens
        
        # Dodaj ostatni chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            
        logger.info(f"Podzielono tekst na {len(chunks)} części")
        return chunks
        
    def _process_chunk(self, chunk: str, chunk_index: int, total_chunks: int) -> str:
        """Przetwarza pojedynczy fragment tekstu."""
        prompt = f"{PROMPT}\n\nCzęść {chunk_index + 1}/{total_chunks}:\n\n{chunk}"
        
        # Sprawdź cache
        cached_response = self.cache.get(prompt)
        if cached_response:
            logger.info(f"Użyto cache dla części {chunk_index + 1}/{total_chunks}")
            return cached_response
            
        # Generuj nową odpowiedź
        html_content = self.generate_html(prompt)
        
        # Zapisz do cache
        self.cache.set(prompt, html_content)
        
        return html_content
        
    def get_input_file(self) -> str:
        """
        Pobiera ścieżkę do pliku wejściowego.
        
        Returns:
            str: Ścieżka do pliku wejściowego
        """
        # Najpierw sprawdź ai.txt
        if os.path.exists("ai.txt"):
            return "ai.txt"
            
        # Potem szukaj innych plików .txt
        txt_files = glob.glob("*.txt")
        if txt_files:
            return txt_files[0]
            
        # Jeśli nie znaleziono, pokaż okno wyboru pliku
        root = tk.Tk()
        root.withdraw()  # Ukryj główne okno
        
        file_path = filedialog.askopenfilename(
            title="Wybierz plik tekstowy",
            filetypes=[("Pliki tekstowe", "*.txt")]
        )
        
        if not file_path:
            raise ValueError("Nie wybrano pliku")
            
        return file_path
        
    def create_prompt(self, input_file: str) -> str:
        """
        Tworzy prompt z pliku wejściowego.
        
        Args:
            input_file: Ścieżka do pliku wejściowego
            
        Returns:
            str: Prompt do wysłania do API
        """
        content = self.file_handler.read_file(input_file)
        self._validate_content_size(content)
        
        # Utwórz wiadomość dla modelu
        message = f"{PROMPT}\n\n{content}"
        logger.info("Utworzono prompt z pliku wejściowego")
        logger.debug(f"Długość tekstu wejściowego: {len(content)} znaków")
        
        return message
        
    def generate_html(self, prompt: str) -> str:
        """
        Generuje kod HTML używając API.
        
        Args:
            prompt: Prompt do wysłania do API
            
        Returns:
            str: Wygenerowany kod HTML
            
        Raises:
            ValueError: Gdy odpowiedź API jest nieprawidłowa
        """
        max_retries = 3
        base_delay = 5  # sekundy
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Wywołaj API z odpowiednim promptem
                messages = [HumanMessage(content=prompt)]
                response = self.llm.invoke(messages)
                html_content = response.content.strip()
                
                # Debug - pokaż fragment odpowiedzi
                logger.info("Odpowiedź z API (fragment):")
                content_preview = html_content[:200] + "..." + html_content[-200:] if len(html_content) > 400 else html_content
                logger.info(content_preview)
                
                # Sprawdź czy odpowiedź nie jest pusta
                if not html_content:
                    raise ValueError("API zwróciło pustą odpowiedź")
                
                # Wyczyść odpowiedź - znajdź i wyodrębnij kod HTML
                article_start = html_content.find("<article")
                if article_start == -1:
                    raise ValueError("Nie znaleziono tagu <article> w odpowiedzi API")
                    
                article_end = html_content.rfind("</article>")
                if article_end == -1:
                    raise ValueError("Nie znaleziono zamykającego tagu </article> w odpowiedzi API")
                
                # Wytnij fragment od <article> do </article> włącznie
                html_content = html_content[article_start:article_end + len("</article>")]
                
                # Waliduj wygenerowany HTML
                html_content = self._validate_html(html_content)
                
                return html_content
                
            except Exception as e:
                # Klasyfikuj błąd
                api_error = APIErrorHandler.classify_error(e)
                last_error = api_error
                
                # Loguj szczegóły błędu
                logger.error(f"Błąd API: {api_error.type.value} - {api_error.message}")
                
                # Sprawdź czy błąd jest możliwy do ponowienia
                if not api_error.retryable or attempt >= max_retries - 1:
                    break
                
                # Oblicz czas oczekiwania
                if api_error.retry_after:
                    wait_time = api_error.retry_after
                else:
                    # Exponential backoff z jitterem
                    wait_time = base_delay * (2 ** attempt) + random.uniform(0, 2)
                
                logger.warning(
                    f"Próba {attempt + 1}/{max_retries} nie powiodła się: {api_error.type.value}. "
                    f"Kolejna próba za {wait_time:.1f} sekund..."
                )
                
                time.sleep(wait_time)
        
        # Jeśli dotarliśmy tutaj, wszystkie próby nie powiodły się
        if last_error:
            error_message = f"Błąd API po {max_retries} próbach: {last_error.type.value} - {last_error.message}"
            if last_error.type == APIErrorType.CONTEXT_LENGTH:
                error_message += "\nTekst jest zbyt długi dla modelu. Spróbuj podzielić go na mniejsze części."
            elif last_error.type == APIErrorType.AUTH_ERROR:
                error_message += "\nSprawdź poprawność klucza API w pliku .env"
            raise ValueError(error_message)
        
        raise ValueError(f"Nieznany błąd po {max_retries} próbach")

    def _validate_html(self, html_content: str) -> str:
        """
        Waliduje wygenerowany kod HTML.
        
        Args:
            html_content: Kod HTML do sprawdzenia
            
        Returns:
            str: Zwalidowany kod HTML
            
        Raises:
            ValueError: Gdy HTML jest niepoprawny lub niebezpieczny
        """
        # Podstawowa walidacja HTML
        self.html_validator.feed(html_content)
        validation_results = self.html_validator.validate()
        
        if not validation_results:
            missing_tags = self.html_validator.required_tags - self.html_validator.found_tags
            raise ValueError(f"Brakuje wymaganych tagów: {', '.join(missing_tags)}")
            
        # Proste sprawdzenie bezpieczeństwa
        unsafe_patterns = [
            '<script', 'javascript:', 'data:',
            'onclick=', 'onload=', 'onerror=',
            'onmouseover=', 'onmouseout=', 'onsubmit='
        ]
        
        for pattern in unsafe_patterns:
            if pattern in html_content.lower():
                html_content = html_content.replace(pattern, '')
                logger.warning(f"Usunięto niebezpieczny wzorzec: {pattern}")
        
        return html_content
        
    def process_file(self, input_file: str) -> None:
        """
        Przetwarza konkretny plik wejściowy.
        
        Args:
            input_file: Ścieżka do pliku wejściowego
        """
        try:
            # Walidacja pliku wejściowego
            Validator.validate_input_file(input_file)
            
            # Walidacja środowiska przed przetwarzaniem
            Validator.validate_environment()
            
            # Wczytaj zawartość pliku
            content = self.file_handler.read_file(input_file)
            self._validate_content_size(content)
            
            # Podziel na mniejsze części jeśli potrzeba
            chunks = self._split_large_content(content)
            logger.info(f"Podzielono tekst na {len(chunks)} części")
            
            # Przetwórz każdą część
            results = []
            for i, chunk in enumerate(chunks, 1):
                html = self._process_chunk(chunk, i, len(chunks))
                results.append(html)
            
            # Połącz wyniki
            final_html = "\n".join(results)
            
            # Zapisz wynik
            output_file = self.file_handler.save_file(final_html, input_file)
            if output_file:
                logger.info(f"Zapisano wynik do pliku: {output_file}")
            else:
                raise ValueError("Nie udało się zapisać pliku wyjściowego")
                
        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania pliku {input_file}: {str(e)}")
            raise

    def process_article(self) -> None:
        """Główna metoda przetwarzająca artykuł."""
        try:
            input_file = self.get_input_file()
            logger.info(f"Wybrany plik wejściowy: {input_file}")
            
            self.process_file(input_file)
            
        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania artykułu: {str(e)}")
            raise
