import os
import hashlib
from database import get_connection

def gerar_hash_senha(senha: str) -> str:
    """Gera um hash SHA-256 com salt aleatório."""
    salt = os.urandom(16).hex()
    hash_obj = hashlib.sha256((salt + senha).encode("utf-8")).hexdigest()
    return f"{salt}${hash_obj}"

def verificar_senha(senha: str, senha_armazenada: str) -> bool:
    """Verifica se a senha em texto plano bate com o salt$hash armazenado."""
    try:
        salt, hash_esperado = senha_armazenada.split("$")
        hash_calculado = hashlib.sha256((salt + senha).encode("utf-8")).hexdigest()
        return hash_calculado == hash_esperado
    except Exception:
        return False

def inicializar_usuarios_padrao():
    """Cria a tabela de usuários e insere o usuário 'admin' caso não existam usuários cadastrados."""
    ddl = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        login VARCHAR(50) NOT NULL UNIQUE,
        senha_hash VARCHAR(256) NOT NULL,
        cargo VARCHAR(50) DEFAULT 'Operador',
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
            cur.execute("SELECT COUNT(*) FROM usuarios;")
            total = cur.fetchone()[0]
            if total == 0:
                senha_padrao_hash = gerar_hash_senha("admin123")
                cur.execute("""
                    INSERT INTO usuarios (nome, login, senha_hash, cargo)
                    VALUES ('Administrador', 'admin', %s, 'Administrador');
                """, (senha_padrao_hash,))
        conn.commit()

def autenticar_usuario(login: str, senha: str):
    """
    Autentica um usuário pelo login e senha.
    Retorna o dicionário com os dados do usuário em caso de sucesso, ou None se inválido.
    """
    inicializar_usuarios_padrao()
    query = "SELECT id_usuario, nome, login, senha_hash, cargo FROM usuarios WHERE login = %s;"
    with get_connection(as_dict=True) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (login.strip(),))
            user = cur.fetchone()
            if user and verificar_senha(senha.strip(), user["senha_hash"]):
                return {
                    "id_usuario": user["id_usuario"],
                    "nome": user["nome"],
                    "login": user["login"],
                    "cargo": user["cargo"]
                }
    return None

def cadastrar_usuario(nome: str, login: str, senha: str, cargo: str = "Operador"):
    """
    Cadastra um novo usuário no banco com senha criptografada.
    """
    inicializar_usuarios_padrao()
    login_limpo = login.strip().lower()
    nome_limpo = nome.strip()

    if not nome_limpo or not login_limpo or not senha:
        raise ValueError("Nome, login e senha são obrigatórios.")

    if len(senha) < 4:
        raise ValueError("A senha deve conter no mínimo 4 caracteres.")

    query_check = "SELECT COUNT(*) FROM usuarios WHERE login = %s;"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query_check, (login_limpo,))
            if cur.fetchone()[0] > 0:
                raise ValueError(f"O login '{login_limpo}' já está em uso por outro usuário.")

            senha_hash = gerar_hash_senha(senha)
            cur.execute("""
                INSERT INTO usuarios (nome, login, senha_hash, cargo)
                VALUES (%s, %s, %s, %s)
                RETURNING id_usuario;
            """, (nome_limpo, login_limpo, senha_hash, cargo))
            novo_id = cur.fetchone()[0]
        conn.commit()
        return novo_id

def listar_usuarios():
    """Retorna lista com dados públicos dos usuários cadastrados."""
    inicializar_usuarios_padrao()
    query = "SELECT id_usuario, nome, login, cargo, data_cadastro FROM usuarios ORDER BY id_usuario ASC;"
    with get_connection(as_dict=True) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()
