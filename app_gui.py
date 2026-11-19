import os
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

import services.aluno_service as aluno_service
import services.livro_service as livro_service
import services.emprestimo_service as emprestimo_service
import services.auth_service as auth_service
import services.relatorio_service as relatorio_service
from database import test_connection
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER


# =============================================================================
# JANELA DE CADASTRO DE NOVO USUÁRIO
# =============================================================================
class JanelaCadastroUsuario(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cadastrar Novo Usuário")
        self.geometry("400x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Centralizar na tela
        largura, altura = 400, 420
        pos_x = (self.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        self.configure(bg="#f8fafc")
        self._criar_widgets()

    def _criar_widgets(self):
        container = tk.Frame(self, bg="#ffffff", padx=25, pady=25, highlightbackground="#e2e8f0", highlightthickness=1)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(container, text="👤 Novo Usuário", font=("Segoe UI", 14, "bold"), fg="#1e293b", bg="#ffffff").pack(anchor="w", pady=(0, 15))

        tk.Label(container, text="Nome Completo:*", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#ffffff").pack(anchor="w")
        self.txt_nome = ttk.Entry(container, width=32, font=("Segoe UI", 10))
        self.txt_nome.pack(fill="x", pady=(2, 10))

        tk.Label(container, text="Login / Usuário:*", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#ffffff").pack(anchor="w")
        self.txt_login = ttk.Entry(container, width=32, font=("Segoe UI", 10))
        self.txt_login.pack(fill="x", pady=(2, 10))

        tk.Label(container, text="Cargo / Função:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#ffffff").pack(anchor="w")
        self.combo_cargo = ttk.Combobox(container, values=["Operador", "Bibliotecário", "Administrador"], state="readonly", font=("Segoe UI", 10))
        self.combo_cargo.set("Bibliotecário")
        self.combo_cargo.pack(fill="x", pady=(2, 10))

        tk.Label(container, text="Senha:* (mínimo 4 caracteres)", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#ffffff").pack(anchor="w")
        self.txt_senha = ttk.Entry(container, show="*", width=32, font=("Segoe UI", 10))
        self.txt_senha.pack(fill="x", pady=(2, 10))

        tk.Label(container, text="Confirmar Senha:*", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#ffffff").pack(anchor="w")
        self.txt_conf_senha = ttk.Entry(container, show="*", width=32, font=("Segoe UI", 10))
        self.txt_conf_senha.pack(fill="x", pady=(2, 15))

        botoes = tk.Frame(container, bg="#ffffff")
        botoes.pack(fill="x", pady=(5, 0))

        btn_cadastrar = tk.Button(
            botoes,
            text="Cadastrar",
            font=("Segoe UI", 10, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self._cadastrar
        )
        btn_cadastrar.pack(side="right", padx=(5, 0))

        btn_cancelar = tk.Button(
            botoes,
            text="Cancelar",
            font=("Segoe UI", 10),
            bg="#e2e8f0",
            fg="#334155",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.destroy
        )
        btn_cancelar.pack(side="right")

    def _cadastrar(self):
        nome = self.txt_nome.get().strip()
        login = self.txt_login.get().strip().lower()
        cargo = self.combo_cargo.get().strip()
        senha = self.txt_senha.get()
        conf_senha = self.txt_conf_senha.get()

        if not nome or not login or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios!", parent=self)
            return

        if senha != conf_senha:
            messagebox.showwarning("Aviso", "A confirmação da senha não confere!", parent=self)
            return

        try:
            auth_service.cadastrar_usuario(nome, login, senha, cargo)
            messagebox.showinfo("Sucesso", f"Usuário '{login}' cadastrado com sucesso! Agora você já pode fazer login.", parent=self)
            self.destroy()
        except ValueError as ve:
            messagebox.showwarning("Aviso", str(ve), parent=self)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {e}", parent=self)


# =============================================================================
# JANELA DE LOGIN
# =============================================================================
class JanelaLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Acesso ao Sistema - Biblioteca")
        self.geometry("420x540")
        self.resizable(False, False)
        self.configure(bg="#0f172a")

        # Centralizar na tela
        largura, altura = 420, 540
        pos_x = (self.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        self._criar_interface()

    def _criar_interface(self):
        # Card Central
        card = tk.Frame(self, bg="#ffffff", padx=30, pady=30, relief="flat")
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # Cabeçalho do Card
        lbl_icone = tk.Label(card, text="📚", font=("Segoe UI Emoji", 34), bg="#ffffff")
        lbl_icone.pack(pady=(0, 2))

        lbl_titulo = tk.Label(card, text="Sistema de Biblioteca", font=("Segoe UI", 16, "bold"), fg="#0f172a", bg="#ffffff")
        lbl_titulo.pack()

        lbl_sub = tk.Label(card, text="Informe suas credenciais para continuar", font=("Segoe UI", 9), fg="#64748b", bg="#ffffff")
        lbl_sub.pack(pady=(2, 20))

        # Mensagem de Erro Dinâmica
        self.lbl_erro = tk.Label(card, text="", font=("Segoe UI", 9, "bold"), fg="#dc2626", bg="#ffffff")
        self.lbl_erro.pack(pady=(0, 5))

        # Campos
        frame_campos = tk.Frame(card, bg="#ffffff")
        frame_campos.pack(fill="x")

        tk.Label(frame_campos, text="Usuário", font=("Segoe UI", 10, "bold"), fg="#334155", bg="#ffffff").pack(anchor="w")
        self.txt_login = tk.Entry(
            frame_campos, 
            font=("Segoe UI", 11), 
            relief="solid", 
            bd=1, 
            highlightthickness=1, 
            highlightcolor="#2563eb", 
            highlightbackground="#cbd5e1"
        )
        self.txt_login.pack(fill="x", ipady=5, pady=(4, 12))
        self.txt_login.focus_set()

        tk.Label(frame_campos, text="Senha", font=("Segoe UI", 10, "bold"), fg="#334155", bg="#ffffff").pack(anchor="w")
        self.txt_senha = tk.Entry(
            frame_campos, 
            font=("Segoe UI", 11), 
            show="•", 
            relief="solid", 
            bd=1, 
            highlightthickness=1, 
            highlightcolor="#2563eb", 
            highlightbackground="#cbd5e1"
        )
        self.txt_senha.pack(fill="x", ipady=5, pady=(4, 6))

        # Opção mostrar senha
        self.var_mostrar = tk.BooleanVar(value=False)
        chk_mostrar = tk.Checkbutton(
            frame_campos,
            text="Mostrar senha",
            variable=self.var_mostrar,
            font=("Segoe UI", 9),
            fg="#64748b",
            bg="#ffffff",
            activebackground="#ffffff",
            command=self._alternar_senha
        )
        chk_mostrar.pack(anchor="w", pady=(0, 15))

        # Botão Entrar
        btn_entrar = tk.Button(
            card,
            text="Entrar no Sistema",
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=8,
            command=self._fazer_login
        )
        btn_entrar.pack(fill="x")

        # Botão Cadastrar Usuário
        btn_novo_usuario = tk.Button(
            card,
            text="Criar Novo Usuário",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#2563eb",
            activebackground="#ffffff",
            activeforeground="#1d4ed8",
            relief="flat",
            cursor="hand2",
            bd=0,
            command=self._abrir_cadastro
        )
        btn_novo_usuario.pack(pady=(10, 0))

        # Dica de acesso padrão
        lbl_dica = tk.Label(
            card,
            text="💡 Padrão inicial: Usuário admin | Senha admin123",
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg="#ffffff"
        )
        lbl_dica.pack(side="bottom", pady=(15, 0))

        # Atalho de teclado Enter para submeter
        self.txt_login.bind("<Return>", lambda e: self._fazer_login())
        self.txt_senha.bind("<Return>", lambda e: self._fazer_login())

    def _alternar_senha(self):
        if self.var_mostrar.get():
            self.txt_senha.config(show="")
        else:
            self.txt_senha.config(show="•")

    def _abrir_cadastro(self):
        JanelaCadastroUsuario(self)

    def _fazer_login(self):
        login = self.txt_login.get().strip()
        senha = self.txt_senha.get()

        if not login or not senha:
            self.lbl_erro.config(text="Por favor, informe o usuário e a senha.")
            return

        self.lbl_erro.config(text="Autenticando...", fg="#2563eb")
        self.update_idletasks()

        user = auth_service.autenticar_usuario(login, senha)
        if user:
            self.destroy()
            app = BibliotecaApp(usuario_logado=user)
            app.mainloop()
        else:
            self.lbl_erro.config(text="Usuário ou senha incorretos!", fg="#dc2626")
            self.txt_senha.delete(0, tk.END)
            self.txt_senha.focus_set()


# =============================================================================
# JANELA PRINCIPAL DA APLICAÇÃO
# =============================================================================
class BibliotecaApp(tk.Tk):
    def __init__(self, usuario_logado: dict = None):
        super().__init__()
        self.usuario_logado = usuario_logado or {"nome": "Administrador", "login": "admin", "cargo": "Administrador"}
        
        self.title("Sistema de Gestão de Biblioteca - PostgreSQL")
        self.geometry("1020x700")
        self.minsize(880, 580)

        # Configurar Estilos ttk
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Paleta de Cores e Estilo
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e1e4e8")
        self.style.configure("Treeview", rowheight=26)
        self.style.configure("TButton", padding=5)
        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background="#0366d6", foreground="#ffffff")
        self.style.map("Primary.TButton", background=[("active", "#0056b3")])

        # Componentes Principais
        self._criar_cabecalho()
        self._criar_abas()
        self._carregar_dados_iniciais()

    def _criar_cabecalho(self):
        header = tk.Frame(self, bg="#1f2937", height=65)
        header.pack(fill="x", side="top")

        frame_esquerda = tk.Frame(header, bg="#1f2937")
        frame_esquerda.pack(side="left", padx=20, pady=12)

        titulo = tk.Label(
            frame_esquerda,
            text="📚 Sistema de Biblioteca",
            font=("Segoe UI", 15, "bold"),
            fg="#ffffff",
            bg="#1f2937"
        )
        titulo.pack(side="left")

        frame_direita = tk.Frame(header, bg="#1f2937")
        frame_direita.pack(side="right", padx=20, pady=12)

        self.lbl_status_db = tk.Label(
            frame_direita,
            text="Verificando banco...",
            font=("Segoe UI", 9),
            fg="#9ca3af",
            bg="#1f2937"
        )
        self.lbl_status_db.pack(side="left", padx=(0, 15))

        nome_user = self.usuario_logado.get("nome", "Usuário")
        cargo_user = self.usuario_logado.get("cargo", "Operador")
        lbl_usuario = tk.Label(
            frame_direita,
            text=f"👤 {nome_user} ({cargo_user})",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#1f2937"
        )
        lbl_usuario.pack(side="left", padx=(0, 12))

        btn_logout = tk.Button(
            frame_direita,
            text="Sair ⮞",
            font=("Segoe UI", 8, "bold"),
            bg="#374151",
            fg="#f3f4f6",
            activebackground="#ef4444",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=3,
            command=self._logout
        )
        btn_logout.pack(side="left")

    def _logout(self):
        if messagebox.askyesno("Logout", "Deseja realmente encerrar a sessão e voltar para a tela de login?"):
            self.destroy()
            janela_login = JanelaLogin()
            janela_login.mainloop()

    def _criar_abas(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_livros = ttk.Frame(self.notebook, padding=10)
        self.tab_alunos = ttk.Frame(self.notebook, padding=10)
        self.tab_emprestimos = ttk.Frame(self.notebook, padding=10)
        self.tab_relatorios = ttk.Frame(self.notebook, padding=10)
        self.tab_info = ttk.Frame(self.notebook, padding=15)

        self.notebook.add(self.tab_livros, text=" 📖 Livros ")
        self.notebook.add(self.tab_alunos, text=" 🎓 Alunos ")
        self.notebook.add(self.tab_emprestimos, text=" 🔄 Empréstimos ")
        self.notebook.add(self.tab_relatorios, text=" 📊 Relatórios ")
        self.notebook.add(self.tab_info, text=" ⚙️ Usuários & Banco ")

        self._montar_aba_livros()
        self._montar_aba_alunos()
        self._montar_aba_emprestimos()
        self._montar_aba_relatorios()
        self._montar_aba_info()

    # =========================================================================
    # ABA LIVROS
    # =========================================================================
    def _montar_aba_livros(self):
        form = ttk.LabelFrame(self.tab_livros, text="Dados do Livro", padding=10)
        form.pack(fill="x", side="top", pady=5)

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.txt_livro_id = ttk.Entry(form, width=8, state="readonly")
        self.txt_livro_id.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form, text="Título:*").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.txt_livro_titulo = ttk.Entry(form, width=32)
        self.txt_livro_titulo.grid(row=0, column=3, sticky="we", padx=5, pady=5)

        ttk.Label(form, text="Autor:*").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.txt_livro_autor = ttk.Entry(form, width=25)
        self.txt_livro_autor.grid(row=0, column=5, sticky="we", padx=5, pady=5)

        ttk.Label(form, text="ISBN:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.txt_livro_isbn = ttk.Entry(form, width=20)
        self.txt_livro_isbn.grid(row=1, column=1, columnspan=2, sticky="we", padx=5, pady=5)

        ttk.Label(form, text="Exemplares:").grid(row=1, column=3, sticky="w", padx=5, pady=5)
        self.txt_livro_qtd = ttk.Spinbox(form, from_=1, to=999, width=8)
        self.txt_livro_qtd.set(1)
        self.txt_livro_qtd.grid(row=1, column=3, sticky="e", padx=5, pady=5)

        botoes = ttk.Frame(form)
        botoes.grid(row=1, column=4, columnspan=2, sticky="e", padx=5, pady=5)

        ttk.Button(botoes, text="Salvar / Cadastrar", style="Primary.TButton", command=self._salvar_livro).pack(side="left", padx=4)
        ttk.Button(botoes, text="Limpar", command=self._limpar_form_livro).pack(side="left", padx=4)
        ttk.Button(botoes, text="Excluir", command=self._excluir_livro).pack(side="left", padx=4)

        tabela_frame = ttk.Frame(self.tab_livros)
        tabela_frame.pack(fill="both", expand=True, pady=10)

        colunas = ("id", "titulo", "autor", "isbn", "total", "emprestados", "disponiveis")
        self.grid_livros = ttk.Treeview(tabela_frame, columns=colunas, show="headings", selectmode="browse")
        
        self.grid_livros.heading("id", text="ID")
        self.grid_livros.heading("titulo", text="Título")
        self.grid_livros.heading("autor", text="Autor")
        self.grid_livros.heading("isbn", text="ISBN")
        self.grid_livros.heading("total", text="Qtd Total")
        self.grid_livros.heading("emprestados", text="Emprestados")
        self.grid_livros.heading("disponiveis", text="Disponíveis")

        self.grid_livros.column("id", width=50, anchor="center")
        self.grid_livros.column("titulo", width=250)
        self.grid_livros.column("autor", width=180)
        self.grid_livros.column("isbn", width=130, anchor="center")
        self.grid_livros.column("total", width=80, anchor="center")
        self.grid_livros.column("emprestados", width=90, anchor="center")
        self.grid_livros.column("disponiveis", width=90, anchor="center")

        scroll_y = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.grid_livros.yview)
        self.grid_livros.configure(yscrollcommand=scroll_y.set)
        self.grid_livros.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.grid_livros.bind("<<TreeviewSelect>>", self._ao_selecionar_livro)

    def _salvar_livro(self):
        titulo = self.txt_livro_titulo.get().strip()
        autor = self.txt_livro_autor.get().strip()
        isbn = self.txt_livro_isbn.get().strip()
        id_str = self.txt_livro_id.get().strip()

        if not titulo or not autor:
            messagebox.showwarning("Aviso", "Título e Autor são obrigatórios!")
            return

        try:
            qtd = int(self.txt_livro_qtd.get())
            if qtd < 1:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Aviso", "A quantidade de exemplares deve ser um número maior ou igual a 1.")
            return

        try:
            if id_str:
                livro_service.atualizar_livro(int(id_str), titulo, autor, isbn, qtd)
                messagebox.showinfo("Sucesso", f"Livro '{titulo}' atualizado com sucesso!")
            else:
                livro_service.cadastrar_livro(titulo, autor, isbn, qtd)
                messagebox.showinfo("Sucesso", f"Livro '{titulo}' cadastrado com sucesso!")
            self._limpar_form_livro()
            self._carregar_livros()
            self._atualizar_combos_emprestimo()
        except Exception as e:
            messagebox.showerror("Erro ao salvar", str(e))

    def _excluir_livro(self):
        id_str = self.txt_livro_id.get().strip()
        if not id_str:
            messagebox.showwarning("Aviso", "Selecione um livro na tabela para excluir.")
            return
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir o livro ID {id_str}?"):
            try:
                livro_service.excluir_livro(int(id_str))
                messagebox.showinfo("Sucesso", "Livro excluído com sucesso!")
                self._limpar_form_livro()
                self._carregar_livros()
                self._atualizar_combos_emprestimo()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível excluir o livro: {e}")

    def _limpar_form_livro(self):
        self.txt_livro_id.config(state="normal")
        self.txt_livro_id.delete(0, tk.END)
        self.txt_livro_id.config(state="readonly")
        self.txt_livro_titulo.delete(0, tk.END)
        self.txt_livro_autor.delete(0, tk.END)
        self.txt_livro_isbn.delete(0, tk.END)
        self.txt_livro_qtd.set(1)

    def _ao_selecionar_livro(self, event):
        item = self.grid_livros.selection()
        if not item:
            return
        v = self.grid_livros.item(item[0], "values")
        self._limpar_form_livro()
        self.txt_livro_id.config(state="normal")
        self.txt_livro_id.insert(0, v[0])
        self.txt_livro_id.config(state="readonly")
        self.txt_livro_titulo.insert(0, v[1])
        self.txt_livro_autor.insert(0, v[2])
        self.txt_livro_isbn.insert(0, v[3] if v[3] != "-" else "")
        self.txt_livro_qtd.set(v[4])

    def _carregar_livros(self):
        for row in self.grid_livros.get_children():
            self.grid_livros.delete(row)
        try:
            livros = livro_service.listar_livros()
            for l in livros:
                self.grid_livros.insert("", "end", values=(
                    l["id_livro"],
                    l["titulo"],
                    l["autor"],
                    l["isbn"] or "-",
                    l["quantidade_total"],
                    l["emprestados"],
                    l["disponiveis"]
                ))
        except Exception as e:
            print("Erro ao carregar livros:", e)

    # =========================================================================
    # ABA ALUNOS
    # =========================================================================
    def _montar_aba_alunos(self):
        form = ttk.LabelFrame(self.tab_alunos, text="Dados do Aluno", padding=10)
        form.pack(fill="x", side="top", pady=5)

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.txt_aluno_id = ttk.Entry(form, width=8, state="readonly")
        self.txt_aluno_id.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form, text="Nome:*").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.txt_aluno_nome = ttk.Entry(form, width=30)
        self.txt_aluno_nome.grid(row=0, column=3, sticky="we", padx=5, pady=5)

        ttk.Label(form, text="Matrícula:*").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.txt_aluno_matr = ttk.Entry(form, width=18)
        self.txt_aluno_matr.grid(row=0, column=5, sticky="we", padx=5, pady=5)

        ttk.Label(form, text="E-mail:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.txt_aluno_email = ttk.Entry(form, width=28)
        self.txt_aluno_email.grid(row=1, column=1, columnspan=2, sticky="we", padx=5, pady=5)

        ttk.Label(form, text="Telefone:").grid(row=1, column=3, sticky="w", padx=5, pady=5)
        self.txt_aluno_tel = ttk.Entry(form, width=18)
        self.txt_aluno_tel.grid(row=1, column=3, sticky="e", padx=5, pady=5)

        botoes = ttk.Frame(form)
        botoes.grid(row=1, column=4, columnspan=2, sticky="e", padx=5, pady=5)

        ttk.Button(botoes, text="Salvar / Cadastrar", style="Primary.TButton", command=self._salvar_aluno).pack(side="left", padx=4)
        ttk.Button(botoes, text="Limpar", command=self._limpar_form_aluno).pack(side="left", padx=4)
        ttk.Button(botoes, text="Excluir", command=self._excluir_aluno).pack(side="left", padx=4)

        tabela_frame = ttk.Frame(self.tab_alunos)
        tabela_frame.pack(fill="both", expand=True, pady=10)

        colunas = ("id", "nome", "matricula", "email", "telefone", "data_cadastro")
        self.grid_alunos = ttk.Treeview(tabela_frame, columns=colunas, show="headings", selectmode="browse")

        self.grid_alunos.heading("id", text="ID")
        self.grid_alunos.heading("nome", text="Nome Completo")
        self.grid_alunos.heading("matricula", text="Matrícula")
        self.grid_alunos.heading("email", text="E-mail")
        self.grid_alunos.heading("telefone", text="Telefone")
        self.grid_alunos.heading("data_cadastro", text="Data Cadastro")

        self.grid_alunos.column("id", width=50, anchor="center")
        self.grid_alunos.column("nome", width=220)
        self.grid_alunos.column("matricula", width=120, anchor="center")
        self.grid_alunos.column("email", width=200)
        self.grid_alunos.column("telefone", width=120, anchor="center")
        self.grid_alunos.column("data_cadastro", width=140, anchor="center")

        scroll_y = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.grid_alunos.yview)
        self.grid_alunos.configure(yscrollcommand=scroll_y.set)
        self.grid_alunos.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.grid_alunos.bind("<<TreeviewSelect>>", self._ao_selecionar_aluno)

    def _salvar_aluno(self):
        nome = self.txt_aluno_nome.get().strip()
        matr = self.txt_aluno_matr.get().strip()
        email = self.txt_aluno_email.get().strip()
        tel = self.txt_aluno_tel.get().strip()
        id_str = self.txt_aluno_id.get().strip()

        if not nome or not matr:
            messagebox.showwarning("Aviso", "Nome e Matrícula são obrigatórios!")
            return

        try:
            if id_str:
                aluno_service.atualizar_aluno(int(id_str), nome, matr, email, tel)
                messagebox.showinfo("Sucesso", f"Aluno '{nome}' atualizado com sucesso!")
            else:
                aluno_service.cadastrar_aluno(nome, matr, email, tel)
                messagebox.showinfo("Sucesso", f"Aluno '{nome}' cadastrado com sucesso!")
            self._limpar_form_aluno()
            self._carregar_alunos()
            self._atualizar_combos_emprestimo()
        except Exception as e:
            messagebox.showerror("Erro ao salvar", str(e))

    def _excluir_aluno(self):
        id_str = self.txt_aluno_id.get().strip()
        if not id_str:
            messagebox.showwarning("Aviso", "Selecione um aluno na tabela para excluir.")
            return
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir o aluno ID {id_str}?"):
            try:
                aluno_service.excluir_aluno(int(id_str))
                messagebox.showinfo("Sucesso", "Aluno excluído com sucesso!")
                self._limpar_form_aluno()
                self._carregar_alunos()
                self._carregar_emprestimos()
                self._atualizar_combos_emprestimo()
            except ValueError as ve:
                messagebox.showwarning("Exclusão Não Permitida", str(ve))
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível excluir o aluno: {e}")

    def _limpar_form_aluno(self):
        self.txt_aluno_id.config(state="normal")
        self.txt_aluno_id.delete(0, tk.END)
        self.txt_aluno_id.config(state="readonly")
        self.txt_aluno_nome.delete(0, tk.END)
        self.txt_aluno_matr.delete(0, tk.END)
        self.txt_aluno_email.delete(0, tk.END)
        self.txt_aluno_tel.delete(0, tk.END)

    def _ao_selecionar_aluno(self, event):
        item = self.grid_alunos.selection()
        if not item:
            return
        v = self.grid_alunos.item(item[0], "values")
        self._limpar_form_aluno()
        self.txt_aluno_id.config(state="normal")
        self.txt_aluno_id.insert(0, v[0])
        self.txt_aluno_id.config(state="readonly")
        self.txt_aluno_nome.insert(0, v[1])
        self.txt_aluno_matr.insert(0, v[2])
        self.txt_aluno_email.insert(0, v[3] if v[3] != "-" else "")
        self.txt_aluno_tel.insert(0, v[4] if v[4] != "-" else "")

    def _carregar_alunos(self):
        for row in self.grid_alunos.get_children():
            self.grid_alunos.delete(row)
        try:
            alunos = aluno_service.listar_alunos()
            for a in alunos:
                dt = a["data_cadastro"].strftime("%d/%m/%Y %H:%M") if a.get("data_cadastro") else "-"
                self.grid_alunos.insert("", "end", values=(
                    a["id_aluno"],
                    a["nome"],
                    a["matricula"],
                    a["email"] or "-",
                    a["telefone"] or "-",
                    dt
                ))
        except Exception as e:
            print("Erro ao carregar alunos:", e)

    # =========================================================================
    # ABA EMPRÉSTIMOS
    # =========================================================================
    def _montar_aba_emprestimos(self):
        form = ttk.LabelFrame(self.tab_emprestimos, text="Novo Empréstimo", padding=10)
        form.pack(fill="x", side="top", pady=5)

        ttk.Label(form, text="Aluno:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_emprestimo_aluno = ttk.Combobox(form, state="readonly", width=35)
        self.combo_emprestimo_aluno.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form, text="Livro:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.combo_emprestimo_livro = ttk.Combobox(form, state="readonly", width=40)
        self.combo_emprestimo_livro.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        ttk.Label(form, text="Prazo (dias):").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.txt_emprestimo_dias = ttk.Spinbox(form, from_=1, to=60, width=5)
        self.txt_emprestimo_dias.set(7)
        self.txt_emprestimo_dias.grid(row=0, column=5, sticky="w", padx=5, pady=5)

        ttk.Button(
            form, 
            text="Confirmar Empréstimo", 
            style="Primary.TButton", 
            command=self._realizar_emprestimo
        ).grid(row=0, column=6, sticky="e", padx=10, pady=5)

        barra_filtro = ttk.Frame(self.tab_emprestimos)
        barra_filtro.pack(fill="x", pady=6)

        self.var_apenas_ativos = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(
            barra_filtro, 
            text="Mostrar apenas empréstimos ativos (não devolvidos)", 
            variable=self.var_apenas_ativos, 
            command=self._carregar_emprestimos
        )
        chk.pack(side="left", padx=5)

        ttk.Button(
            barra_filtro, 
            text="✓ Registrar Devolução do Selecionado", 
            command=self._registrar_devolucao
        ).pack(side="right", padx=5)

        tabela_frame = ttk.Frame(self.tab_emprestimos)
        tabela_frame.pack(fill="both", expand=True, pady=5)

        colunas = ("id", "aluno", "matricula", "livro", "dt_emprestimo", "dt_previsao", "dt_devolucao", "status")
        self.grid_emprestimos = ttk.Treeview(tabela_frame, columns=colunas, show="headings", selectmode="browse")

        self.grid_emprestimos.heading("id", text="ID")
        self.grid_emprestimos.heading("aluno", text="Aluno")
        self.grid_emprestimos.heading("matricula", text="Matrícula")
        self.grid_emprestimos.heading("livro", text="Livro")
        self.grid_emprestimos.heading("dt_emprestimo", text="Empréstimo")
        self.grid_emprestimos.heading("dt_previsao", text="Prev. Devolução")
        self.grid_emprestimos.heading("dt_devolucao", text="Data Devolução")
        self.grid_emprestimos.heading("status", text="Status")

        self.grid_emprestimos.column("id", width=45, anchor="center")
        self.grid_emprestimos.column("aluno", width=160)
        self.grid_emprestimos.column("matricula", width=100, anchor="center")
        self.grid_emprestimos.column("livro", width=220)
        self.grid_emprestimos.column("dt_emprestimo", width=110, anchor="center")
        self.grid_emprestimos.column("dt_previsao", width=110, anchor="center")
        self.grid_emprestimos.column("dt_devolucao", width=110, anchor="center")
        self.grid_emprestimos.column("status", width=95, anchor="center")

        scroll_y = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.grid_emprestimos.yview)
        self.grid_emprestimos.configure(yscrollcommand=scroll_y.set)
        self.grid_emprestimos.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def _atualizar_combos_emprestimo(self):
        try:
            alunos = aluno_service.listar_alunos()
            self._map_alunos = {f"{a['nome']} ({a['matricula']})": a["id_aluno"] for a in alunos}
            self.combo_emprestimo_aluno["values"] = list(self._map_alunos.keys())
            if self._map_alunos:
                self.combo_emprestimo_aluno.current(0)

            livros = livro_service.listar_livros()
            self._map_livros = {
                f"{l['titulo']} [Disp: {l['disponiveis']}/{l['quantidade_total']}]": l["id_livro"]
                for l in livros
            }
            self.combo_emprestimo_livro["values"] = list(self._map_livros.keys())
            if self._map_livros:
                self.combo_emprestimo_livro.current(0)

            if hasattr(self, "combo_rel_aluno"):
                self._atualizar_combos_relatorio()
                self._gerar_relatorio()
        except Exception as e:
            print("Erro ao atualizar combos:", e)

    def _realizar_emprestimo(self):
        aluno_sel = self.combo_emprestimo_aluno.get()
        livro_sel = self.combo_emprestimo_livro.get()

        if not aluno_sel or not livro_sel:
            messagebox.showwarning("Aviso", "Selecione o aluno e o livro.")
            return

        id_aluno = self._map_alunos.get(aluno_sel)
        id_livro = self._map_livros.get(livro_sel)

        try:
            dias = int(self.txt_emprestimo_dias.get())
            if dias < 1:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Aviso", "Prazo de dias inválido!")
            return

        try:
            novo_id = emprestimo_service.realizar_emprestimo(id_aluno, id_livro, dias)
            messagebox.showinfo("Sucesso", f"Empréstimo nº {novo_id} registrado com sucesso!")
            self._carregar_emprestimos()
            self._carregar_livros()
            self._atualizar_combos_emprestimo()
        except ValueError as ve:
            messagebox.showwarning("Operação Bloqueada pelo Banco", str(ve))
        except Exception as e:
            messagebox.showerror("Erro ao realizar empréstimo", str(e))

    def _registrar_devolucao(self):
        item = self.grid_emprestimos.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um empréstimo na tabela para registrar a devolução.")
            return
        v = self.grid_emprestimos.item(item[0], "values")
        id_emprestimo = int(v[0])
        status = v[7]

        if status == "DEVOLVIDO":
            messagebox.showinfo("Informação", "Este empréstimo já consta como DEVOLVIDO.")
            return

        if messagebox.askyesno("Confirmar Devolução", f"Confirmar a devolução do livro referente ao empréstimo nº {id_emprestimo}?"):
            try:
                emprestimo_service.devolver_livro(id_emprestimo)
                messagebox.showinfo("Sucesso", "Devolução registrada com sucesso!")
                self._carregar_emprestimos()
                self._carregar_livros()
                self._atualizar_combos_emprestimo()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def _carregar_emprestimos(self):
        for row in self.grid_emprestimos.get_children():
            self.grid_emprestimos.delete(row)
        try:
            apenas_ativos = self.var_apenas_ativos.get()
            lista = emprestimo_service.listar_emprestimos(apenas_ativos=apenas_ativos)
            for e in lista:
                dt_emp = e["data_emprestimo"].strftime("%d/%m/%Y %H:%M") if e.get("data_emprestimo") else "-"
                dt_prev = e["data_previsao_devolucao"].strftime("%d/%m/%Y") if e.get("data_previsao_devolucao") else "-"
                dt_dev = e["data_devolucao"].strftime("%d/%m/%Y %H:%M") if e.get("data_devolucao") else "-"
                
                self.grid_emprestimos.insert("", "end", values=(
                    e["id_emprestimo"],
                    e["nome_aluno"],
                    e["matricula_aluno"],
                    e["titulo_livro"],
                    dt_emp,
                    dt_prev,
                    dt_dev,
                    e["status"]
                ))
        except Exception as e:
            print("Erro ao carregar empréstimos:", e)

    # =========================================================================
    # ABA RELATÓRIOS DE EMPRÉSTIMOS COM FILTROS
    # =========================================================================
    def _montar_aba_relatorios(self):
        self._dados_relatorio_atual = []

        # Card de Filtros
        form = ttk.LabelFrame(self.tab_relatorios, text="Filtros do Relatório de Empréstimos", padding=10)
        form.pack(fill="x", side="top", pady=5)

        # Linha 1 de Filtros
        ttk.Label(form, text="Filtrar por Aluno:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.combo_rel_aluno = ttk.Combobox(form, state="readonly", width=32)
        self.combo_rel_aluno.grid(row=0, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(form, text="Filtrar por Livro:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.combo_rel_livro = ttk.Combobox(form, state="readonly", width=35)
        self.combo_rel_livro.grid(row=0, column=3, sticky="w", padx=5, pady=4)

        ttk.Label(form, text="Status:").grid(row=0, column=4, sticky="w", padx=5, pady=4)
        self.combo_rel_status = ttk.Combobox(
            form, 
            state="readonly", 
            width=16, 
            values=["[Todos os Status]", "EMPRESTADO", "DEVOLVIDO"]
        )
        self.combo_rel_status.set("[Todos os Status]")
        self.combo_rel_status.grid(row=0, column=5, sticky="w", padx=5, pady=4)

        # Linha 2 de Filtros (Datas e Ações de busca)
        ttk.Label(form, text="Data Inicial:").grid(row=1, column=0, sticky="w", padx=5, pady=6)
        frame_dt_ini = ttk.Frame(form)
        frame_dt_ini.grid(row=1, column=1, sticky="w", padx=5, pady=6)
        self.txt_rel_data_ini = ttk.Entry(frame_dt_ini, width=12)
        self.txt_rel_data_ini.pack(side="left")
        ttk.Label(frame_dt_ini, text=" (DD/MM/AAAA)", font=("Segoe UI", 8), foreground="#64748b").pack(side="left", padx=2)

        ttk.Label(form, text="Data Final:").grid(row=1, column=2, sticky="w", padx=5, pady=6)
        frame_dt_fim = ttk.Frame(form)
        frame_dt_fim.grid(row=1, column=3, sticky="w", padx=5, pady=6)
        self.txt_rel_data_fim = ttk.Entry(frame_dt_fim, width=12)
        self.txt_rel_data_fim.pack(side="left")
        ttk.Label(frame_dt_fim, text=" (DD/MM/AAAA)", font=("Segoe UI", 8), foreground="#64748b").pack(side="left", padx=2)

        # Botões de busca
        botoes_busca = ttk.Frame(form)
        botoes_busca.grid(row=1, column=4, columnspan=2, sticky="e", padx=5, pady=6)

        ttk.Button(
            botoes_busca, 
            text="🔍 Filtrar Relatório", 
            style="Primary.TButton", 
            command=self._gerar_relatorio
        ).pack(side="left", padx=4)

        ttk.Button(
            botoes_busca, 
            text="Limpar Filtros", 
            command=self._limpar_filtros_relatorio
        ).pack(side="left", padx=4)

        # Barra de Ações (Exportações e Resumo)
        barra_export = ttk.Frame(self.tab_relatorios)
        barra_export.pack(fill="x", pady=6)

        self.lbl_rel_resumo = tk.Label(
            barra_export,
            text="Carregando dados...",
            font=("Segoe UI", 9, "bold"),
            fg="#1e293b"
        )
        self.lbl_rel_resumo.pack(side="left", padx=5)

        btn_html = tk.Button(
            barra_export,
            text="🌐 Visualizar Relatório em HTML",
            font=("Segoe UI", 9, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self._exportar_relatorio_html
        )
        btn_html.pack(side="right", padx=4)

        btn_csv = tk.Button(
            barra_export,
            text="📥 Exportar para CSV (Excel)",
            font=("Segoe UI", 9, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self._exportar_relatorio_csv
        )
        btn_csv.pack(side="right", padx=4)

        # Tabela do Relatório
        tabela_frame = ttk.Frame(self.tab_relatorios)
        tabela_frame.pack(fill="both", expand=True, pady=5)

        colunas = ("id", "aluno", "matricula", "livro", "dt_emp", "dt_prev", "dt_dev", "status", "situacao")
        self.grid_relatorios = ttk.Treeview(tabela_frame, columns=colunas, show="headings", selectmode="browse")

        self.grid_relatorios.heading("id", text="ID")
        self.grid_relatorios.heading("aluno", text="Aluno")
        self.grid_relatorios.heading("matricula", text="Matrícula")
        self.grid_relatorios.heading("livro", text="Livro")
        self.grid_relatorios.heading("dt_emp", text="Empréstimo")
        self.grid_relatorios.heading("dt_prev", text="Prev. Devolução")
        self.grid_relatorios.heading("dt_dev", text="Data Devolução")
        self.grid_relatorios.heading("status", text="Status")
        self.grid_relatorios.heading("situacao", text="Situação / Atraso")

        self.grid_relatorios.column("id", width=45, anchor="center")
        self.grid_relatorios.column("aluno", width=160)
        self.grid_relatorios.column("matricula", width=95, anchor="center")
        self.grid_relatorios.column("livro", width=210)
        self.grid_relatorios.column("dt_emp", width=110, anchor="center")
        self.grid_relatorios.column("dt_prev", width=105, anchor="center")
        self.grid_relatorios.column("dt_dev", width=110, anchor="center")
        self.grid_relatorios.column("status", width=90, anchor="center")
        self.grid_relatorios.column("situacao", width=130, anchor="center")

        # Tags visuais de destaque
        self.grid_relatorios.tag_configure("atrasado", foreground="#b91c1c")
        self.grid_relatorios.tag_configure("emprestado", foreground="#d97706")
        self.grid_relatorios.tag_configure("devolvido", foreground="#15803d")

        scroll_y = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.grid_relatorios.yview)
        self.grid_relatorios.configure(yscrollcommand=scroll_y.set)
        self.grid_relatorios.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def _atualizar_combos_relatorio(self):
        try:
            alunos = aluno_service.listar_alunos()
            self._map_rel_alunos = {"[Todos os Alunos]": None}
            for a in alunos:
                self._map_rel_alunos[f"{a['nome']} ({a['matricula']})"] = a["id_aluno"]
            self.combo_rel_aluno["values"] = list(self._map_rel_alunos.keys())
            if not self.combo_rel_aluno.get() or self.combo_rel_aluno.get() not in self._map_rel_alunos:
                self.combo_rel_aluno.current(0)

            livros = livro_service.listar_livros()
            self._map_rel_livros = {"[Todos os Livros]": None}
            for l in livros:
                self._map_rel_livros[l["titulo"]] = l["id_livro"]
            self.combo_rel_livro["values"] = list(self._map_rel_livros.keys())
            if not self.combo_rel_livro.get() or self.combo_rel_livro.get() not in self._map_rel_livros:
                self.combo_rel_livro.current(0)
        except Exception as e:
            print("Erro ao atualizar combos de relatório:", e)

    def _gerar_relatorio(self):
        for row in self.grid_relatorios.get_children():
            self.grid_relatorios.delete(row)

        aluno_sel = self.combo_rel_aluno.get()
        livro_sel = self.combo_rel_livro.get()
        status_sel = self.combo_rel_status.get()
        data_ini_str = self.txt_rel_data_ini.get().strip()
        data_fim_str = self.txt_rel_data_fim.get().strip()

        id_aluno = getattr(self, "_map_rel_alunos", {}).get(aluno_sel)
        id_livro = getattr(self, "_map_rel_livros", {}).get(livro_sel)

        status_param = None
        if status_sel in ("EMPRESTADO", "DEVOLVIDO"):
            status_param = status_sel

        try:
            dados = relatorio_service.gerar_relatorio_emprestimos(
                id_aluno=id_aluno,
                id_livro=id_livro,
                data_inicio=data_ini_str if data_ini_str else None,
                data_fim=data_fim_str if data_fim_str else None,
                status=status_param
            )
            self._dados_relatorio_atual = dados

            total = len(dados)
            ativos = sum(1 for r in dados if r["status"] == "EMPRESTADO")
            devolvidos = sum(1 for r in dados if r["status"] == "DEVOLVIDO")
            atrasados = sum(1 for r in dados if r.get("atrasado"))

            self.lbl_rel_resumo.config(
                text=f"Total: {total} | Emprestados: {ativos} | Devolvidos: {devolvidos} | Em Atraso: {atrasados}"
            )

            for r in dados:
                dt_emp = r["data_emprestimo"].strftime("%d/%m/%Y %H:%M") if r.get("data_emprestimo") else "-"
                dt_prev = r["data_previsao_devolucao"].strftime("%d/%m/%Y") if r.get("data_previsao_devolucao") else "-"
                dt_dev = r["data_devolucao"].strftime("%d/%m/%Y %H:%M") if r.get("data_devolucao") else "-"

                if r.get("atrasado"):
                    tag = "atrasado"
                    situacao = f"⚠️ ATRASADO ({r['dias_atraso']}d)"
                elif r["status"] == "EMPRESTADO":
                    tag = "emprestado"
                    situacao = "No prazo"
                else:
                    tag = "devolvido"
                    situacao = "Devolvido"

                self.grid_relatorios.insert("", "end", values=(
                    r["id_emprestimo"],
                    r["nome_aluno"],
                    r["matricula_aluno"],
                    r["titulo_livro"],
                    dt_emp,
                    dt_prev,
                    dt_dev,
                    r["status"],
                    situacao
                ), tags=(tag,))

        except ValueError as ve:
            messagebox.showwarning("Filtro Inválido", str(ve))
        except Exception as e:
            messagebox.showerror("Erro ao Gerar Relatório", str(e))

    def _limpar_filtros_relatorio(self):
        if hasattr(self, "combo_rel_aluno"):
            self.combo_rel_aluno.current(0)
        if hasattr(self, "combo_rel_livro"):
            self.combo_rel_livro.current(0)
        if hasattr(self, "combo_rel_status"):
            self.combo_rel_status.set("[Todos os Status]")
        self.txt_rel_data_ini.delete(0, tk.END)
        self.txt_rel_data_fim.delete(0, tk.END)
        self._gerar_relatorio()

    def _obter_descricao_filtros(self):
        partes = []
        aluno_sel = self.combo_rel_aluno.get()
        if aluno_sel and aluno_sel != "[Todos os Alunos]":
            partes.append(f"Aluno: {aluno_sel}")
        livro_sel = self.combo_rel_livro.get()
        if livro_sel and livro_sel != "[Todos os Livros]":
            partes.append(f"Livro: {livro_sel}")
        status_sel = self.combo_rel_status.get()
        if status_sel and status_sel != "[Todos os Status]":
            partes.append(f"Status: {status_sel}")
        d_ini = self.txt_rel_data_ini.get().strip()
        d_fim = self.txt_rel_data_fim.get().strip()
        if d_ini or d_fim:
            partes.append(f"Período: {d_ini or 'início'} até {d_fim or 'atual'}")
        return " | ".join(partes) if partes else "Todos os registros (Sem filtros)"

    def _exportar_relatorio_csv(self):
        if not getattr(self, "_dados_relatorio_atual", None):
            messagebox.showwarning("Aviso", "Não há dados no relatório atual para exportar!")
            return

        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar Relatório em CSV",
            defaultextension=".csv",
            filetypes=[("Arquivo CSV (Excel)", "*.csv"), ("Todos os arquivos", "*.*")],
            initialfile=f"relatorio_emprestimos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not caminho:
            return

        try:
            relatorio_service.exportar_relatorio_csv(self._dados_relatorio_atual, caminho)
            messagebox.showinfo("Sucesso", f"Relatório exportado com sucesso para:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro ao Exportar", str(e))

    def _exportar_relatorio_html(self):
        if not getattr(self, "_dados_relatorio_atual", None):
            messagebox.showwarning("Aviso", "Não há dados no relatório atual para exportar!")
            return

        pasta_temp = os.getenv("TEMP", ".")
        caminho_html = os.path.join(pasta_temp, f"relatorio_emprestimos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

        try:
            desc_filtros = self._obter_descricao_filtros()
            relatorio_service.exportar_relatorio_html(self._dados_relatorio_atual, caminho_html, desc_filtros)
            webbrowser.open(f"file:///{os.path.abspath(caminho_html).replace(os.sep, '/')}")
        except Exception as e:
            messagebox.showerror("Erro ao abrir relatório", str(e))

    # =========================================================================
    # ABA INFORMAÇÕES, USUÁRIOS & BANCO DE DADOS
    # =========================================================================
    def _montar_aba_info(self):
        card_usuario = ttk.LabelFrame(self.tab_info, text="Operador Atual", padding=12)
        card_usuario.pack(fill="x", pady=5)

        nome = self.usuario_logado.get("nome", "Admin")
        login = self.usuario_logado.get("login", "admin")
        cargo = self.usuario_logado.get("cargo", "Administrador")

        txt_user = f"• Nome: {nome}   |   Login: {login}   |   Cargo: {cargo}"
        ttk.Label(card_usuario, text=txt_user, font=("Segoe UI", 10, "bold"), foreground="#0284c7").pack(anchor="w")

        frame_btn_user = ttk.Frame(card_usuario)
        frame_btn_user.pack(fill="x", pady=(8, 0))
        ttk.Button(frame_btn_user, text="➕ Cadastrar Outro Usuário", command=lambda: JanelaCadastroUsuario(self)).pack(side="left")

        card_db = ttk.LabelFrame(self.tab_info, text="Conexão com o Banco de Dados", padding=12)
        card_db.pack(fill="x", pady=8)

        info_text = (
            f"• Host: {DB_HOST}   |   Porta: {DB_PORT}   |   Banco: {DB_NAME}\n"
            f"• Usuário PostgreSQL: {DB_USER}\n"
        )
        ttk.Label(card_db, text=info_text, font=("Consolas", 10), justify="left").pack(anchor="w", pady=2)
        ttk.Button(card_db, text="Testar Conexão Novamente", command=self._testar_conexao_manual).pack(anchor="w", pady=4)

        card_ajuda = ttk.LabelFrame(self.tab_info, text="Regras de Negócio e Segurança", padding=12)
        card_ajuda.pack(fill="both", expand=True, pady=5)

        ajuda_text = (
            "1. Autenticação: Todas as senhas são armazenadas com hash criptográfico SHA-256 e salt.\n"
            "2. Livros & Acervo: A trigger 'trg_valida_emprestimo' valida se existem cópias disponíveis.\n"
            "3. Alunos & Empréstimos: A trigger 'trg_valida_exclusao_aluno' impede a exclusão de aluno com\n"
            "   empréstimos em aberto, e permite a exclusão caso tudo já tenha sido devolvido."
        )
        ttk.Label(card_ajuda, text=ajuda_text, font=("Segoe UI", 10), justify="left").pack(anchor="w", pady=5)

    def _testar_conexao_manual(self):
        ok, msg = test_connection()
        if ok:
            messagebox.showinfo("Teste de Conexão", msg)
            self.lbl_status_db.config(text="● Banco Conectado", fg="#10b981")
        else:
            messagebox.showerror("Erro de Conexão", msg)
            self.lbl_status_db.config(text="● Desconectado", fg="#ef4444")

    # =========================================================================
    # INICIALIZAÇÃO
    # =========================================================================
    def _carregar_dados_iniciais(self):
        ok, msg = test_connection()
        if ok:
            self.lbl_status_db.config(text="● Conectado (biblioteca)", fg="#10b981")
            self._carregar_livros()
            self._carregar_alunos()
            self._carregar_emprestimos()
            self._atualizar_combos_emprestimo()
            self._atualizar_combos_relatorio()
            self._gerar_relatorio()
        else:
            self.lbl_status_db.config(text="● Falha na Conexão", fg="#ef4444")
            messagebox.showwarning("Aviso de Conexão", f"Não foi possível conectar ao PostgreSQL:\n{msg}")


def main():
    login_app = JanelaLogin()
    login_app.mainloop()


if __name__ == "__main__":
    main()
