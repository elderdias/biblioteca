import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import services.aluno_service as aluno_service
import services.livro_service as livro_service
import services.emprestimo_service as emprestimo_service
from database import test_connection
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER


class BibliotecaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestão de Biblioteca - PostgreSQL")
        self.geometry("980x680")
        self.minsize(850, 550)

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

        # Criação dos Componentes Principais
        self._criar_cabecalho()
        self._criar_abas()
        self._carregar_dados_iniciais()

    def _criar_cabecalho(self):
        header = tk.Frame(self, bg="#1f2937", height=60)
        header.pack(fill="x", side="top")

        titulo = tk.Label(
            header,
            text="📚 Sistema de Biblioteca",
            font=("Segoe UI", 16, "bold"),
            fg="#ffffff",
            bg="#1f2937"
        )
        titulo.pack(side="left", padx=20, pady=12)

        self.lbl_status_db = tk.Label(
            header,
            text="Verificando conexão...",
            font=("Segoe UI", 9),
            fg="#9ca3af",
            bg="#1f2937"
        )
        self.lbl_status_db.pack(side="right", padx=20, pady=15)

    def _criar_abas(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Abas
        self.tab_livros = ttk.Frame(self.notebook, padding=10)
        self.tab_alunos = ttk.Frame(self.notebook, padding=10)
        self.tab_emprestimos = ttk.Frame(self.notebook, padding=10)
        self.tab_info = ttk.Frame(self.notebook, padding=15)

        self.notebook.add(self.tab_livros, text=" 📖 Livros ")
        self.notebook.add(self.tab_alunos, text=" 🎓 Alunos ")
        self.notebook.add(self.tab_emprestimos, text=" 🔄 Empréstimos ")
        self.notebook.add(self.tab_info, text=" ⚙️ Informações & Banco ")

        self._montar_aba_livros()
        self._montar_aba_alunos()
        self._montar_aba_emprestimos()
        self._montar_aba_info()

    # =========================================================================
    # ABA LIVROS
    # =========================================================================
    def _montar_aba_livros(self):
        # Formulário
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

        # Botões Livro
        botoes = ttk.Frame(form)
        botoes.grid(row=1, column=4, columnspan=2, sticky="e", padx=5, pady=5)

        ttk.Button(botoes, text="Salvar / Cadastrar", style="Primary.TButton", command=self._salvar_livro).pack(side="left", padx=4)
        ttk.Button(botoes, text="Limpar", command=self._limpar_form_livro).pack(side="left", padx=4)
        ttk.Button(botoes, text="Excluir", command=self._excluir_livro).pack(side="left", padx=4)

        # Tabela Livros
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
            messagebox.showwarning("Aviso", "A quantidade de exemplares deve ser um número inteiro maior ou igual a 1.")
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
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir o livro de ID {id_str}?"):
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
        valores = self.grid_livros.item(item[0], "values")
        self._limpar_form_livro()
        self.txt_livro_id.config(state="normal")
        self.txt_livro_id.insert(0, valores[0])
        self.txt_livro_id.config(state="readonly")
        self.txt_livro_titulo.insert(0, valores[1])
        self.txt_livro_autor.insert(0, valores[2])
        self.txt_livro_isbn.insert(0, valores[3] if valores[3] != "None" else "")
        self.txt_livro_qtd.set(valores[4])

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
                self._atualizar_combos_emprestimo()
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

        # Barra de Ações para Empréstimos Existentes
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

        # Tabela Empréstimos
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
            # Exibe mensagem amigável quando a trigger de estoque bloqueia
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
    # ABA INFORMAÇÕES & BANCO DE DADOS
    # =========================================================================
    def _montar_aba_info(self):
        card = ttk.LabelFrame(self.tab_info, text="Conexão com o Banco de Dados", padding=15)
        card.pack(fill="x", pady=10)

        info_text = (
            f"• Host: {DB_HOST}\n"
            f"• Porta: {DB_PORT}\n"
            f"• Banco de Dados: {DB_NAME}\n"
            f"• Usuário: {DB_USER}\n"
            f"• Status de Conexão: Verificado com Sucesso\n"
        )
        ttk.Label(card, text=info_text, font=("Consolas", 10), justify="left").pack(anchor="w", pady=5)

        ttk.Button(card, text="Testar Conexão Novamente", command=self._testar_conexao_manual).pack(anchor="w", pady=5)

        card_ajuda = ttk.LabelFrame(self.tab_info, text="Regras de Negócio e Triggers", padding=15)
        card_ajuda.pack(fill="both", expand=True, pady=10)

        ajuda_text = (
            "1. Tabela 'alunos': Guarda os alunos cadastrados com controle de matrícula única.\n"
            "2. Tabela 'livros': Guarda os livros e a quantidade total de exemplares no acervo.\n"
            "3. Tabela 'emprestimos': Registra os empréstimos e a data prevista de devolução.\n"
            "4. Trigger 'trg_valida_emprestimo': Implementada no PostgreSQL, bloqueia novos empréstimos\n"
            "   caso todos os exemplares daquele livro já estejam emprestados e não devolvidos."
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
            self.lbl_status_db.config(text="● Banco Conectado (biblioteca)", fg="#10b981")
            self._carregar_livros()
            self._carregar_alunos()
            self._carregar_emprestimos()
            self._atualizar_combos_emprestimo()
        else:
            self.lbl_status_db.config(text="● Falha na Conexão", fg="#ef4444")
            messagebox.showwarning("Aviso de Conexão", f"Não foi possível conectar ao PostgreSQL:\n{msg}")


if __name__ == "__main__":
    app = BibliotecaApp()
    app.mainloop()
