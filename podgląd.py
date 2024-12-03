import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import webbrowser
import tempfile

class HTMLPreviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML Previewer")
        self.root.geometry("800x600")

        # Konfiguracja stylu
        style = ttk.Style()
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="white")
        style.configure("TButton", padding=5)

        # Ustawienie układu
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # Pasek narzędzi
        self.root.rowconfigure(1, weight=1)  # Główny obszar

        # Tworzenie paska narzędzi
        self.create_toolbar()

        # Tworzenie głównego obszaru
        self.create_main_area()

        # Inicjalizacja zmiennych
        self.current_file = None
        self.template_file = os.path.join(os.path.dirname(__file__), "szablon.html")
        self.preview_file = os.path.join(tempfile.gettempdir(), "preview.html")
        
        # Wczytanie domyślnego pliku
        self.load_default_file()

    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Przycisk wyboru pliku
        self.file_btn = ttk.Button(
            toolbar, 
            text="Wybierz plik HTML", 
            command=self.choose_file
        )
        self.file_btn.pack(side=tk.LEFT, padx=5)

        # Przycisk odświeżania
        self.refresh_btn = ttk.Button(
            toolbar, 
            text="Odśwież podgląd", 
            command=self.refresh_preview
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # Przycisk zapisu
        self.save_btn = ttk.Button(
            toolbar, 
            text="Zapisz", 
            command=self.save_preview
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        # Etykieta z aktualnym plikiem
        self.file_label = ttk.Label(toolbar, text="Brak wybranego pliku")
        self.file_label.pack(side=tk.LEFT, padx=20)

    def create_main_area(self):
        # Edytor tekstu
        self.text_editor = tk.Text(
            self.root,
            wrap="word",
            font=("Consolas", 12),
            bg="#1e1e1e",
            fg="white",
            insertbackground="white"
        )
        self.text_editor.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Przycisk podglądu
        preview_btn = ttk.Button(
            self.root,
            text="Otwórz podgląd w przeglądarce",
            command=self.open_preview
        )
        preview_btn.grid(row=2, column=0, pady=5)

    def load_template(self):
        """Wczytuje szablon HTML"""
        try:
            with open(self.template_file, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można wczytać szablonu: {str(e)}")
            return None

    def insert_content_into_template(self, content):
        """Wstawia treść artykułu do szablonu"""
        template = self.load_template()
        if template:
            # Wstawiamy treść w miejsce komentarza w szablonie
            return template.replace("<!-- Tutaj zostanie wklejony artykuł -->", content)
        return content

    def update_preview(self):
        """Aktualizuje plik podglądu i otwiera go w przeglądarce"""
        content = self.text_editor.get("1.0", tk.END)
        formatted_content = self.insert_content_into_template(content)
        
        try:
            with open(self.preview_file, "w", encoding="utf-8") as file:
                file.write(formatted_content)
            return True
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zapisać podglądu: {str(e)}")
            return False

    def open_preview(self):
        """Otwiera podgląd w domyślnej przeglądarce"""
        if self.update_preview():
            webbrowser.open(f"file://{self.preview_file}")

    def choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Wybierz plik HTML",
            filetypes=[("Pliki HTML", "*.html"), ("Wszystkie pliki", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.file_label.configure(text=f"Plik: {os.path.basename(file_path)}")
            self.load_html_file(file_path)

    def load_default_file(self):
        """Próbuje wczytać domyślny plik artykul.html"""
        default_file = os.path.join(os.path.dirname(__file__), "artykul.html")
        if os.path.exists(default_file):
            self.current_file = default_file
            self.file_label.configure(text=f"Plik: artykul.html")
            self.load_html_file(default_file)

    def load_html_file(self, file_path):
        """Wczytuje zawartość pliku HTML"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                # Aktualizuj edytor
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", content)
                # Aktualizuj podgląd
                self.update_preview()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można wczytać pliku: {str(e)}")

    def refresh_preview(self):
        """Odświeża podgląd"""
        self.update_preview()
        self.open_preview()

    def save_preview(self):
        """Zapisuje połączony szablon z artykułem do pliku"""
        if not self.text_editor.get("1.0", tk.END).strip():
            messagebox.showinfo("Info", "Brak treści do zapisania")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("Pliki HTML", "*.html")],
            initialfile="podglad.html"
        )
        if save_path:
            try:
                # Pobierz treść z edytora i połącz ją z szablonem
                content = self.text_editor.get("1.0", tk.END)
                formatted_content = self.insert_content_into_template(content)
                
                # Zapisz połączony plik
                with open(save_path, "w", encoding="utf-8") as target:
                    target.write(formatted_content)
                messagebox.showinfo("Sukces", f"Zapisano podgląd do {save_path}")
                
                # Jeśli zapisano jako podglad.html, odśwież widok w przeglądarce
                if os.path.basename(save_path) == "podglad.html":
                    self.preview_file = save_path
                    self.open_preview()
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można zapisać pliku: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HTMLPreviewApp(root)
    root.mainloop()
