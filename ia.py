import os
import requests

MODELO = "gemini-3.6-flash"

def _url():
    api_key = os.environ.get("GEMINI_API_KEY")
    return f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={api_key}"

def _chamar_ia(prompt):
    try:
        resposta = requests.post(
            _url(),
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        resposta.raise_for_status()
        dados = resposta.json()
        return dados["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as erro:
        return f"Não foi possível falar com a IA agora. Detalhe: {erro}"

def _contexto_gastos(lista_gastos):
    if not lista_gastos:
        return "O usuário ainda não registrou nenhum gasto."
    linhas = [f"- {g[1]}: R$ {g[2]:.2f} ({g[3] or 'sem categoria'}) em {g[4]}" for g in lista_gastos]
    return "Gastos registrados pelo usuário:\n" + "\n".join(linhas)

def gerar_analise(lista_gastos):
    contexto = _contexto_gastos(lista_gastos)
    prompt = (
        "Você é o assistente financeiro do app Bolso. Analise os gastos abaixo. "
        "Categorize os que estiverem 'sem categoria'. Dê um resumo curto, "
        "aponte onde a pessoa mais gastou, e dê 1 ou 2 dicas práticas e específicas "
        "de como ela poderia economizar, baseado nos dados reais dela:\n\n"
        f"{contexto}"
    )
    return _chamar_ia(prompt)

def gerar_resposta_chat(lista_gastos, historico, pergunta):
    contexto = _contexto_gastos(lista_gastos)
    transcricao = ""
    for msg in historico:
        papel = "Usuário" if msg["role"] == "user" else "Bolso"
        transcricao += f"{papel}: {msg['texto']}\n"

    prompt = (
        "Você é o Bolso, um assistente financeiro pessoal amigável e direto. "
        "Você tem acesso aos gastos reais do usuário abaixo e deve usar esses dados "
        "pra responder de forma específica e útil — não genérica. "
        "Seja proativo: se notar um padrão problemático, avise. "
        "Dê conselhos práticos e acionáveis. Seja breve (poucos parágrafos).\n\n"
        f"{contexto}\n\n"
        f"Conversa até agora:\n{transcricao}\n"
        f"Usuário: {pergunta}\n"
        "Bolso:"
    )
    return _chamar_ia(prompt)