import logging
import os
from src.article_processor import ArticleProcessor
from src.logger import setup_logger

def main():
    # Konfiguracja loggera
    setup_logger()
    logger = logging.getLogger(__name__)
    
    try:
        # Użyj konkretnego pliku ai.txt
        script_dir = os.path.dirname(os.path.abspath(__file__))
        input_file = os.path.join(script_dir, 'ai.txt')
        
        # Przetwórz artykuł - walidacja jest teraz w ArticleProcessor
        processor = ArticleProcessor()
        processor.process_file(input_file)
        
    except Exception as e:
        logger.error(f"Wystąpił błąd: {str(e)}")

if __name__ == "__main__":
    main()