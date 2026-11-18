import psycopg
from psycopg.rows import dict_row
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_connection(as_dict: bool = False):
    """
    Retorna uma conexão ativa com o banco PostgreSQL.
    Se as_dict=True, os cursores retornarão dicionários em vez de tuplas.
    """
    row_factory = dict_row if as_dict else None
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        row_factory=row_factory
    )

def test_connection():
    """
    Testa a conexão com o banco e retorna uma tupla (sucesso: bool, mensagem: str).
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), version();")
                db_name, version = cur.fetchone()
                return True, f"Conectado ao banco '{db_name}' com sucesso! ({version.split()[0]} {version.split()[1]})"
    except Exception as e:
        return False, f"Falha na conexão: {e}"

def init_db():
    """
    Garante que as tabelas necessárias existam no banco de dados.
    """
    ddl = """
    CREATE TABLE IF NOT EXISTS alunos (
        id_aluno SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        matricula VARCHAR(20) NOT NULL UNIQUE,
        email VARCHAR(100),
        telefone VARCHAR(20),
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS livros (
        id_livro SERIAL PRIMARY KEY,
        titulo VARCHAR(150) NOT NULL,
        autor VARCHAR(100) NOT NULL,
        isbn VARCHAR(20) UNIQUE,
        quantidade_total INT NOT NULL DEFAULT 1,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS emprestimos (
        id_emprestimo SERIAL PRIMARY KEY,
        id_aluno INT NOT NULL REFERENCES alunos(id_aluno),
        id_livro INT NOT NULL REFERENCES livros(id_livro),
        data_emprestimo TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        data_previsao_devolucao DATE NOT NULL,
        data_devolucao TIMESTAMP NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'EMPRESTADO'
    );
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()
