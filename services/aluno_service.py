from database import get_connection

def listar_alunos():
    """Retorna lista com todos os alunos cadastrados."""
    query = """
        SELECT id_aluno, nome, matricula, email, telefone, data_cadastro
        FROM alunos
        ORDER BY id_aluno ASC;
    """
    with get_connection(as_dict=True) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def buscar_aluno_por_id(id_aluno: int):
    """Busca um aluno pelo ID."""
    query = "SELECT * FROM alunos WHERE id_aluno = %s;"
    with get_connection(as_dict=True) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (id_aluno,))
            return cur.fetchone()

def buscar_aluno_por_matricula(matricula: str):
    """Busca um aluno pela matrícula."""
    query = "SELECT * FROM alunos WHERE matricula = %s;"
    with get_connection(as_dict=True) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (matricula,))
            return cur.fetchone()

def cadastrar_aluno(nome: str, matricula: str, email: str = None, telefone: str = None):
    """
    Cadastra um novo aluno no banco de dados.
    Retorna o id_aluno cadastrado.
    """
    query = """
        INSERT INTO alunos (nome, matricula, email, telefone)
        VALUES (%s, %s, %s, %s)
        RETURNING id_aluno;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (nome.strip(), matricula.strip(), email.strip() if email else None, telefone.strip() if telefone else None))
            novo_id = cur.fetchone()[0]
        conn.commit()
        return novo_id

def atualizar_aluno(id_aluno: int, nome: str, matricula: str, email: str = None, telefone: str = None):
    """Atualiza as informações de um aluno existente."""
    query = """
        UPDATE alunos
        SET nome = %s, matricula = %s, email = %s, telefone = %s
        WHERE id_aluno = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (nome.strip(), matricula.strip(), email.strip() if email else None, telefone.strip() if telefone else None, id_aluno))
            linhas_afetadas = cur.rowcount
        conn.commit()
        return linhas_afetadas > 0

def excluir_aluno(id_aluno: int):
    """Exclui um aluno pelo ID."""
    query = "DELETE FROM alunos WHERE id_aluno = %s;"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (id_aluno,))
            linhas_afetadas = cur.rowcount
        conn.commit()
        return linhas_afetadas > 0
