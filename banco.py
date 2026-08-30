import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def conectar():
    return sqlite3.connect("gastos.db")

def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT,
            data TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)
    conexao.commit()
    conexao.close()

# ---------- USUÁRIOS ----------

def criar_usuario(username, senha):
    conexao = conectar()
    cursor = conexao.cursor()
    senha_hash = generate_password_hash(senha)
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, senha_hash) VALUES (?, ?)",
            (username, senha_hash)
        )
        conexao.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexao.close()

def buscar_usuario(username):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, username, senha_hash FROM usuarios WHERE username = ?", (username,))
    usuario = cursor.fetchone()
    conexao.close()
    return usuario

# ---------- GASTOS ----------

def adicionar_gasto(usuario_id, descricao, valor, categoria=None):
    conexao = conectar()
    cursor = conexao.cursor()
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    cursor.execute(
        "INSERT INTO gastos (usuario_id, descricao, valor, categoria, data) VALUES (?, ?, ?, ?, ?)",
        (usuario_id, descricao, valor, categoria, data_hoje)
    )
    conexao.commit()
    conexao.close()

def listar_gastos(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, descricao, valor, categoria, data FROM gastos WHERE usuario_id = ? ORDER BY id DESC",
        (usuario_id,)
    )
    resultados = cursor.fetchall()
    conexao.close()
    return resultados

def total_gasto(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT SUM(valor) FROM gastos WHERE usuario_id = ?", (usuario_id,))
    total = cursor.fetchone()[0]
    conexao.close()
    return total if total else 0