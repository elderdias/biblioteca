# 📚 Sistema de Gestão de Biblioteca (PostgreSQL + Python)

Sistema completo desenvolvido em Python para cadastro, consulta e controle de fluxo de uma biblioteca integrada a um banco de dados relacional **PostgreSQL** (banco `biblioteca`).

O sistema oferece tanto uma **Interface Gráfica (Desktop - Tkinter)** moderna e intuitiva, quanto um **Terminal Interativo (CLI)** para manipulação dos dados diretamente pelo console do Visual Studio / VS Code.

---

## 🗄️ Estrutura do Banco de Dados

O banco de dados `biblioteca` possui as seguintes tabelas e regras:

0. **`usuarios`**: Controle de acesso ao sistema (login, senha criptografada com salt e SHA-256, cargo e data de cadastro).
1. **`alunos`**: Cadastro de alunos com controle de matrícula única, e-mail e telefone.
2. **`livros`**: Cadastro de obras com controle de quantidade total de exemplares no acervo físico.
3. **`emprestimos`**: Registro do vínculo entre aluno e livro, data de empréstimo, previsão de devolução, data efetiva de entrega e status (`EMPRESTADO` / `DEVOLVIDO`).
4. **Trigger `trg_valida_emprestimo`**: Validação ativa no PostgreSQL que impede o empréstimo de um livro caso todos os seus exemplares já estejam em posse de outros alunos.
5. **Trigger `trg_valida_exclusao_aluno`**: Permite a exclusão de alunos caso todos os seus empréstimos constem como `DEVOLVIDO` (removendo os registros de vínculo devolvidos para liberar a chave estrangeira). Se o aluno ainda tiver qualquer livro em posse (status `EMPRESTADO`), a exclusão é bloqueada.

---

## 🔐 Acesso e Credenciais Iniciais

Ao abrir o sistema pela primeira vez, utilize o usuário administrador padrão:

- **Usuário:** `admin`
- **Senha:** `admin123`

Você pode cadastrar novos usuários e operadores a qualquer momento diretamente pela **Tela de Login** (botão *"Criar Novo Usuário"*) ou pela aba **"⚙️ Usuários & Banco"**.

---

## 📁 Estrutura do Projeto

```text
Redes/
├── .vscode/
│   ├── launch.json              # Configurações de execução (F5) no Visual Studio / VS Code
│   └── settings.json            # Apontamento do interpretador Python
├── services/
│   ├── __init__.py
│   ├── auth_service.py          # Autenticação, hash SHA-256 e gestão de usuários
│   ├── aluno_service.py         # CRUD e buscas de Alunos
│   ├── livro_service.py         # CRUD, buscas e cálculo de estoque de Livros
│   ├── emprestimo_service.py    # Empréstimos, devoluções e regras de negócio
│   └── relatorio_service.py     # Relatórios, filtros dinâmicos e exportações (CSV/HTML)
├── app_gui.py                   # Interface Gráfica Desktop (Login + Abas + Relatórios)
├── main.py                      # Menu interativo no Terminal e inicializador
├── database.py                  # Gerenciador de conexão com PostgreSQL (psycopg)
├── config.py                    # Variáveis de conexão com o banco
├── schema.sql                   # DDL das tabelas, triggers e dados iniciais
├── .gitignore                   # Arquivos ignorados pelo Git
└── README.md                    # Documentação do projeto
```

---

## 📊 Relatórios e Filtros de Empréstimos

O sistema conta com uma aba exclusiva **"📊 Relatórios"** (e opção 4 no menu de terminal), que permite:

- **Filtrar por Aluno:** Visualize os empréstimos de um aluno específico ou de todos.
- **Filtrar por Livro:** Acompanhe a circulação de um livro específico ou de todo o acervo.
- **Filtrar por Período de Datas:** Pesquise por intervalo de datas de empréstimo (`DD/MM/AAAA`).
- **Filtrar por Status:** Visualize apenas empréstimos ativos (`EMPRESTADO`), devoluções (`DEVOLVIDO`) ou todos.
- **Detecção de Atrasos:** Identifica empréstimos ativos que ultrapassaram a data de previsão e exibe a quantidade exata de dias em atraso com destaque visual.
- **Exportação para CSV (Excel):** Exporta os dados filtrados com codificação UTF-8 compatível com Microsoft Excel.
- **Exportação para HTML:** Abre no navegador um relatório visual com cards de indicadores (KPIs) pronto para impressão ou salvamento em PDF.

---

## ⚙️ Configuração da Conexão

Por padrão, o arquivo `config.py` conecta no banco local com as credenciais padrão do seu PostgreSQL:

- **Host:** `localhost`
- **Porta:** `5432`
- **Banco:** `biblioteca`
- **Usuário:** `postgres`
- **Senha:** `123456`

---

## 🚀 Como Executar no Visual Studio / VS Code

### Opção 1: Pela Interface do Visual Studio (Recomendado)
1. Abra a pasta do projeto no **Visual Studio** ou **VS Code**.
2. Pressione **`F5`** (ou acesse a aba lateral de **Executar e Depurar** / *Run and Debug*).
3. Selecione a opção desejada:
   - **`Executar Sistema (Interface Gráfica)`**: Inicia a janela com abas para Livros, Alunos e Empréstimos.
   - **`Executar Sistema (Terminal Interativo)`**: Inicia o menu pelo terminal integrado.

### Opção 2: Pelo Terminal
Abra o terminal integrado (`Ctrl + '`) e execute:

```bash
# Para abrir a Interface Gráfica:
py app_gui.py

# Para executar o menu no Terminal:
py main.py
```

---

## 🐙 Como Criar e Publicar o Repositório no GitHub

O repositório Git local já foi inicializado. Para enviar para o seu GitHub, você pode escolher uma das seguintes alternativas:

### Pelo Visual Studio / VS Code (Mais Fácil):
1. No menu lateral esquerdo do VS Code, clique no ícone do **Controle do Código-Fonte** (`Ctrl + Shift + G`).
2. Clique no botão **"Publicar no GitHub"** (*Publish to GitHub*).
3. O VS Code solicitará a autorização com sua conta do GitHub no navegador e criará o repositório automaticamente (Público ou Privado, conforme sua escolha).

### Pelo Terminal (Usando GitHub CLI `gh`):
1. Faça login na sua conta do GitHub:
   ```bash
   gh auth login
   ```
   *(Siga as instruções rápidas na tela selecionando `GitHub.com` -> `HTTPS` -> `Login with a web browser`)*
2. Crie e envie o repositório com um único comando:
   ```bash
   gh repo create biblioteca-python --public --source=. --push
   ```
