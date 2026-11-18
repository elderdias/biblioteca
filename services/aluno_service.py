from psycopg import errors
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
    """
    Exclui um aluno pelo ID.
    Graças à trigger no banco de dados:
    - Se o aluno possuir empréstimos em andamento (não devolvidos), a exclusão é bloqueada.
    - Se todos os empréstimos já foram devolvidos, o histórico de devoluções é liberado
      e o aluno é excluído com sucesso.
    """
    query = "DELETE FROM alunos WHERE id_aluno = %s;"
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (id_aluno,))
                linhas_afetadas = cur.rowcount
            conn.commit()
            if linhas_afetadas == 0:
                raise ValueError("Aluno não encontrado no banco de dados.")
            return True
    except errors.RaiseException as e:
        # Mensagem vinda da trigger fn_valida_exclusao_aluno()
        msg = e.diag.message_primary if hasattr(e, 'diag') and e.diag else str(e)
        raise ValueError(msg)
    except errors.ForeignKeyViolation:
        raise ValueError("Não é possível excluir o aluno pois existem registros vinculados a ele.")
    except Exception as e:
        raise RuntimeError(f"Erro ao excluir aluno: {e}")
