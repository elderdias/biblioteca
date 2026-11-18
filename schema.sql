-- ============================================================
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS BIBLIOTECA
-- PostgreSQL 18
-- ============================================================

-- 1. TABELA DE ALUNOS
CREATE TABLE IF NOT EXISTS alunos (
    id_aluno SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    matricula VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100),
    telefone VARCHAR(20),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABELA DE LIVROS
CREATE TABLE IF NOT EXISTS livros (
    id_livro SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    quantidade_total INT NOT NULL DEFAULT 1,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABELA DE EMPRÉSTIMOS
CREATE TABLE IF NOT EXISTS emprestimos (
    id_emprestimo SERIAL PRIMARY KEY,
    id_aluno INT NOT NULL REFERENCES alunos(id_aluno),
    id_livro INT NOT NULL REFERENCES livros(id_livro),
    data_emprestimo TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_previsao_devolucao DATE NOT NULL,
    data_devolucao TIMESTAMP NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'EMPRESTADO'
);

-- 4. TRIGGER PARA BLOQUEAR EMPRÉSTIMO SE NÃO HOUVER UNIDADES DISPONÍVEIS
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

-- 5. TRIGGER PARA BLOQUEAR EXCLUSÃO DE ALUNO COM EMPRÉSTIMO ATIVO
-- (Permite exclusão caso todos os empréstimos estejam DEVOLVIDOS)
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

    -- Remove o histórico de empréstimos devolvidos para permitir a exclusão do aluno
    DELETE FROM emprestimos WHERE id_aluno = OLD.id_aluno;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_valida_exclusao_aluno ON alunos;
CREATE TRIGGER trg_valida_exclusao_aluno
BEFORE DELETE ON alunos
FOR EACH ROW
EXECUTE FUNCTION fn_valida_exclusao_aluno();

-- 6. DADOS DE EXEMPLO (OPCIONAL)
INSERT INTO alunos (nome, matricula, email, telefone) VALUES 
('Lucas Pereira', 'MAT-202401', 'lucas@email.com', '11988881111'),
('Mariana Costa', 'MAT-202402', 'mariana@email.com', '11977772222')
ON CONFLICT (matricula) DO NOTHING;

INSERT INTO livros (titulo, autor, isbn, quantidade_total) VALUES 
('Redes de Computadores', 'Andrew Tanenbaum', '978-8576059240', 1),
('Sistemas de Banco de Dados', 'Navathe', '978-8580553796', 3)
ON CONFLICT (isbn) DO NOTHING;
