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
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        login VARCHAR(50) NOT NULL UNIQUE,
        senha_hash VARCHAR(256) NOT NULL,
        cargo VARCHAR(50) DEFAULT 'Operador',
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

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

    -- Trigger para validar quantidade disponível de livros
    CREATE OR REPLACE FUNCTION fn_valida_emprestimo()
    RETURNS TRIGGER AS $$
    DECLARE
        v_quantidade_total INT;
        v_emprestimos_ativos INT;
    BEGIN
        SELECT quantidade_total INTO v_quantidade_total
        FROM livros
        WHERE id_livro = NEW.id_livro;

        SELECT COUNT(*) INTO v_emprestimos_ativos
        FROM emprestimos
        WHERE id_livro = NEW.id_livro 
          AND data_devolucao IS NULL;

        IF v_emprestimos_ativos >= v_quantidade_total THEN
            RAISE EXCEPTION 'Empréstimo negado: Este livro possui apenas % unidade(s) e já está emprestado! Aguarde a devolução.', v_quantidade_total;
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_valida_emprestimo ON emprestimos;
    CREATE TRIGGER trg_valida_emprestimo
    BEFORE INSERT ON emprestimos
    FOR EACH ROW
    EXECUTE FUNCTION fn_valida_emprestimo();

    -- Trigger para validar exclusão de aluno (permite se empréstimos foram devolvidos)
    CREATE OR REPLACE FUNCTION fn_valida_exclusao_aluno()
    RETURNS TRIGGER AS $$
    DECLARE
        v_emprestimos_ativos INT;
    BEGIN
        SELECT COUNT(*) INTO v_emprestimos_ativos
        FROM emprestimos
        WHERE id_aluno = OLD.id_aluno 
          AND (data_devolucao IS NULL OR status != 'DEVOLVIDO');

        IF v_emprestimos_ativos > 0 THEN
            RAISE EXCEPTION 'Não é possível excluir o aluno "%": existem % empréstimo(s) pendente(s) de devolução!', OLD.nome, v_emprestimos_ativos;
        END IF;

        -- Remove os registros de empréstimos já devolvidos para permitir a exclusão do aluno
        DELETE FROM emprestimos WHERE id_aluno = OLD.id_aluno;

        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_valida_exclusao_aluno ON alunos;
    CREATE TRIGGER trg_valida_exclusao_aluno
    BEFORE DELETE ON alunos
    FOR EACH ROW
    EXECUTE FUNCTION fn_valida_exclusao_aluno();
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()
