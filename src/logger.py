import os
import logging
from datetime import datetime

def setup_logger():
    """Konfiguruje logger z zapisem do pliku i konsoli."""
    # Utwórz folder logs jeśli nie istnieje
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Utwórz nazwę pliku z datą i godziną
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(logs_dir, f"article_generator_{timestamp}.log")
    
    # Konfiguracja formatu logów
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Handler dla pliku
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Handler dla konsoli
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Konfiguracja głównego loggera
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Rozpoczęcie logowania do pliku: {log_file}")
    
    return logger
