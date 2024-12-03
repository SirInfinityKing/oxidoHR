"""
Konfiguracja dla aplikacji generującej artykuły HTML.

Stałe:
    MAX_TOKENS (int): Maksymalna liczba tokenów dla odpowiedzi API
    PROMPT (str): Szablon promptu do generowania HTML
"""

# Konfiguracja limitów API
MAX_TOKENS = 1500

# Konfiguracja promptu
PROMPT = """
Przekształć poniższy tekst w kod HTML według tego dokładnego formatu:

Format wyjściowy MUSI wyglądać tak:
<article>
    <h1>[pierwszy akapit jako tytuł]</h1>
    <p>[treść]</p>
</article>

Zasady:
1. Użyj DOKŁADNIE powyższego formatu
2. NIE dodawaj żadnych innych tagów (<html>, <head>, <body>, etc.)
3. NIE dodawaj żadnego tekstu przed ani po kodzie HTML
4. NIE dodawaj komentarzy ani wyjaśnień
5. Zachowaj oryginalną treść bez zmian
6. Dodawaj obrazki w kluczowych miejscach tekstu:
   - Po tytule dla zilustrowania głównego tematu
   - Przy ważnych koncepcjach lub przykładach
   - Na końcu sekcji dla podsumowania
7. Dla każdego obrazka w atrybucie alt MUSISZ zawrzeć następujące informacje:
   a) Przedmiot/obiekt: Co dokładnie ma być pokazane (np. "robot przemysłowy spawający karoserię samochodu")
   b) Szczegółowy opis: Jak ma wyglądać scena, w tym:
      - Otoczenie i tło (np. "nowoczesna hala produkcyjna z liniami montażowymi")
      - Oświetlenie (np. "jasne światło przemysłowe z góry, niebieskie iskry spawania")
      - Perspektywa (np. "ujęcie z boku pod lekkim kątem")
      - Detale (np. "widoczne przewody i złącza robota, drobne cząsteczki w powietrzu")
   c) Styl artystyczny:
      - Technika (np. "fotorealizm", "ilustracja techniczna", "rendering 3D")
      - Paleta kolorów (np. "industrialne szarości z akcentami niebieskiego")
      - Nastrój (np. "dynamiczny", "profesjonalny", "futurystyczny")
8. Możesz używać <h2> dla podtytułów
9. Dziel tekst na akapity używając <p>

Przykład z obrazkiem:
<article>
    <h1>Automatyzacja w Przemyśle Motoryzacyjnym</h1>
    <figure>
        <img src="image_placeholder.jpg" alt="Przedmiot: Zrobotyzowana linia montażowa samochodów elektrycznych. Szczegółowy opis: Nowoczesna, sterylnie czysta hala produkcyjna z pięcioma robotami przemysłowymi pracującymi nad szkieletem samochodu elektrycznego. Jasne, równomierne oświetlenie LED z góry. Ujęcie szerokie pokazujące całą linię z perspektywy lekko podwyższonej. W tle widoczne stanowiska kontroli jakości z monitorami wyświetlającymi dane produkcyjne. Na pierwszym planie robot precyzyjnie montujący drzwi do karoserii. Styl: Fotorealistyczny rendering 3D, wysoki kontrast, chłodna paleta kolorów z dominacją bieli i srebra, akcenty świetlne LED w kolorze niebieskim, nastrój high-tech i futurystyczny">
        <figcaption>Zautomatyzowana linia montażowa najnowszej generacji</figcaption>
    </figure>
    <p>Pierwszy akapit tekstu...</p>
    <h2>Zastosowania w Produkcji</h2>
    <p>Kolejny akapit...</p>
</article>

Oto tekst do przekształcenia:
"""