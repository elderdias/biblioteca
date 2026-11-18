from database import get_connection

def listar_livros():
    """
    Retorna todos os livros cadastrados, calculando os exemplares emprestados
    e a quantidade disponível para novos empréstimos.
    """
    query = """
        SELECT 
            l.id_livro, 
            l.titulo, 
            l.autor, 
            l.isbn, 
            l.quantidade_total,
            COUNT(e.id_emprestimo) FILTER (WHERE e.data_devolucao IS NULL) AS emprestados,
            (l.quantidade_total - COUNT(e.id_emprestimo) FILTER (WHERE e.data_devolucao IS NULL)) AS disponiveis,
            l.data_cadastro
        FROM livros l
        LEFT JOIN emprestimos e ON l.id_livro = e.id_livro
        GROUP BY l.id_livro, l.titulo, l.autor, l.isbn, l.quantidade_total
        ORDER BY l.id_livro ASC;
    """
    with get_connection(as_dict=True) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def buscar_livro_por_id(id_livro: int):
    """Busca livro por ID."""
    query = "SELECT * FROM livros WHERE id_livro = %s;"
    with get_connection(as_dict=True) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (id_livro,))
            return cur.fetchone()

def cadastrar_livro(titulo: str, autor: str, isbn: str = None, quantidade_total: int = 1):
    """Cadastra um novo livro."""
    query = """
        INSERT INTO livros (titulo, autor, isbn, quantidade_total)
        VALUES (%s, %s, %s, %s)
        RETURNING id_livro;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (titulo.strip(), autor.strip(), isbn.strip() if isbn else None, int(quantidade_total)))
            novo_id = cur.fetchone()[0]
        conn.commit()
        return novo_id

def atualizar_livro(id_livro: int, titulo: str, autor: str, isbn: str = None, quantidade_total: int = 1):
    """Atualiza as informações de um livro."""
    query = """
        UPDATE livros
        SET titulo = %s, autor = %s, isbn = %s, quantidade_total = %s
        WHERE id_livro = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (titulo.strip(), autor.strip(), isbn.strip() if isbn else None, int(quantidade_total), id_livro))
            linhas_afetadas = cur.rowcount
        conn.commit()
        return linhas_afetadas > 0

def excluir_livro(id_livro: int):
    """Exclui um livro pelo ID."""
    query = "DELETE FROM livros WHERE id_livro = %s;"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (id_livro,))
            linhas_afetadas = cur.rowcount
        conn.commit()
        return linhas_afetadas > 0
