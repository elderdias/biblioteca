import sys
from database import test_connection, init_db
import services.aluno_service as aluno_service
import services.livro_service as livro_service
import services.emprestimo_service as emprestimo_service

def imprimir_cabecalho(texto: str):
    print("\n" + "=" * 60)
    print(f" {texto}".center(60))
    print("=" * 60)

def menu_alunos():
    while True:
        imprimir_cabecalho("GERENCIAR ALUNOS")
        print("1. Listar Alunos")
        print("2. Cadastrar Novo Aluno")
        print("3. Atualizar Aluno")
        print("4. Excluir Aluno")
        print("0. Voltar ao Menu Principal")
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            alunos = aluno_service.listar_alunos()
            print("\n" + "-" * 75)
            print(f"{'ID':<4} | {'Nome':<25} | {'Matrícula':<12} | {'Telefone':<14} | {'E-mail'}")
            print("-" * 75)
            for a in alunos:
                print(f"{a['id_aluno']:<4} | {a['nome']:<25} | {a['matricula']:<12} | {str(a['telefone'] or '-'):<14} | {a['email'] or '-'}")
            print("-" * 75)
            input("\nPressione ENTER para continuar...")

        elif opcao == "2":
            print("\n-- Cadastrar Aluno --")
            nome = input("Nome completo: ").strip()
            matr = input("Matrícula: ").strip()
            email = input("E-mail (opcional): ").strip()
            tel = input("Telefone (opcional): ").strip()

            if not nome or not matr:
                print("❌ Nome e matrícula são obrigatórios.")
            else:
                try:
                    novo_id = aluno_service.cadastrar_aluno(nome, matr, email, tel)
                    print(f"✅ Aluno cadastrado com sucesso! ID: {novo_id}")
                except Exception as e:
                    print(f"❌ Erro ao cadastrar aluno: {e}")
            input("\nPressione ENTER para continuar...")

        elif opcao == "3":
            try:
                id_aluno = int(input("\nID do aluno para atualizar: ").strip())
                aluno = aluno_service.buscar_aluno_por_id(id_aluno)
                if not aluno:
                    print("❌ Aluno não encontrado.")
                else:
                    print(f"Atualizando: {aluno['nome']} ({aluno['matricula']})")
                    nome = input(f"Novo nome [{aluno['nome']}]: ").strip() or aluno['nome']
                    matr = input(f"Nova matrícula [{aluno['matricula']}]: ").strip() or aluno['matricula']
                    email = input(f"Novo e-mail [{aluno['email']}]: ").strip() or aluno['email']
                    tel = input(f"Novo telefone [{aluno['telefone']}]: ").strip() or aluno['telefone']

                    aluno_service.atualizar_aluno(id_aluno, nome, matr, email, tel)
                    print("✅ Aluno atualizado com sucesso!")
            except Exception as e:
                print(f"❌ Erro: {e}")
            input("\nPressione ENTER para continuar...")

        elif opcao == "4":
            try:
                id_aluno = int(input("\nID do aluno para excluir: ").strip())
                confirm = input(f"Tem certeza que deseja excluir o aluno ID {id_aluno}? (s/N): ").strip().lower()
                if confirm == "s":
                    if aluno_service.excluir_aluno(id_aluno):
                        print("✅ Aluno excluído com sucesso!")
                    else:
                        print("❌ Aluno não encontrado.")
            except ValueError as ve:
                print(f"\n⚠️  {ve}")
            except Exception as e:
                print(f"❌ Erro: {e}")
            input("\nPressione ENTER para continuar...")

        elif opcao == "0":
            break


def menu_livros():
    while True:
        imprimir_cabecalho("GERENCIAR LIVROS")
        print("1. Listar Livros do Acervo")
        print("2. Cadastrar Novo Livro")
        print("3. Atualizar Informações de Livro")
        print("4. Excluir Livro")
        print("0. Voltar ao Menu Principal")
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            livros = livro_service.listar_livros()
            print("\n" + "-" * 85)
            print(f"{'ID':<4} | {'Título':<30} | {'Autor':<20} | {'Total':<6} | {'Emp.':<5} | {'Disp.'}")
            print("-" * 85)
            for l in livros:
                print(f"{l['id_livro']:<4} | {l['titulo']:<30} | {l['autor']:<20} | {l['quantidade_total']:<6} | {l['emprestados']:<5} | {l['disponiveis']}")
            print("-" * 85)
            input("\nPressione ENTER para continuar...")

        elif opcao == "2":
            print("\n-- Cadastrar Livro --")
            titulo = input("Título: ").strip()
            autor = input("Autor: ").strip()
            isbn = input("ISBN (opcional): ").strip()
            qtd_str = input("Quantidade de exemplares [1]: ").strip() or "1"

            if not titulo or not autor:
                print("❌ Título e autor são obrigatórios.")
            else:
                try:
                    novo_id = livro_service.cadastrar_livro(titulo, autor, isbn, int(qtd_str))
                    print(f"✅ Livro cadastrado com sucesso! ID: {novo_id}")
                except Exception as e:
                    print(f"❌ Erro ao cadastrar livro: {e}")
            input("\nPressione ENTER para continuar...")

        elif opcao == "3":
            try:
                id_livro = int(input("\nID do livro para atualizar: ").strip())
                livro = livro_service.buscar_livro_por_id(id_livro)
                if not livro:
                    print("❌ Livro não encontrado.")
                else:
                    print(f"Atualizando: {livro['titulo']}")
                    titulo = input(f"Novo título [{livro['titulo']}]: ").strip() or livro['titulo']
                    autor = input(f"Novo autor [{livro['autor']}]: ").strip() or livro['autor']
                    isbn = input(f"Novo ISBN [{livro['isbn']}]: ").strip() or livro['isbn']
                    qtd_str = input(f"Nova quantidade total [{livro['quantidade_total']}]: ").strip() or str(livro['quantidade_total'])

                    livro_service.atualizar_livro(id_livro, titulo, autor, isbn, int(qtd_str))
                    print("✅ Livro atualizado com sucesso!")
            except Exception as e:
                print(f"❌ Erro: {e}")
            input("\nPressione ENTER para continuar...")

        elif opcao == "4":
            try:
                id_livro = int(input("\nID do livro para excluir: ").strip())
                confirm = input(f"Tem certeza que deseja excluir o livro ID {id_livro}? (s/N): ").strip().lower()
                if confirm == "s":
                    if livro_service.excluir_livro(id_livro):
                        print("✅ Livro excluído com sucesso!")
                    else:
                        print("❌ Livro não encontrado.")
            except Exception as e:
                print(f"❌ Erro: {e}")
            input("\nPressione ENTER para continuar...")

        elif opcao == "0":
            break


def menu_emprestimos():
    while True:
        imprimir_cabecalho("EMPRÉSTIMOS E DEVOLUÇÕES")
        print("1. Listar Todos os Empréstimos")
        print("2. Listar Apenas Empréstimos Ativos (Não devolvidos)")
        print("3. Realizar Novo Empréstimo")
        print("4. Registrar Devolução")
        print("0. Voltar ao Menu Principal")
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao in ("1", "2"):
            apenas_ativos = (opcao == "2")
            emprestimos = emprestimo_service.listar_emprestimos(apenas_ativos=apenas_ativos)
            print("\n" + "-" * 95)
            print(f"{'ID':<4} | {'Aluno':<20} | {'Livro':<28} | {'Dt Empréstimo':<13} | {'Prev. Dev.':<10} | {'Status'}")
            print("-" * 95)
            for e in emprestimos:
                dt_emp = e['data_emprestimo'].strftime('%d/%m/%Y') if e.get('data_emprestimo') else '-'
                dt_prev = e['data_previsao_devolucao'].strftime('%d/%m/%Y') if e.get('data_previsao_devolucao') else '-'
                print(f"{e['id_emprestimo']:<4} | {e['nome_aluno'][:20]:<20} | {e['titulo_livro'][:28]:<28} | {dt_emp:<13} | {dt_prev:<10} | {e['status']}")
            print("-" * 95)
            input("\nPressione ENTER para continuar...")

        elif opcao == "3":
            print("\n-- Realizar Empréstimo --")
            try:
                id_aluno = int(input("ID do Aluno: ").strip())
                id_livro = int(input("ID do Livro: ").strip())
                dias_str = input("Prazo em dias [7]: ").strip() or "7"

                novo_id = emprestimo_service.realizar_emprestimo(id_aluno, id_livro, int(dias_str))
                print(f"✅ Empréstimo realizado com sucesso! ID: {novo_id}")
            except ValueError as ve:
                print(f"\n⚠️  {ve}")
            except Exception as e:
                print(f"\n❌ Erro: {e}")
            input("\nPressione ENTER para continuar...")

        elif opcao == "4":
            print("\n-- Registrar Devolução --")
            try:
                id_emp = int(input("ID do Empréstimo: ").strip())
                emprestimo_service.devolver_livro(id_emp)
                print("✅ Devolução registrada com sucesso!")
            except Exception as e:
                print(f"❌ Erro: {e}")
            input("\nPressione ENTER para continuar...")

        elif opcao == "0":
            break


def main():
    if "--gui" in sys.argv:
        from app_gui import BibliotecaApp
        app = BibliotecaApp()
        app.mainloop()
        return

    ok, msg = test_connection()
    if not ok:
        print(f"⚠️ Atenção ao conectar no banco: {msg}")
    else:
        init_db()

    while True:
        imprimir_cabecalho("SISTEMA DE GESTÃO DA BIBLIOTECA")
        print(f"Conexão: {'🟢 Online' if ok else '🔴 Offline'} (PostgreSQL)")
        print("\nEscolha o módulo desejado:")
        print("1. 🎓 Gerenciar Alunos")
        print("2. 📖 Gerenciar Livros")
        print("3. 🔄 Empréstimos e Devoluções")
        print("4. 🖥️  Abrir Interface Gráfica (Desktop)")
        print("5. 🔍 Testar Conexão com o Banco")
        print("0. Sair")

        opcao = input("\nDigite sua opção: ").strip()

        if opcao == "1":
            menu_alunos()
        elif opcao == "2":
            menu_livros()
        elif opcao == "3":
            menu_emprestimos()
        elif opcao == "4":
            print("\nAbrindo interface gráfica...")
            try:
                from app_gui import BibliotecaApp
                app = BibliotecaApp()
                app.mainloop()
            except Exception as e:
                print(f"Erro ao abrir interface gráfica: {e}")
        elif opcao == "5":
            sucesso, texto = test_connection()
            status = "✅ Sucesso" if sucesso else "❌ Erro"
            print(f"\n[{status}]: {texto}")
            input("\nPressione ENTER para continuar...")
        elif opcao == "0":
            print("\nEncerrando sistema. Até logo!")
            break
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    main()
