# Konfiguracja dla generatora artykułów HTML

# Maksymalna liczba tokenów dla modelu
MAX_TOKENS = 32000

# Prompt dla generowania HTML
PROMPT = """Przekształć poniższy tekst w semantyczny kod HTML zgodnie z następującymi wymaganiami:

1. Struktura dokumentu:
   - Zwróć TYLKO zawartość, która powinna znaleźć się między tagami <body> i </body>
   - NIE dodawaj tagów <html>, <head>, <body> ani żadnego kodu CSS/JavaScript
   - Użyj <article> jako głównego kontenera treści
   - Podziel treść na logiczne <section> z odpowiednimi nagłówkami
   - Zachowaj hierarchiczną strukturę dokumentu
   - NIE DODAWAJ żadnych metadanych (autor, data, źródło itp.)

2. Semantyczne tagi HTML:
   - <article> jako główny kontener z atrybutem role="main"
   - <header> na początku artykułu zawierający TYLKO <h1> dla głównego tytułu
   - <section> dla każdej głównej sekcji treści, zawierającej:
     * <h2> lub <h3> dla tytułu sekcji
     * <p> dla akapitów
     * <blockquote> dla cytatów
   - <aside> dla treści pobocznych
   - <ul> lub <ol> z <li> dla list

3. Obrazy i multimedia:
   - Wstawiaj obrazy w strategicznych miejscach używając struktury:
     <figure>
       <img src="image_placeholder.jpg" alt="[PROMPT DO AI:
         Styl: [określ styl grafiki]
         Scena: [szczegółowy opis głównego obiektu/sceny]
         Kontekst: [szerszy kontekst i otoczenie]
         Nastrój: [atmosfera i emocje]
         Kolory: [główna paleta kolorów]
         Kompozycja: [układ i perspektywa]
         Szczegóły: [ważne detale do uwzględnienia]
         Format: [preferowane proporcje obrazu]]"
         loading="lazy">
       <figcaption>[zwięzły, informacyjny podpis]</figcaption>
     </figure>
   - Umieszczaj obrazy tylko tam, gdzie znacząco wspierają treść
   - Każdy prompt musi być kompletny i szczegółowy

4. Dostępność i SEO:
   - Używaj nagłówków w logicznej kolejności (h1 > h2 > h3)
   - Dodawaj aria-label do sekcji gdy potrzebne
   - Zapewnij alt dla wszystkich obrazów
   - Używaj list dla grupowania powiązanych elementów
   - Dodawaj role="presentation" dla obrazów dekoracyjnych

5. Zasady formatowania:
   - Zachowaj oryginalne podziały na akapity
   - Używaj <strong> i <em> dla wyróżnień w tekście
   - Grupuj powiązane treści w <section>
   - Zachowaj czystą i konsekwentną strukturę kodu

6. Ważne:
   - NIE dodawaj żadnych metadanych ani informacji o autorze/źródle
   - NIE używaj atrybutów class ani id
   - NIE dodawaj stylów inline ani JavaScript
   - Zachowaj semantyczną i logiczną strukturę
   - Waliduj poprawność zagnieżdżenia tagów

Przetwórz poniższy tekst zgodnie z tymi wytycznymi:"""
