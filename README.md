# Generator Artykułów HTML

## Spis Treści
1. [Wprowadzenie](#wprowadzenie)
   - [Opis Projektu](#opis-projektu)
   - [Kluczowe Funkcje](#kluczowe-funkcje)
2. [Wymagania i Instalacja](#wymagania-i-instalacja)
   - [Wymagania Systemowe](#wymagania-systemowe)
   - [Proces Instalacji](#proces-instalacji)
   - [Konfiguracja Środowiska](#konfiguracja-środowiska)
3. [Użytkowanie](#użytkowanie)
   - [Szybki Start](#szybki-start)
   - [Szczegółowe Opcje](#szczegółowe-opcje)
   - [Podgląd i Weryfikacja](#podgląd-i-weryfikacja)
4. [Struktura Projektu](#struktura-projektu)
   - [Organizacja Plików](#organizacja-plików)
   - [Konwencje Kodu](#konwencje-kodu)
5. [Rozwiązywanie Problemów](#rozwiązywanie-problemów)
   - [Typowe Problemy](#typowe-problemy)
   - [Dobre Praktyki](#dobre-praktyki)
6. [Licencja](#licencja)

## Wprowadzenie

### Opis Projektu
OxidoHR to narzędzie do przetwarzania i generowania artykułów HTML z wykorzystaniem AI. Program został zaprojektowany z myślą o bezpieczeństwie i transparentności.

### Kluczowe Funkcje
- Przetwarzanie plików tekstowych na format HTML
- Walidacja kodu HTML
- Bezpieczne buforowanie wyników
- Obsługa błędów API
- Podgląd wygenerowanych plików HTML

## Wymagania i Instalacja

### Wymagania Systemowe
- Python 3.8 lub nowszy
- Minimum 4GB RAM
- Stabilne połączenie internetowe
- Klucz API Groq

### Proces Instalacji
1. **Klonowanie Repozytorium**
   ```bash
   git clone [adres-repozytorium]
   cd oxidoHR
   ```

2. **Instalacja Zależności**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Konfiguracja Środowiska
1. **Konfiguracja API**
   - Utwórz plik `.env` w głównym katalogu
   - Dodaj klucz API:
     ```env
     GROQ_API_KEY=twój-klucz-api
     ```

2. **Weryfikacja Instalacji**
   ```bash
   python main.py --test
   ```

## Użytkowanie

### Szybki Start

1. **Przygotowanie Pliku**
   - Umieść plik tekstowy w formacie UTF-8 w folderze projektu
   - Upewnij się, że plik jest poprawnie sformatowany (Markdown)

2. **Konwersja**
   ```bash
   python main.py artykul.txt
   ```

3. **Podgląd**
   ```bash
   python podgląd.py
   ```

### Szczegółowe Opcje

#### Parametry Konwersji
```bash
python main.py [opcje] plik1 [plik2 ...]

Opcje:
  --template PLIK     Użyj własnego szablonu HTML
  --output KATALOG    Zapisz wyniki w określonym katalogu
  --cache            Włącz cachowanie wyników API
  --verbose          Wyświetl szczegółowe logi
  --no-images        Pomiń generowanie promptów dla obrazów
```

#### Format Wejściowy
```markdown
# Tytuł Artykułu

## Podtytuł Sekcji

Tekst akapitu...

* Punkt listy
* Kolejny punkt
```

### Podgląd i Weryfikacja

1. **Uruchomienie Podglądu**
   ```bash
   python podgląd.py
   ```
   - Automatyczne wczytanie `artykul.html`
   - Interfejs z opcjami:
     - "Update Preview"
     - "Zapisz podgląd w html"

2. **Weryfikacja Online**
   - Użyj [W3Schools HTML Editor](https://www.w3schools.com/html/tryit.asp?filename=tryhtml_editor)
   - Wklej zawartość `podglad.html`
   - Sprawdź responsywność i poprawność HTML

## Struktura Projektu

### Organizacja Plików
```
oxidoHR/
├── main.py              # Główny skrypt
├── podgląd.py          # Narzędzie podglądu
├── szablon.html        # Szablon HTML
├── config.py           # Konfiguracja
├── requirements.txt    # Zależności
├── .env               # Zmienne środowiskowe
└── src/               # Moduły źródłowe
    ├── article_processor.py
    ├── file_handler.py
    └── validator.py
```

### Konwencje Kodu

#### Nazewnictwo
```python
# Klasy - PascalCase
class ArticleProcessor:
    pass

# Funkcje i zmienne - snake_case
def process_article():
    article_content = ""

# Stałe - UPPERCASE
MAX_WORKERS = 5
```

#### Formatowanie
- Wcięcia: 4 spacje
- Maksymalna długość linii: 88 znaków
- Odstępy między klasami: 2 linie
- Odstępy między metodami: 1 linia

#### Importy
```python
# Standardowa biblioteka
import os
import sys

# Zewnętrzne pakiety
import requests
import langchain

# Lokalne moduły
from .processor import ArticleProcessor
from .validator import HTMLValidator
```

#### Docstringi
```python
def process_file(self, filepath: str) -> bool:
    """
    Przetwarza plik tekstowy na HTML.

    Args:
        filepath (str): Ścieżka do pliku wejściowego

    Returns:
        bool: True jeśli przetwarzanie się powiodło

    Raises:
        FileNotFoundError: Gdy plik nie istnieje
        ValueError: Gdy zawartość jest nieprawidłowa
    """
    pass
```

#### Komentarze
```python
# TODO: Oznaczenie zadań do zrobienia
# FIXME: Oznaczenie błędów do naprawienia
# NOTE: Ważne uwagi
# WARNING: Ostrzeżenia
```

#### Type Hints
```python
from typing import List, Dict, Optional

def get_articles(
    paths: List[str],
    config: Optional[Dict[str, any]] = None
) -> List[str]:
    pass
```

## Rozwiązywanie Problemów

### Typowe Problemy

1. **Problemy z Kodowaniem**
   ```bash
   # Sprawdź kodowanie
   file -i artykul.txt
   
   # Konwertuj na UTF-8
   iconv -f WINDOWS-1250 -t UTF-8 artykul.txt > artykul_utf8.txt
   ```

2. **Problemy z API**
   ```bash
   # Sprawdź klucz API
   echo %GROQ_API_KEY%
   
   # Test połączenia
   python -c "import requests; print(requests.get('https://api.groq.com').status_code)"
   ```

### Dobre Praktyki

1. **Przygotowanie Tekstu**
   - Używaj UTF-8
   - Sprawdzaj formatowanie Markdown
   - Unikaj skomplikowanego formatowania

2. **Optymalizacja**
   - Używaj cache
   - Przetwarzaj wsadowo
   - Regularnie czyść cache

3. **Bezpieczeństwo**
   - Chroń klucz API
   - Twórz kopie zapasowe
   - Waliduj pliki wejściowe

## Licencja
MIT License

Copyright (c) 2024 OxidoHR

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
