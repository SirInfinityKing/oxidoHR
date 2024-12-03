import os
import logging
from pathlib import Path
from typing import Tuple, Optional

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    tk = None
    filedialog = None

logger = logging.getLogger(__name__)

# Klasa obsługująca operacje na plikach
# Funkcjonalności:
# - Wybór plików wejściowych przez użytkownika
# - Wykrywanie kodowania plików
# - Bezpieczne operacje I/O
# - Walidacja rozszerzeń plików
class FileHandler:
    """Klasa odpowiedzialna za operacje na plikach."""
    
    ENCODINGS = ['utf-8', 'cp1250', 'iso-8859-2', 'ascii']
    MIN_CONTENT_LENGTH = 50
    
    @staticmethod
    def try_read_with_encodings(filename: str) -> Tuple[str, str]:
        """
        Próbuje odczytać plik używając różnych kodowań.
        
        Args:
            filename: Ścieżka do pliku
            
        Returns:
            Tuple[str, str]: (zawartość pliku, użyte kodowanie)
            
        Raises:
            UnicodeDecodeError: Gdy nie udało się odczytać pliku żadnym kodowaniem
        """
        errors = []
        
        for encoding in FileHandler.ENCODINGS:
            try:
                with open(filename, 'r', encoding=encoding) as file:
                    content = file.read().strip()
                    return content, encoding
            except UnicodeDecodeError as e:
                errors.append(f"Próba {encoding}: {str(e)}")
                continue
                
        raise UnicodeDecodeError(
            f"Nie udało się odczytać pliku {filename} z żadnym z kodowań: "
            f"{', '.join(FileHandler.ENCODINGS)}. Błędy: {'; '.join(errors)}"
        )

    @staticmethod
    def read_file(filename: str) -> str:
        """
        Odczytuje zawartość pliku z automatycznym wykrywaniem kodowania.
        
        Args:
            filename: Ścieżka do pliku
            
        Returns:
            str: Zawartość pliku
            
        Raises:
            FileNotFoundError: Gdy plik nie istnieje
            ValueError: Gdy plik jest pusty lub za krótki
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Nie znaleziono pliku {filename}")
            
        if os.path.getsize(filename) == 0:
            raise ValueError(f"Plik {filename} jest pusty")
            
        content, encoding = FileHandler.try_read_with_encodings(filename)
        
        if len(content) < FileHandler.MIN_CONTENT_LENGTH:
            raise ValueError(
                f"Zawartość pliku {filename} jest za krótka "
                f"(minimum {FileHandler.MIN_CONTENT_LENGTH} znaków)"
            )
            
        return content

    @staticmethod
    def save_file(content: str, original_path: str = None) -> Optional[str]:
        """
        Zapisuje wygenerowany HTML do pliku.
        
        Args:
            content (str): Treść do zapisania
            original_path (str, optional): Ścieżka oryginalnego pliku
            
        Returns:
            Optional[str]: Ścieżka zapisanego pliku lub None w przypadku błędu
        """
        try:
            # Ustal nazwę pliku wyjściowego
            if original_path:
                output_dir = os.path.dirname(os.path.abspath(original_path))
                base_name = "artykul"  # Zawsze używaj nazwy "artykul"
            else:
                output_dir = os.getcwd()
                base_name = "artykul"
            
            # Znajdź pierwszą wolną nazwę pliku
            counter = 0
            while True:
                suffix = f"_{counter}" if counter > 0 else ""
                output_path = os.path.join(output_dir, f"{base_name}{suffix}.html")
                if not os.path.exists(output_path):
                    break
                counter += 1
                if counter > 100:  # Zabezpieczenie przed nieskończoną pętlą
                    raise ValueError("Nie można znaleźć wolnej nazwy pliku")
            
            # Utwórz katalog jeśli nie istnieje
            os.makedirs(output_dir, exist_ok=True)
            
            # Zapisz plik
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania pliku: {str(e)}")
            return None

    @staticmethod
    def get_next_filename(base_filename: str, extension: str) -> str:
        """
        Generuje następną dostępną nazwę pliku.
        
        Args:
            base_filename: Bazowa nazwa pliku
            extension: Rozszerzenie pliku
            
        Returns:
            str: Następna dostępna nazwa pliku
        """
        counter = 1
        while True:
            if counter == 1:
                new_filename = f"{base_filename}.{extension}"
            else:
                new_filename = f"{base_filename}_{counter}.{extension}"
                
            if not os.path.exists(new_filename):
                return new_filename
            counter += 1

    @staticmethod
    def find_text_files(directory="."):
        """
        Wyszukuje pliki tekstowe w podanym katalogu.
        
        Args:
            directory (str): Ścieżka do katalogu do przeszukania (domyślnie bieżący)
            
        Returns:
            list: Lista znalezionych plików tekstowych
        """
        text_extensions = {'.txt', '.md', '.text'}
        text_files = []
        
        try:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path) and Path(file).suffix.lower() in text_extensions:
                    # Ignoruj pliki zaczynające się od kropki i checklisty
                    if not os.path.basename(file).startswith('.') and not 'checklist' in file.lower():
                        text_files.append(file_path)
            
            logger.info(f"Znaleziono pliki tekstowe: {text_files}")
            return text_files
            
        except Exception as e:
            logger.error(f"Błąd podczas wyszukiwania plików: {str(e)}")
            return []

    @staticmethod
    def select_input_file():
        """
        Wybiera plik wejściowy - najpierw szuka w bieżącym katalogu,
        jeśli nie znajdzie, otwiera okno dialogowe.
        
        Returns:
            str: Ścieżka do wybranego pliku lub None
        """
        # Najpierw szukaj w bieżącym katalogu
        current_dir = os.getcwd()
        text_files = FileHandler.find_text_files(current_dir)
        
        if text_files:
            # Jeśli znaleziono pliki, użyj pierwszego który nie jest checklistą
            selected_file = text_files[0]
            logger.info(f"Automatycznie wybrano plik: {selected_file}")
            return selected_file  # Już mamy pełną ścieżkę
        
        # Sprawdź czy tkinter jest dostępny
        if tk is None:
            logger.error("Nie można otworzyć okna wyboru pliku - moduł tkinter nie jest dostępny")
            return None
            
        # Jeśli nie znaleziono plików, otwórz okno dialogowe
        logger.info("Nie znaleziono plików tekstowych, otwieram okno wyboru...")
        root = tk.Tk()
        root.withdraw()  # Ukryj główne okno
        
        file_path = filedialog.askopenfilename(
            title="Wybierz plik tekstowy",
            filetypes=[
                ("Pliki tekstowe", "*.txt;*.md;*.text"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        
        if file_path:
            logger.info(f"Wybrano plik: {file_path}")
            return file_path
        
        logger.warning("Nie wybrano żadnego pliku")
        return None
