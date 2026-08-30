import os
from google import genai

# Pega a chave de API que já está salva no seu computador
api_key = os.environ.get("GEMINI_API_KEY")

# Cria o cliente que vai conversar com a IA
client = genai.Client(api_key=api_key)

# Faz uma pergunta simples pra IA
resposta = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Explique em uma frase o que é uma API."
)

# Mostra a resposta na tela
print(resposta.text)
