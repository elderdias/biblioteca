from datetime import datetime, timedelta
import psycopg
from psycopg import errors
from database import get_connection

def listar_emprestimos(apenas_ativos: bool = False):
    """
    Retorna a lista de empréstimos com os nomes dos alunos e títulos dos livros.
    Se apenas_ativos=True, retorna somente empréstimos com data_devolucao nula.
    """
    filtro = "WHERE e.data_devolucao IS NULL" if apenas_ativos else ""
    query = f"""
        SELECT 
            e.id_emprestimo,
            e.id_aluno,
            a.nome AS nome_aluno,
            a.matricula AS matricula_aluno,
            e.id_livro,
            l.titulo AS titulo_livro,
            e.data_emprestimo,
            e.data_previsao_devolucao,
            e.data_devolucao,
            e.status
        FROM emprestimos e
        JOIN alunos a ON e.id_aluno = a.id_aluno
        JOIN livros l ON e.id_livro = l.id_livro
        {filtro}
        ORDER BY e.data_emprestimo DESC;
    """
    with get_connection(as_dict=True) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def realizar_emprestimo(id_aluno: int, id_livro: int, dias_prazo: int = 7):
    """
    Registra um empréstimo.
    Calcula a data de previsão baseada nos dias de prazo informados.
    Se a quantidade de exemplares estiver esgotada, a trigger do banco acionará um erro.
    """
    data_previsao = (datetime.now() + timedelta(days=dias_prazo)).date()
    query = """
        INSERT INTO emprestimos (id_aluno, id_livro, data_previsao_devolucao, status)
        VALUES (%s, %s, %s, 'EMPRESTADO')
        RETURNING id_emprestimo;
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (id_aluno, id_livro, data_previsao))
                novo_id = cur.fetchone()[0]
            conn.commit()
            return novo_id
    except errors.RaiseException as e:
        # Captura o erro da trigger 'trg_valida_emprestimo'
        mensagem = e.diag.message_primary if hasattr(e, 'diag') and e.diag else str(e)
        raise ValueError(mensagem)
    except errors.ForeignKeyViolation as e:
        raise ValueError("Aluno ou Livro informado não existe no sistema.")
    except Exception as e:
        raise RuntimeError(f"Erro ao processar empréstimo: {e}")

def devolver_livro(id_emprestimo: int):
    """
    Registra a devolução de um empréstimo, preenchendo a data de devolução e alterando o status.
    """
    query = """
        UPDATE emprestimos
        SET data_devolucao = CURRENT_TIMESTAMP,
            status = 'DEVOLVIDO'
        WHERE id_emprestimo = %s AND data_devolucao IS NULL;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (id_emprestimo,))
            linhas_afetadas = cur.rowcount
        conn.commit()
        if linhas_afetadas == 0:
            raise ValueError("Empréstimo não encontrado ou já foi devolvido anteriormente.")
        return True
