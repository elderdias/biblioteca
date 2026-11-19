import csv
import os
from datetime import datetime, date
from database import get_connection

def converter_data(texto_data: str):
    """Converte strings em formatos comuns (DD/MM/AAAA ou AAAA-MM-DD) para objeto date."""
    if not texto_data or not str(texto_data).strip():
        return None
    texto = str(texto_data).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Data inválida: '{texto}'. Use o formato DD/MM/AAAA ou AAAA-MM-DD.")

def gerar_relatorio_emprestimos(
    id_aluno: int = None,
    id_livro: int = None,
    data_inicio = None,
    data_fim = None,
    status: str = None
):
    """
    Gera uma lista detalhada de empréstimos aplicando filtros opcionais por:
    - Aluno (id_aluno)
    - Livro (id_livro)
    - Período de data de empréstimo (data_inicio até data_fim)
    - Status ('EMPRESTADO' ou 'DEVOLVIDO')
    """
    clausulas = []
    parametros = []

    if id_aluno is not None:
        clausulas.append("e.id_aluno = %s")
        parametros.append(id_aluno)

    if id_livro is not None:
        clausulas.append("e.id_livro = %s")
        parametros.append(id_livro)

    if data_inicio:
        dt_ini = converter_data(data_inicio) if isinstance(data_inicio, str) else data_inicio
        clausulas.append("e.data_emprestimo::date >= %s")
        parametros.append(dt_ini)

    if data_fim:
        dt_fim = converter_data(data_fim) if isinstance(data_fim, str) else data_fim
        clausulas.append("e.data_emprestimo::date <= %s")
        parametros.append(dt_fim)

    if status and status.upper() in ("EMPRESTADO", "DEVOLVIDO"):
        clausulas.append("e.status = %s")
        parametros.append(status.upper())

    where_sql = ("WHERE " + " AND ".join(clausulas)) if clausulas else ""

    query = f"""
        SELECT 
            e.id_emprestimo,
            e.id_aluno,
            a.nome AS nome_aluno,
            a.matricula AS matricula_aluno,
            a.email AS email_aluno,
            a.telefone AS telefone_aluno,
            e.id_livro,
            l.titulo AS titulo_livro,
            l.autor AS autor_livro,
            l.isbn AS isbn_livro,
            e.data_emprestimo,
            e.data_previsao_devolucao,
            e.data_devolucao,
            e.status
        FROM emprestimos e
        JOIN alunos a ON e.id_aluno = a.id_aluno
        JOIN livros l ON e.id_livro = l.id_livro
        {where_sql}
        ORDER BY e.data_emprestimo DESC;
    """

    hoje = date.today()
    registros = []

    with get_connection(as_dict=True) as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(parametros))
            linhas = cur.fetchall()

    for item in linhas:
        # Calcular se está em atraso
        prev = item["data_previsao_devolucao"]
        dev = item["data_devolucao"]
        em_aberto = (dev is None and item["status"] == "EMPRESTADO")
        
        atrasado = False
        dias_atraso = 0
        if em_aberto and prev and hoje > prev:
            atrasado = True
            dias_atraso = (hoje - prev).days

        item_dict = dict(item)
        item_dict["atrasado"] = atrasado
        item_dict["dias_atraso"] = dias_atraso
        registros.append(item_dict)

    return registros

def exportar_relatorio_csv(registros: list, caminho_arquivo: str):
    """
    Exporta a lista de registros para um arquivo CSV com codificação UTF-8-SIG (compatível com Excel).
    """
    colunas = [
        "ID Empréstimo",
        "Aluno",
        "Matrícula",
        "E-mail",
        "Telefone",
        "Título do Livro",
        "Autor",
        "ISBN",
        "Data Empréstimo",
        "Previsão Devolução",
        "Data Devolução",
        "Status",
        "Situação / Atraso"
    ]

    with open(caminho_arquivo, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(colunas)

        for r in registros:
            dt_emp = r["data_emprestimo"].strftime("%d/%m/%Y %H:%M") if r.get("data_emprestimo") else ""
            dt_prev = r["data_previsao_devolucao"].strftime("%d/%m/%Y") if r.get("data_previsao_devolucao") else ""
            dt_dev = r["data_devolucao"].strftime("%d/%m/%Y %H:%M") if r.get("data_devolucao") else ""

            if r.get("atrasado"):
                situacao = f"ATRASADO ({r['dias_atraso']} dias)"
            else:
                situacao = "No prazo" if r["status"] == "EMPRESTADO" else "Devolvido"

            writer.writerow([
                r["id_emprestimo"],
                r["nome_aluno"],
                r["matricula_aluno"],
                r["email_aluno"] or "",
                r["telefone_aluno"] or "",
                r["titulo_livro"],
                r["autor_livro"],
                r["isbn_livro"] or "",
                dt_emp,
                dt_prev,
                dt_dev,
                r["status"],
                situacao
            ])

def exportar_relatorio_html(registros: list, caminho_arquivo: str, filtros_desc: str = "Todos os registros"):
    """
    Gera um relatório formatado em HTML com layout limpo e suporte para impressão ou salvar como PDF.
    """
    total = len(registros)
    ativos = sum(1 for r in registros if r["status"] == "EMPRESTADO")
    devolvidos = sum(1 for r in registros if r["status"] == "DEVOLVIDO")
    atrasados = sum(1 for r in registros if r.get("atrasado"))

    linhas_html = []
    for r in registros:
        dt_emp = r["data_emprestimo"].strftime("%d/%m/%Y %H:%M") if r.get("data_emprestimo") else "-"
        dt_prev = r["data_previsao_devolucao"].strftime("%d/%m/%Y") if r.get("data_previsao_devolucao") else "-"
        dt_dev = r["data_devolucao"].strftime("%d/%m/%Y %H:%M") if r.get("data_devolucao") else "-"

        if r.get("atrasado"):
            badge = f'<span class="badge badge-danger">Atrasado ({r["dias_atraso"]}d)</span>'
        elif r["status"] == "EMPRESTADO":
            badge = '<span class="badge badge-warning">Emprestado</span>'
        else:
            badge = '<span class="badge badge-success">Devolvido</span>'

        linhas_html.append(f"""
        <tr>
            <td style="text-align: center;">{r['id_emprestimo']}</td>
            <td><strong>{r['nome_aluno']}</strong><br><small style="color: #64748b;">Matrícula: {r['matricula_aluno']}</small></td>
            <td><strong>{r['titulo_livro']}</strong><br><small style="color: #64748b;">Autor: {r['autor_livro']}</small></td>
            <td style="text-align: center;">{dt_emp}</td>
            <td style="text-align: center;">{dt_prev}</td>
            <td style="text-align: center;">{dt_dev}</td>
            <td style="text-align: center;">{badge}</td>
        </tr>
        """)

    tabela_conteudo = "\n".join(linhas_html) if linhas_html else '<tr><td colspan="7" style="text-align: center; padding: 20px;">Nenhum empréstimo encontrado para os filtros selecionados.</td></tr>'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Empréstimos - Biblioteca</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            margin: 30px;
            color: #1e293b;
            background-color: #f8fafc;
        }}
        .header {{
            background: #ffffff;
            padding: 24px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }}
        .header h1 {{ margin: 0 0 6px 0; font-size: 22px; color: #0f172a; }}
        .header p {{ margin: 0; color: #64748b; font-size: 13px; }}
        .kpis {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            flex: 1;
            background: #ffffff;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            text-align: center;
        }}
        .kpi-num {{ font-size: 24px; font-weight: bold; color: #0f172a; }}
        .kpi-label {{ font-size: 12px; color: #64748b; text-transform: uppercase; margin-top: 4px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }}
        th {{
            background: #f1f5f9;
            color: #475569;
            font-size: 12px;
            text-transform: uppercase;
            padding: 12px;
            border-bottom: 1px solid #cbd5e1;
        }}
        td {{
            padding: 10px 12px;
            font-size: 13px;
            border-bottom: 1px solid #f1f5f9;
        }}
        tr:hover {{ background-color: #f8fafc; }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        .badge-success {{ background: #dcfce7; color: #166534; }}
        .badge-danger {{ background: #fee2e2; color: #991b1b; }}
        .no-print {{
            margin-bottom: 20px;
        }}
        .btn {{
            background: #2563eb;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }}
        @media print {{
            .no-print {{ display: none; }}
            body {{ background: #ffffff; margin: 0; }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="btn" onclick="window.print()">🖨️ Imprimir / Salvar em PDF</button>
    </div>

    <div class="header">
        <h1>📚 Relatório de Empréstimos da Biblioteca</h1>
        <p>Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')} | Filtros: {filtros_desc}</p>
    </div>

    <div class="kpis">
        <div class="kpi-card">
            <div class="kpi-num">{total}</div>
            <div class="kpi-label">Total Listado</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-num" style="color: #d97706;">{ativos}</div>
            <div class="kpi-label">Empréstimos Ativos</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-num" style="color: #16a34a;">{devolvidos}</div>
            <div class="kpi-label">Devolvidos</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-num" style="color: #dc2626;">{atrasados}</div>
            <div class="kpi-label">Em Atraso</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Aluno</th>
                <th>Livro</th>
                <th>Data Empréstimo</th>
                <th>Previsão Devolução</th>
                <th>Data Devolução</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {tabela_conteudo}
        </tbody>
    </table>
</body>
</html>
"""
    with open(caminho_arquivo, mode="w", encoding="utf-8") as f:
        f.write(html)
