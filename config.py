OPENAI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1500

PROMPT = """
Dodaj tagi HTML do strukturyzacji treści, takie jak <h1>, <h2>, <p>, </br> oraz 2 grafiki jako okładka i w treści. Oznacz je z użyciem tagu z atrybutem src="image_placeholder.jpg

Dodaj atrybut alt do każdego obrazka z dokładnym promptem, który możemy użyć do wygenerowania grafiki. Umieść podpisy pod grafikami używając odpowiedniego tagu HTML.

Nie dołączaj znaczników <html>, <head> ani <body>

Nie zmieniaj treści artykułu
"""