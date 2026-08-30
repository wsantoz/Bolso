import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import check_password_hash
from banco import criar_tabelas, criar_usuario, buscar_usuario, adicionar_gasto, listar_gastos, total_gasto
from ia import gerar_analise, gerar_resposta_chat

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave-temporaria-so-para-desenvolvimento")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
criar_tabelas()

def logado():
    return "usuario_id" in session

# ---------- PÁGINAS ----------

@app.route("/")
def home():
    if not logado():
        return redirect(url_for("login"))
    return render_template("index.html", username=session.get("username"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        senha = request.form.get("senha", "")
        usuario = buscar_usuario(username)
        if usuario and check_password_hash(usuario[2], senha):
            session["usuario_id"] = usuario[0]
            session["username"] = usuario[1]
            return redirect(url_for("home"))
        return render_template("login.html", erro="Usuário ou senha inválidos.")
    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        senha = request.form.get("senha", "")
        if not username or not senha:
            return render_template("registro.html", erro="Preencha todos os campos.")
        if len(senha) < 6:
            return render_template("registro.html", erro="A senha precisa ter pelo menos 6 caracteres.")
        sucesso = criar_usuario(username, senha)
        if not sucesso:
            return render_template("registro.html", erro="Esse nome de usuário já existe.")
        return redirect(url_for("login"))
    return render_template("registro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------- API ----------

@app.route("/api/gastos", methods=["GET"])
def api_listar_gastos():
    if not logado():
        return jsonify({"erro": "Não autenticado."}), 401
    gastos = listar_gastos(session["usuario_id"])
    lista = [
        {"id": g[0], "descricao": g[1], "valor": g[2], "categoria": g[3], "data": g[4]}
        for g in gastos
    ]
    return jsonify({"gastos": lista, "total": total_gasto(session["usuario_id"])})

@app.route("/api/gastos", methods=["POST"])
def api_adicionar_gasto():
    if not logado():
        return jsonify({"erro": "Não autenticado."}), 401
    dados = request.get_json()
    descricao = dados.get("descricao", "").strip()[:200]
    valor = dados.get("valor")
    categoria = (dados.get("categoria") or None)
    if categoria:
        categoria = categoria.strip()[:50]

    if not descricao or valor is None:
        return jsonify({"erro": "Descrição e valor são obrigatórios."}), 400
    try:
        valor = float(valor)
        if valor <= 0 or valor > 1_000_000:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"erro": "Valor inválido."}), 400

    adicionar_gasto(session["usuario_id"], descricao, valor, categoria)
    return jsonify({"mensagem": "Gasto registrado com sucesso!"}), 201

@app.route("/api/analise", methods=["GET"])
def api_analise():
    if not logado():
        return jsonify({"erro": "Não autenticado."}), 401
    gastos = listar_gastos(session["usuario_id"])
    resultado = gerar_analise(gastos)
    return jsonify({"analise": resultado})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    if not logado():
        return jsonify({"erro": "Não autenticado."}), 401
    dados = request.get_json()
    pergunta = (dados.get("mensagem") or "").strip()[:500]
    historico = dados.get("historico") or []
    if not pergunta:
        return jsonify({"erro": "Mensagem vazia."}), 400

    gastos = listar_gastos(session["usuario_id"])
    resposta = gerar_resposta_chat(gastos, historico, pergunta)
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(debug=False)