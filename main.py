import openai
import os
from dotenv import load_dotenv
from config import OPENAI_MODEL, MAX_TOKENS, PROMPT

# Załaduj klucz API z pliku .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_text():
    with open("ai.txt", "r", encoding="utf-8") as file:
        return file.read().strip()

def create_prompt():
    ai_text = get_ai_text()
    return f"{PROMPT.strip()}\n\n{ai_text}"

def main():
    # Przygotowanie prompta jako wiadomości
    messages = [{"role": "user", "content": create_prompt()}]
    
    # Wysyłanie prompta do API OpenAI
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS
    )
    
    # Pobranie odpowiedzi z modelu
    html_content = response.choices[0].message['content'].strip()

    # Zapisanie odpowiedzi do pliku HTML
    with open("artykul.html", "w", encoding="utf-8") as file:
        file.write(html_content)

if __name__ == "__main__":
    main()