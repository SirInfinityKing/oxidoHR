import html.parser
from typing import Dict, List, Set

class HTMLValidator(html.parser.HTMLParser):
    """Validator kodu HTML sprawdzający poprawność struktury."""
    
    def __init__(self):
        super().__init__()
        self.tags: List[str] = []
        self.required_tags: Set[str] = {"article", "h1", "p"}
        self.optional_tags: Set[str] = {"h2", "figure", "figcaption", "img"}
        self.found_tags: Set[str] = set()
        self.self_closing_tags: Set[str] = {"img", "br", "hr"}
        
    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        """
        Obsługa otwierającego tagu HTML.
        
        Args:
            tag: Nazwa tagu
            attrs: Lista atrybutów tagu
        """
        self.found_tags.add(tag)
        
        # Ignoruj self-closing tagi
        if tag in self.self_closing_tags:
            return
            
        self.tags.append(tag)
        
        # Sprawdź atrybuty img
        if tag == "img":
            attrs_dict = dict(attrs)
            if "src" not in attrs_dict or "alt" not in attrs_dict:
                raise ValueError("Tag img musi mieć atrybuty src i alt")
            if not attrs_dict["alt"].strip():
                raise ValueError("Atrybut alt nie może być pusty")
        
    def handle_endtag(self, tag: str) -> None:
        """
        Obsługa zamykającego tagu HTML.
        
        Args:
            tag: Nazwa tagu
        """
        # Ignoruj zamykające tagi dla self-closing tagów
        if tag in self.self_closing_tags:
            return
            
        if tag in self.tags:
            # Znajdź i usuń tag ze stosu
            tag_index = len(self.tags) - 1 - self.tags[::-1].index(tag)
            self.tags.pop(tag_index)
            
    def validate(self) -> Dict[str, bool]:
        """
        Sprawdza poprawność struktury HTML.
        
        Returns:
            Dict[str, bool]: Słownik z wynikami walidacji
        """
        return {
            "is_balanced": len(self.tags) == 0,
            "has_required_tags": self.required_tags.issubset(self.found_tags)
        }
