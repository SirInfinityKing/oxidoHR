import os
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class Validator:
    """Klasa odpowiedzialna za walidację konfiguracji i danych wejściowych."""
    
    @staticmethod
    def validate_environment() -> None:
        """Sprawdza czy środowisko jest poprawnie skonfigurowane.
        
        Raises:
            EnvironmentError: Gdy brak pliku .env lub klucza API
        """
        if not load_dotenv():
            raise EnvironmentError("Nie znaleziono pliku .env")
        
        if not os.getenv('GROQ_API_KEY'):
            raise EnvironmentError("Brak klucza API GROQ_API_KEY w pliku .env")
            
        logger.info("Środowisko zostało poprawnie zwalidowane")

    @staticmethod
    def validate_input_file(file_path: str) -> None:
        """Sprawdza czy plik wejściowy jest prawidłowy.
        
        Args:
            file_path: Ścieżka do pliku wejściowego
            
        Raises:
            FileNotFoundError: Gdy plik nie istnieje
            ValueError: Gdy plik jest nieprawidłowy
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Nie znaleziono pliku {file_path}")
        
        if not os.path.isfile(file_path):
            raise ValueError(f"{file_path} nie jest plikiem")
        
        if os.path.getsize(file_path) == 0:
            raise ValueError(f"Plik {file_path} jest pusty")
        
        if Path(file_path).suffix.lower() not in ['.txt', '.md']:
            raise ValueError(f"Nieobsługiwane rozszerzenie pliku: {file_path}")
            
        logger.info(f"Plik {file_path} został poprawnie zwalidowany")
