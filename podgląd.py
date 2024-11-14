import tkinter as tk
from tkinter import ttk
from tkhtmlview import HTMLLabel

# Funkcja do wczytania treści artykułu z pliku artykul.html
def load_article():
    try:
        with open("artykul.html", "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "<p>Artykuł nie został znaleziony. Proszę wstawić artykuł do pliku <strong>artykul.html</strong>.</p>"

# Funkcja do wczytania szablonu HTML z pliku szablon.html
def load_template():
    try:
        with open("szablon.html", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "<p>Szablon HTML nie został znaleziony. Proszę dodać plik <strong>szablon.html</strong>.</p>"

# Funkcja do zapisywania podglądu HTML do pliku
def save_preview(html_content):
    with open("podglad.html", "w", encoding="utf-8") as file:
        file.write(html_content)

class HTMLPreviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML Previewer")
        self.root.geometry("800x500")

        # Ustawienie układu kolumn
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        # Tworzenie lewej strony - edytor HTML
        self.create_html_input_panel()

        # Tworzenie prawej strony - podgląd HTML
        self.create_html_preview_panel()

        # Wczytanie artykułu do edytora HTML
        self.load_initial_content()

    def create_html_input_panel(self):
        frame_left = ttk.Frame(self.root, padding=10)
        frame_left.grid(row=0, column=0, sticky="nsew")
        
        label = ttk.Label(frame_left, text="HTML Input")
        label.pack(anchor="nw", pady=(0, 5))

        # Pole tekstowe do wklejania kodu HTML
        self.html_input = tk.Text(frame_left, wrap="word", height=30)
        self.html_input.pack(fill="both", expand=True)

        # Przycisk do odświeżenia podglądu
        update_button = ttk.Button(frame_left, text="Update Preview", command=self.update_preview)
        update_button.pack(anchor="s", pady=(5, 0))

    def create_html_preview_panel(self):
        frame_right = ttk.Frame(self.root, padding=10)
        frame_right.grid(row=0, column=1, sticky="nsew")

        label = ttk.Label(frame_right, text="HTML Preview")
        label.pack(anchor="nw", pady=(0, 5))

        # Wyświetlanie podglądu HTML
        self.html_preview = HTMLLabel(frame_right, html="", width=40, height=30)
        self.html_preview.pack(fill="both", expand=True)
        self.html_preview.fit_height()

        # Przycisk do zapisywania podglądu
        save_button = ttk.Button(frame_right, text="Zapisz podgląd w HTML", command=self.save_html_preview)
        save_button.pack(anchor="s", pady=(5, 0))

    def load_initial_content(self):
        # Wczytanie artykułu i szablonu, a następnie wstawienie artykułu do szablonu
        article_content = load_article()
        html_template = load_template()
        full_content = html_template.replace("<!-- Wklejony artykuł pojawi się tutaj -->", article_content)
        self.html_input.insert("1.0", full_content)

    def update_preview(self):
        # Aktualizacja podglądu HTML na podstawie treści wprowadzonej przez użytkownika
        html_content = self.html_input.get("1.0", tk.END)
        self.html_preview.set_html(html_content)

    def save_html_preview(self):
        # Zapisanie HTML do pliku podglad.html
        html_content = self.html_input.get("1.0", tk.END)
        save_preview(html_content)
        print("Podgląd zapisany jako podglad.html")

if __name__ == "__main__":
    root = tk.Tk()
    app = HTMLPreviewApp(root)
    root.mainloop()
