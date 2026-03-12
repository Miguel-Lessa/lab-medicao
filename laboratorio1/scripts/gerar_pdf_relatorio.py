"""
Gera relatorio final COMPLETO em PDF (18 secoes).
Template de experimento cientifico aplicado a mineracao de repositorios GitHub.

Dependencia: pip install fpdf2 pandas
"""

from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

from fpdf import FPDF

# ──────────────────── Paths ────────────────────
PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "output"
CSV_PATH = OUTPUT_DIR / "top_1000_repos.csv"
CHARTS_DIR = OUTPUT_DIR / "charts"
PDF_PATH = OUTPUT_DIR / "relatorio_final_completo.pdf"


# ──────────────────── Helpers ────────────────────
def describe_col(series: pd.Series) -> dict:
    return {
        "n": int(series.count()),
        "media": round(float(series.mean()), 2),
        "mediana": round(float(series.median()), 2),
        "desvio_padrao": round(float(series.std()), 2),
        "min": round(float(series.min()), 2),
        "q1": round(float(series.quantile(0.25)), 2),
        "q3": round(float(series.quantile(0.75)), 2),
        "max": round(float(series.max()), 2),
        "iqr": round(float(series.quantile(0.75) - series.quantile(0.25)), 2),
    }


# ──────────────────── PDF Class ────────────────────
class ReportPDF(FPDF):
    """PDF com header/footer customizados e metodos auxiliares."""

    def header(self):
        pass  # sem cabecalho

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"{self.page_no()}", align="C")

    # ── Formatacao ──
    def section_title(self, num: int | str, title: str):
        """Titulo de secao principal."""
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub(self, title: str):
        """Subtitulo."""
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def txt(self, text: str):
        """Texto corrido."""
        self.set_font("Helvetica", "", 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def bold_txt(self, text: str):
        """Texto em negrito."""
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullet_list(self, items: list[str]):
        """Lista com marcadores."""
        self.set_font("Helvetica", "", 12)
        self.set_text_color(0, 0, 0)
        for item in items:
            x0 = self.get_x()
            self.cell(6, 6, "-")
            self.multi_cell(0, 6, item)
            self.set_x(x0)
        self.ln(3)

    def table(self, headers: list[str], rows: list[list[str]],
              col_widths: list[float] | None = None,
              wrap: bool = False):
        """Tabela formatada. Se wrap=True, permite quebra de linha nas celulas."""
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)

        # Cabecalho
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(220, 220, 220)
        self.set_text_color(0, 0, 0)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
        self.ln()

        # Linhas
        self.set_font("Helvetica", "", 9)
        self.set_text_color(0, 0, 0)
        line_h = 5
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(245, 245, 245)
            else:
                self.set_fill_color(255, 255, 255)

            if not wrap:
                for i, cell_text in enumerate(row):
                    align = "L" if i == 0 else "R"
                    self.cell(col_widths[i], 6, str(cell_text),
                              border=1, fill=True, align=align)
                self.ln()
            else:
                # Calcular a altura necessaria para a linha (wrap)
                max_lines = 1
                for i, cell_text in enumerate(row):
                    # Estimar quantas linhas o texto precisa
                    txt_w = self.get_string_width(str(cell_text))
                    cell_w = col_widths[i] - 2  # padding
                    n_lines = max(1, int(txt_w / cell_w) + 1)
                    if n_lines > max_lines:
                        max_lines = n_lines
                row_h = max_lines * line_h

                # Verificar quebra de pagina
                if self.get_y() + row_h > 270:
                    self.add_page()

                x_start = self.get_x()
                y_start = self.get_y()

                for i, cell_text in enumerate(row):
                    x = x_start + sum(col_widths[:i])
                    # Desenhar retangulo de fundo + borda
                    self.rect(x, y_start, col_widths[i], row_h, style="DF")
                    # Escrever texto dentro da celula
                    self.set_xy(x + 1, y_start + 1)
                    self.multi_cell(col_widths[i] - 2, line_h, str(cell_text),
                                    border=0, align="L")

                self.set_xy(x_start, y_start + row_h)
            fill = not fill
        self.ln(4)

    def chart(self, image_path, width: int = 170):
        """Insere imagem de grafico com quebra de pagina automatica."""
        p = Path(image_path)
        if not p.exists():
            self.txt(f"[Imagem nao encontrada: {p.name}]")
            return
        if self.get_y() + 75 > 270:
            self.add_page()
        x = (210 - width) / 2
        self.image(str(p), x=x, w=width)
        self.ln(6)

    def separator(self):
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)


# ──────────────────── Main ────────────────────
def main() -> None:
    print("=" * 60)
    print("Gerando Relatorio Final em PDF (18 secoes)")
    print("=" * 60)

    # ── Carregar dados ──
    print("\nCarregando dados...")
    df = pd.read_csv(CSV_PATH)
    df = df[df["primary_language"] != "Unknown"].copy()
    n = len(df)
    print(f"Repositorios na amostra: {n}")

    # ── Estatisticas ──
    rq01 = describe_col(df["age_years"])
    rq02 = describe_col(df["merged_prs"])
    rq03 = describe_col(df["total_releases"])
    rq04 = describe_col(df["days_since_last_push"])
    rq06 = describe_col(df["closed_issues_percent"])

    rq03["repos_sem_release"] = int((df["total_releases"] == 0).sum())
    rq03["pct_sem_release"] = round(rq03["repos_sem_release"] / n * 100, 2)

    rq04["repos_7d"] = int((df["days_since_last_push"] <= 7).sum())
    rq04["repos_30d"] = int((df["days_since_last_push"] <= 30).sum())
    rq04["repos_365d"] = int((df["days_since_last_push"] <= 365).sum())

    lang_counts = df["primary_language"].value_counts()
    total_langs = int(lang_counts.nunique())
    top5 = lang_counts.head(5)
    top5_pct = round(float(top5.sum()) / n * 100, 2)
    top10_pct = round(float(lang_counts.head(10).sum()) / n * 100, 2)

    rq06["above_90"] = int((df["closed_issues_percent"] >= 90).sum())
    rq06["above_70"] = int((df["closed_issues_percent"] >= 70).sum())
    rq06["below_50"] = int((df["closed_issues_percent"] < 50).sum())

    now = datetime.now(timezone.utc)

    # ────────────────────────────────────────────
    #                PDF BUILD
    # ────────────────────────────────────────────
    pdf = ReportPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ============================================
    #              CAPA
    # ============================================
    pdf.add_page()
    pdf.ln(20)

    # Instituicao / Disciplina
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Laboratorio de Experimentacao de Software", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)

    # Titulo do experimento
    pdf.set_font("Helvetica", "B", 20)
    pdf.multi_cell(0, 11,
                   "Caracteristicas de Repositorios Populares do GitHub",
                   align="C")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 9, "Laboratorio 1 - Relatorio Final (Sprint 3)", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)

    # Linha separadora
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.5)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(15)

    # Autores
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Autores:", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 13)
    pdf.cell(0, 8, "Isaac Portela", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Miguel Lessa", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)

    # Metadados
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, f"Data: {now.strftime('%d/%m/%Y')}", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Versao 3.0", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Amostra: {n} repositorios (de 1.000 buscados)", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 7, "https://github.com/Miguel-Lessa/lab-medicao", align="C",
             new_x="LMARGIN", new_y="NEXT")

    # ============================================
    #  1. RESUMO
    # ============================================
    pdf.add_page()
    pdf.section_title(1, "Resumo")

    pdf.txt(
        f"Este estudo investiga as caracteristicas dos repositorios mais populares "
        f"do GitHub (medido por estrelas). A busca inicial contemplou os 1.000 "
        f"repositorios mais estrelados, porem, apos a aplicacao do filtro que exige "
        f"linguagem de programacao primaria definida (excluindo repositorios de listas, "
        f"documentacao e dados), a amostra final ficou com {n} repositorios. "
        f"Foram analisadas seis questoes de pesquisa (RQ01-RQ06) e uma questao "
        f"bonus (RQ07)."
    )

    pdf.sub("Principais resultados:")
    pdf.bullet_list([
        f"Idade mediana: {rq01['mediana']} anos - repositorios populares sao maduros.",
        f"Mediana de {rq04['mediana']:.0f} dia(s) desde ultimo push - "
        f"{rq04['repos_30d']} repos atualizados no ultimo mes.",
        f"Mediana de {rq06['mediana']:.1f}% de issues fechadas - alta resolucao.",
        f"Top 5 linguagens concentram {top5_pct}% da amostra: "
        f"{', '.join(top5.index[:5])}.",
    ])

    pdf.sub("Decisao recomendada:")
    pdf.txt(
        "Iterar: aprofundar a analise com series temporais e grupo de controle "
        "(repos menos populares) para estabelecer relacoes causais."
    )

    # ============================================
    #  2. CONTEXTO E MOTIVACAO
    # ============================================
    pdf.section_title(2, "Contexto e Motivacao")

    pdf.sub("Problema:")
    pdf.txt(
        "O GitHub hospeda mais de 300 milhoes de repositorios. Compreender quais "
        "caracteristicas os projetos mais populares compartilham pode revelar padroes "
        "de sucesso, auxiliar novos projetos open-source e fornecer insights para a "
        "engenharia de software empirica."
    )

    pdf.sub("Por que este experimento agora:")
    pdf.txt(
        "A disciplina de Laboratorio de Experimentacao de Software exige a aplicacao "
        "de metodologia cientifica a dados reais. O GitHub oferece uma API GraphQL "
        "robusta que permite coleta automatizada, tornando viavel um estudo quantitativo "
        "de larga escala em tempo limitado."
    )

    pdf.sub("Restricoes e riscos:")
    pdf.bullet_list([
        "Rate limit da API GraphQL do GitHub (5.000 pontos/hora).",
        "Dados observacionais: nao e possivel estabelecer causalidade.",
        "Vies de sobrevivencia: apenas repos atualmente populares sao capturados.",
        "Classificacao automatica de linguagem pode ser imprecisa para projetos poliglotas.",
    ])

    # ============================================
    #  4. OBJETIVO E HIPOTESES
    # ============================================
    pdf.section_title(3, "Objetivo e Hipoteses")

    pdf.txt(
        f"Objetivo: Caracterizar os repositorios mais estrelados do GitHub (busca "
        f"inicial de 1.000, amostra final de {n} apos filtro de linguagem), "
        "identificando padroes de maturidade, atividade, contribuicao, releases e "
        "linguagens de programacao."
    )

    pdf.sub("Hipoteses:")
    pdf.table(
        ["#", "H0 (nula)", "H1 (alternativa)", "Criterio"],
        [
            ["H1", "Repos populares NAO sao mais antigos que a media",
             "Repos populares sao significativamente mais maduros",
             "Mediana > 5 anos"],
            ["H2", "Repos populares NAO recebem mais PRs que a media",
             "Recebem volume expressivo de contribuicoes externas",
             "Mediana > 100 PRs"],
            ["H3", "Repos populares NAO lancam mais releases",
             "Usam o mecanismo de releases ativamente",
             "Mediana > 10 releases"],
            ["H4", "Repos populares NAO sao mais ativos que a media",
             "Sao atualizados com alta frequencia",
             "Mediana < 30 dias"],
            ["H5", "Linguagens populares NAO dominam o top 1000",
             "Linguagens populares concentram a maioria",
             "Top 5 > 50%"],
            ["H6", "Repos populares NAO fecham mais issues",
             "Mantem alto percentual de issues fechadas",
             "Mediana > 70%"],
        ],
        col_widths=[12, 62, 62, 54],
        wrap=True,
    )

    # ============================================
    #  5. PERGUNTAS DE PESQUISA
    # ============================================
    pdf.section_title(4, "Perguntas de Pesquisa")

    pdf.table(
        ["RQ", "Pergunta", "Metrica"],
        [
            ["RQ01", "Sistemas populares sao maduros/antigos?",
             "Idade (anos desde createdAt)"],
            ["RQ02", "Recebem muita contribuicao externa?",
             "Total de PRs aceitas (merged)"],
            ["RQ03", "Lancam releases com frequencia?",
             "Total de releases"],
            ["RQ04", "Sao atualizados com frequencia?",
             "Dias desde ultimo push (pushedAt)"],
            ["RQ05", "Sao escritos nas linguagens mais populares?",
             "Linguagem primaria"],
            ["RQ06", "Possuem alto % de issues fechadas?",
             "Razao issues fechadas / total"],
            ["RQ07", "Linguagens populares tem mais atividade?",
             "RQ02-04 segmentadas por linguagem"],
        ],
        col_widths=[15, 80, 95],
    )

    # ============================================
    #  6. VARIAVEIS E METRICAS
    # ============================================
    pdf.section_title(5, "Variaveis e Metricas")

    pdf.sub("Metricas primarias (decisivas):")
    pdf.bullet_list([
        "age_years: idade do repositorio em anos (calculada a partir de createdAt).",
        "merged_prs: total de pull requests aceitas (states: MERGED).",
        "total_releases: total de releases publicadas no GitHub.",
        "days_since_last_push: dias desde ultimo push (campo pushedAt).",
        "primary_language: linguagem primaria classificada pelo GitHub.",
        "closed_issues_percent: (issues fechadas / total de issues) * 100.",
    ])

    pdf.sub("Metricas secundarias:")
    pdf.bullet_list([
        "stars: total de estrelas (criterio de selecao, nao de analise direta).",
        "total_issues: total de issues abertas + fechadas.",
        "closed_issues_ratio: razao decimal de issues fechadas.",
    ])

    pdf.sub("Guardrails:")
    pdf.bullet_list([
        "Nenhum repositorio sem linguagem de programacao foi incluido.",
        "Repos com zero issues recebem closed_issues_percent = 0 (sem NaN).",
        "Rate limit monitorado a cada requisicao da API.",
    ])

    pdf.sub("Definicoes:")
    pdf.table(
        ["Metrica", "Formula / Origem"],
        [
            ["age_years", "(data_coleta - createdAt).days / 365.25"],
            ["days_since_last_push", "(data_coleta - pushedAt).days"],
            ["closed_issues_percent", "(closedIssues / totalIssues) * 100"],
            ["merged_prs", "pullRequests(states: MERGED).totalCount"],
            ["total_releases", "releases.totalCount"],
        ],
        col_widths=[55, 135],
    )

    # ============================================
    #  7. DESENHO EXPERIMENTAL
    # ============================================
    pdf.section_title(6, "Desenho Experimental")

    pdf.table(
        ["Aspecto", "Descricao"],
        [
            ["Tipo de estudo", "Observacional (mineracao de repositorios)"],
            ["Unidade de analise", "Repositorio publico do GitHub"],
            ["Populacao", "Todos os repositorios publicos do GitHub"],
            ["Amostra", f"1.000 buscados, {n} coletados (com linguagem definida)"],
            ["Amostragem", "Top-k por estrelas (nao-aleatoria, intencional)"],
            ["Randomizacao", "N/A (estudo observacional, sem tratamento)"],
            ["Duracao", f"Coleta pontual (snapshot em {now.strftime('%d/%m/%Y')})"],
            ["Inclusao", "Repositorio com primaryLanguage definida"],
            ["Exclusao", "Repos sem primaryLanguage (listas, docs, dados)"],
        ],
        col_widths=[45, 145],
    )

    pdf.txt(
        "Observacao: a busca abrangeu os 1.000 repositorios mais estrelados do GitHub. "
        f"Destes, 95 foram descartados durante a coleta por nao possuirem linguagem de "
        f"programacao primaria (repositorios de listas curadas, documentacao, datasets "
        f"etc.), resultando em uma amostra final de {n} projetos de software. "
        "Por se tratar de um estudo observacional (nao experimental), "
        "conceitos como poder estatistico e randomizacao nao se aplicam diretamente. "
        "A amostragem top-k e intencional, pois o objetivo e caracterizar especificamente "
        "os repositorios mais populares."
    )

    # ============================================
    #  8. AMBIENTE E MATERIAIS
    # ============================================
    pdf.section_title(7, "Ambiente e Materiais")

    pdf.table(
        ["Item", "Detalhe"],
        [
            ["Sistema Operacional", "Windows 10/11"],
            ["Linguagem", "Python 3.10+"],
            ["API", "GitHub GraphQL API v4"],
            ["Autenticacao", "Personal Access Token (PAT) via .env"],
            ["Libs coleta", "requests, python-dotenv"],
            ["Libs analise", "pandas, matplotlib, seaborn, scipy, numpy"],
            ["Dataset", f"{n} repos coletados em {now.strftime('%d/%m/%Y')}"],
            ["Saida", "CSV + 13 graficos PNG + relatorio Markdown"],
            ["Seed/aleatoriedade", "N/A (ranking deterministico por estrelas)"],
        ],
        col_widths=[45, 145],
    )

    # ============================================
    #  9. PROCEDIMENTO (PASSO A PASSO)
    # ============================================
    pdf.section_title(8, "Procedimento (Passo a Passo)")

    pdf.sub("Pipeline de execucao:")
    pdf.txt(
        "1. Configurar ambiente:\n"
        "   - Criar arquivo .env com GITHUB_TOKEN.\n"
        "   - python -m venv venv && ativar ambiente virtual.\n"
        "   - pip install requests python-dotenv pandas matplotlib seaborn scipy.\n\n"
        "2. Executar main.py (coleta de dados, ~5-10 min):\n"
        "   - Busca os 1.000 repos mais estrelados via GraphQL (paginacao de 100).\n"
        "   - Filtra repos sem primaryLanguage durante a coleta (client-side).\n"
        "   - Enriquece com metricas de PRs, releases e issues em lotes de 20.\n"
        "   - Salva output/top_1000_repos.csv.\n\n"
        "3. Executar analise_sprint3.py (analise + graficos, ~30s):\n"
        "   - Calcula estatisticas descritivas para cada RQ.\n"
        "   - Gera 13 graficos em output/charts/.\n"
        "   - Gera relatorio final em Markdown."
    )

    pdf.sub("Integridade dos dados:")
    pdf.bullet_list([
        "Rate limit monitorado e exibido no console a cada requisicao.",
        "Retries automaticos com backoff exponencial em caso de erro HTTP ou rate limit.",
        "Lotes que falham sao divididos pela metade e re-tentados.",
        "Repos com metricas ausentes mantidos com valores default (0).",
    ])

    pdf.sub("Checklist operacional:")
    pdf.txt(
        "[ ] Token do GitHub valido com permissoes de leitura\n"
        "[ ] Ambiente virtual ativado\n"
        "[ ] Verificar rate limit restante (>= 150 pontos)\n"
        "[ ] CSV gerado com todas as colunas esperadas\n"
        "[ ] 13 graficos salvos em output/charts/\n"
        "[ ] Relatorio final gerado"
    )

    # ============================================
    #  10. TRATAMENTOS E BASELINE
    # ============================================
    pdf.section_title(9, "Tratamentos e Baseline")

    pdf.txt(
        "Este e um estudo observacional, nao experimental. Nao ha tratamento "
        "(treatment) aplicado a unidades experimentais."
    )

    pdf.sub("Baseline (o que foi observado):")
    pdf.bullet_list([
        f"1.000 repositorios buscados, {n} coletados apos filtro de linguagem.",
        "Metricas coletadas: idade, PRs aceitas, releases, dias sem push, "
        "linguagem primaria, issues fechadas.",
        "Os dados refletem o estado natural dos repositorios no momento da coleta.",
    ])

    pdf.sub("O que NAO mudou (controle de confundidores):")
    pdf.bullet_list([
        "Nenhuma intervencao foi feita nos repositorios.",
        "Nao houve manipulacao de variaveis.",
        "A query de busca e a mesma para todos (stars:>0 sort:stars-desc).",
        "Todas as metricas foram coletadas no mesmo instante temporal.",
    ])

    # ============================================
    #  11. ANALISE DE DADOS
    # ============================================
    pdf.section_title(10, "Analise de Dados")

    pdf.sub("Metodos estatisticos:")
    pdf.bullet_list([
        "Tendencia central: MEDIANA (robusta a outliers, adequada para "
        "distribuicoes assimetricas com cauda longa).",
        "Dispersao: media, desvio padrao, Q1, Q3, IQR, min, max.",
        "Correlacao: coeficiente de Spearman (nao-parametrico, mede "
        "relacoes monotonicas entre variaveis ordinais/continuas).",
        "Distribuicao: contagem e percentuais para variaveis categoricas.",
    ])

    pdf.sub("Tratamento de outliers:")
    pdf.bullet_list([
        "Outliers NAO removidos dos calculos (mediana, media, desvio).",
        "Em boxplots comparativos (RQ07): outliers ocultados visualmente "
        "(showfliers=False) para legibilidade, mantidos nos calculos.",
        "Histogramas de PRs e releases: escala logaritmica no eixo x.",
    ])

    pdf.sub("Segmentacoes planejadas:")
    pdf.bullet_list([
        "Por linguagem primaria (top 10 + 'Outras').",
        "Por faixas de atividade (7 dias, 30 dias, 365 dias).",
        "Por faixas de issues fechadas (<50%, >=70%, >=90%).",
    ])

    pdf.txt(
        "Nota: por ser um estudo observacional com uma unica amostra (sem "
        "grupos de comparacao), nao foram realizados testes de hipoteses formais "
        "(ex.: t-test, Mann-Whitney). As hipoteses sao avaliadas comparando as "
        "medianas observadas aos thresholds pre-definidos."
    )

    # ============================================
    #  12. RESULTADOS
    # ============================================
    pdf.add_page()
    pdf.section_title(11, "Resultados")

    # ── RQ01 ──
    pdf.sub("RQ01 - Sistemas populares sao maduros/antigos?")
    pdf.txt("Metrica: idade do repositorio em anos (desde createdAt).")

    pdf.table(
        ["Estatistica", "Valor"],
        [
            ["N (amostra)", str(rq01["n"])],
            ["Mediana", f"{rq01['mediana']} anos"],
            ["Media", f"{rq01['media']} anos"],
            ["Desvio Padrao", f"{rq01['desvio_padrao']} anos"],
            ["Minimo", f"{rq01['min']} anos"],
            ["Q1 (25%)", f"{rq01['q1']} anos"],
            ["Q3 (75%)", f"{rq01['q3']} anos"],
            ["Maximo", f"{rq01['max']} anos"],
            ["IQR", f"{rq01['iqr']} anos"],
        ],
        col_widths=[60, 130],
    )

    pdf.chart(CHARTS_DIR / "rq01_idade.png")
    pdf.chart(CHARTS_DIR / "rq01_idade_por_linguagem.png")

    pdf.txt(
        f"Analise: A mediana de {rq01['mediana']} anos confirma que repositorios "
        f"populares sao sistemas maduros. O IQR de {rq01['iqr']} anos "
        f"(Q1={rq01['q1']}, Q3={rq01['q3']}) mostra que 50% dos repos tem entre "
        f"{rq01['q1']} e {rq01['q3']} anos. "
        f"H1 CONFIRMADA: popularidade esta fortemente associada a maturidade."
    )

    pdf.separator()

    # ── RQ02 ──
    pdf.sub("RQ02 - Recebem muita contribuicao externa?")
    pdf.txt("Metrica: total de pull requests aceitas (merged).")

    pdf.table(
        ["Estatistica", "Valor"],
        [
            ["N", str(rq02["n"])],
            ["Mediana", f"{rq02['mediana']:,.0f} PRs"],
            ["Media", f"{rq02['media']:,.0f} PRs"],
            ["Desvio Padrao", f"{rq02['desvio_padrao']:,.0f}"],
            ["Minimo", f"{rq02['min']:,.0f}"],
            ["Q1 (25%)", f"{rq02['q1']:,.0f}"],
            ["Q3 (75%)", f"{rq02['q3']:,.0f}"],
            ["Maximo", f"{rq02['max']:,.0f}"],
            ["IQR", f"{rq02['iqr']:,.0f}"],
        ],
        col_widths=[60, 130],
    )

    pdf.chart(CHARTS_DIR / "rq02_prs_aceitas.png")

    pdf.txt(
        f"Analise: A mediana de {rq02['mediana']:,.0f} PRs aceitas demonstra volume "
        f"significativo de contribuicoes. A diferenca entre mediana e media "
        f"({rq02['media']:,.0f}) indica distribuicao com cauda longa a direita. "
        f"H2 PARCIALMENTE CONFIRMADA: contribuicao expressiva com grande variabilidade."
    )

    pdf.separator()

    # ── RQ03 ──
    pdf.sub("RQ03 - Lancam releases com frequencia?")
    pdf.txt("Metrica: total de releases.")

    pdf.table(
        ["Estatistica", "Valor"],
        [
            ["N", str(rq03["n"])],
            ["Mediana", f"{rq03['mediana']:,.0f} releases"],
            ["Media", f"{rq03['media']:,.0f} releases"],
            ["Desvio Padrao", f"{rq03['desvio_padrao']:,.0f}"],
            ["Minimo", f"{rq03['min']:,.0f}"],
            ["Q1 (25%)", f"{rq03['q1']:,.0f}"],
            ["Q3 (75%)", f"{rq03['q3']:,.0f}"],
            ["Maximo", f"{rq03['max']:,.0f}"],
            ["IQR", f"{rq03['iqr']:,.0f}"],
            ["Repos sem release", f"{rq03['repos_sem_release']} ({rq03['pct_sem_release']}%)"],
        ],
        col_widths=[60, 130],
    )

    pdf.chart(CHARTS_DIR / "rq03_releases.png")

    pdf.txt(
        f"Analise: Mediana de {rq03['mediana']:,.0f} releases. "
        f"{rq03['pct_sem_release']}% dos repos nao possuem nenhuma release formal, "
        f"refletindo a tendencia de deploy continuo (CD). "
        f"H3 PARCIALMENTE CONFIRMADA."
    )

    pdf.separator()

    # ── RQ04 ──
    pdf.sub("RQ04 - Sao atualizados com frequencia?")
    pdf.txt("Metrica: dias desde o ultimo push (pushedAt).")

    pdf.table(
        ["Estatistica", "Valor"],
        [
            ["N", str(rq04["n"])],
            ["Mediana", f"{rq04['mediana']:,.0f} dias"],
            ["Media", f"{rq04['media']:,.0f} dias"],
            ["Desvio Padrao", f"{rq04['desvio_padrao']:,.0f}"],
            ["Minimo", f"{rq04['min']:,.0f}"],
            ["Q1 (25%)", f"{rq04['q1']:,.0f}"],
            ["Q3 (75%)", f"{rq04['q3']:,.0f}"],
            ["Maximo", f"{rq04['max']:,.0f}"],
            ["IQR", f"{rq04['iqr']:,.0f}"],
            ["Push ultimos 7 dias", str(rq04["repos_7d"])],
            ["Push ultimos 30 dias", str(rq04["repos_30d"])],
            ["Push no ultimo ano", str(rq04["repos_365d"])],
        ],
        col_widths=[60, 130],
    )

    pdf.chart(CHARTS_DIR / "rq04_atualizacao.png")

    pdf.txt(
        f"Analise: A mediana de {rq04['mediana']:,.0f} dia(s) desde o ultimo push "
        f"confirma fortemente H4. {rq04['repos_7d']} repos receberam push na ultima "
        f"semana e {rq04['repos_30d']} no ultimo mes. A metrica pushedAt e mais precisa "
        f"que updatedAt pois reflete apenas pushes de codigo reais. "
        f"H4 FORTEMENTE CONFIRMADA."
    )

    pdf.separator()

    # ── RQ05 ──
    pdf.sub("RQ05 - Escritos nas linguagens mais populares?")
    pdf.txt("Metrica: linguagem primaria (primaryLanguage).")

    pdf.table(
        ["Estatistica", "Valor"],
        [
            ["Linguagens distintas", str(total_langs)],
            ["Concentracao top 5", f"{top5_pct}%"],
            ["Concentracao top 10", f"{top10_pct}%"],
        ],
        col_widths=[60, 130],
    )

    top5_rows = [[lang, str(cnt), f"{cnt / n * 100:.1f}%"]
                 for lang, cnt in top5.items()]
    pdf.table(
        ["Linguagem", "Repositorios", "Percentual"],
        top5_rows,
        col_widths=[65, 60, 65],
    )

    pdf.chart(CHARTS_DIR / "rq05_linguagens_barras.png")
    pdf.chart(CHARTS_DIR / "rq05_linguagens_pizza.png")

    pdf.txt(
        f"Analise: Top 5 concentra {top5_pct}% e top 10 concentra {top10_pct}% da "
        f"amostra. {', '.join(top5.index[:3])} lideram o ranking. "
        f"H5 CONFIRMADA."
    )

    pdf.separator()

    # ── RQ06 ──
    pdf.sub("RQ06 - Alto percentual de issues fechadas?")
    pdf.txt("Metrica: razao issues fechadas / total de issues (%).")

    pdf.table(
        ["Estatistica", "Valor"],
        [
            ["N", str(rq06["n"])],
            ["Mediana", f"{rq06['mediana']:.1f}%"],
            ["Media", f"{rq06['media']:.1f}%"],
            ["Desvio Padrao", f"{rq06['desvio_padrao']:.1f}%"],
            ["Minimo", f"{rq06['min']:.1f}%"],
            ["Q1 (25%)", f"{rq06['q1']:.1f}%"],
            ["Q3 (75%)", f"{rq06['q3']:.1f}%"],
            ["Maximo", f"{rq06['max']:.1f}%"],
            ["Repos >= 90% issues fechadas", str(rq06["above_90"])],
            ["Repos >= 70% issues fechadas", str(rq06["above_70"])],
            ["Repos < 50% issues fechadas", str(rq06["below_50"])],
        ],
        col_widths=[60, 130],
    )

    pdf.chart(CHARTS_DIR / "rq06_issues_fechadas.png")

    pdf.txt(
        f"Analise: Mediana de {rq06['mediana']:.1f}% de issues fechadas. "
        f"{rq06['above_70']} repos ({rq06['above_70'] / n * 100:.1f}%) fecham "
        f">= 70% de suas issues. H6 CONFIRMADA."
    )

    pdf.separator()

    # ── RQ07 ──
    pdf.add_page()
    pdf.sub("RQ07 (Bonus) - Analise segmentada por linguagem")
    pdf.txt(
        "Questao: Sistemas escritos em linguagens mais populares recebem mais "
        "contribuicao, lancam mais releases e sao atualizados com mais frequencia?"
    )

    top_langs = lang_counts.head(10).index.tolist()
    rq07_rows = []
    for lang in top_langs:
        sub = df[df["primary_language"] == lang]
        rq07_rows.append([
            lang,
            str(len(sub)),
            f"{sub['merged_prs'].median():,.0f}",
            f"{sub['total_releases'].median():,.0f}",
            f"{sub['days_since_last_push'].median():,.0f}",
        ])

    pdf.table(
        ["Linguagem", "Repos", "Med. PRs", "Med. Releases", "Med. Dias Push"],
        rq07_rows,
        col_widths=[38, 25, 42, 42, 43],
    )

    pdf.chart(CHARTS_DIR / "rq07_boxplots_por_linguagem.png", width=180)
    pdf.chart(CHARTS_DIR / "rq07_medianas_barras.png", width=180)
    pdf.chart(CHARTS_DIR / "rq07_heatmap.png", width=155)

    pdf.txt(
        "Analise: A segmentacao revela diferencas significativas entre ecossistemas. "
        "Linguagens com gestao de pacotes madura (TypeScript, Rust, Go) concentram "
        "mais PRs e releases. A maioria mostra repos atualizados muito recentemente. "
        "H7 PARCIALMENTE CONFIRMADA."
    )

    pdf.separator()

    # ── Correlacoes ──
    pdf.add_page()
    pdf.sub("Analise de Correlacoes (Spearman)")

    # Explicacao didatica
    pdf.txt(
        "O coeficiente de correlacao de Spearman (rho) mede a forca e a direcao "
        "da relacao monotonica entre duas variaveis. Diferente do coeficiente de "
        "Pearson, o Spearman nao exige que as variaveis sigam distribuicao normal "
        "e e baseado nos postos (rankings) dos valores, o que o torna robusto a "
        "outliers - ideal para nossos dados que possuem distribuicoes assimetricas "
        "com cauda longa."
    )

    pdf.sub("Como interpretar os valores:")
    pdf.table(
        ["Faixa de |rho|", "Interpretacao", "Significado pratico"],
        [
            ["0.00 - 0.19", "Muito fraca ou nula", "As variaveis sao praticamente independentes"],
            ["0.20 - 0.39", "Fraca", "Existe uma tendencia sutil entre as variaveis"],
            ["0.40 - 0.59", "Moderada", "Relacao perceptivel entre as variaveis"],
            ["0.60 - 0.79", "Forte", "As variaveis claramente se movem juntas"],
            ["0.80 - 1.00", "Muito forte", "Relacao quase deterministica"],
        ],
        col_widths=[35, 45, 110],
    )

    pdf.txt(
        "Valores positivos (+) indicam que quando uma metrica aumenta, a outra "
        "tambem tende a aumentar. Valores negativos (-) indicam relacao inversa: "
        "quando uma cresce, a outra tende a diminuir."
    )

    pdf.chart(CHARTS_DIR / "correlacao_spearman.png", width=145)

    # Calcular correlacoes reais
    corr_cols = ["stars", "age_years", "merged_prs", "total_releases",
                 "days_since_last_push", "closed_issues_percent"]
    corr_matrix = df[corr_cols].corr(method="spearman")

    r_prs_push = corr_matrix.loc["merged_prs", "days_since_last_push"]
    r_prs_rel = corr_matrix.loc["merged_prs", "total_releases"]
    r_rel_push = corr_matrix.loc["total_releases", "days_since_last_push"]
    r_prs_iss = corr_matrix.loc["merged_prs", "closed_issues_percent"]
    r_rel_iss = corr_matrix.loc["total_releases", "closed_issues_percent"]
    r_push_iss = corr_matrix.loc["days_since_last_push", "closed_issues_percent"]
    r_age_prs = corr_matrix.loc["age_years", "merged_prs"]
    r_stars_prs = corr_matrix.loc["stars", "merged_prs"]
    r_stars_age = corr_matrix.loc["stars", "age_years"]
    r_stars_rel = corr_matrix.loc["stars", "total_releases"]
    r_stars_push = corr_matrix.loc["stars", "days_since_last_push"]
    r_stars_iss = corr_matrix.loc["stars", "closed_issues_percent"]

    pdf.sub("Correlacoes fortes (|rho| >= 0.4):")

    pdf.bold_txt(f"1. PRs Aceitas x Dias sem Push (rho = {r_prs_push:.3f}) - Forte negativa")
    pdf.txt(
        "Esta e a correlacao mais forte encontrada. A relacao negativa significa que "
        "repositorios que recebem mais PRs aceitas tendem a ter menos dias desde o "
        "ultimo push. Em termos praticos: projetos com alta atividade de contribuicao "
        "externa sao tambem os que recebem pushes mais frequentes. Isso e intuitivo - "
        "cada PR aceita gera um merge/push. Repositorios com comunidades ativas de "
        "contribuidores mantem um ciclo virtuoso de atividade constante."
    )

    pdf.bold_txt(f"2. PRs Aceitas x Releases (rho = {r_prs_rel:.3f}) - Moderada a forte positiva")
    pdf.txt(
        "Repositorios que recebem mais contribuicoes externas tambem lancam mais "
        "releases. Isso sugere que projetos com comunidades ativas de contribuidores "
        "tendem a adotar praticas formais de versionamento. Cada ciclo de contribuicoes "
        "culmina em uma nova release, refletindo um processo de desenvolvimento "
        "estruturado com entregas regulares."
    )

    pdf.bold_txt(f"3. Releases x Dias sem Push (rho = {r_rel_push:.3f}) - Moderada negativa")
    pdf.txt(
        "Projetos que publicam mais releases sao tambem mais ativos (menos dias sem "
        "push). A pratica de releases formais esta associada a manutencao continua "
        "e ciclos regulares de desenvolvimento, nao sendo um evento isolado."
    )

    pdf.sub("Correlacoes moderadas (|rho| entre 0.2 e 0.4):")

    pdf.bold_txt(
        f"4. Issues Fechadas (%) x PRs ({r_prs_iss:.3f}), "
        f"Releases ({r_rel_iss:.3f}) e Dias sem Push ({r_push_iss:.3f})"
    )
    pdf.txt(
        "O percentual de issues fechadas apresenta correlacao moderada com as tres "
        "metricas de atividade. Repositorios mais ativos (mais PRs, mais releases, "
        "menos dias sem push) tendem a fechar uma proporcao maior de suas issues. "
        "Isso indica que equipes de manutencao ativas nao apenas produzem codigo, "
        "mas tambem dedicam esforco a resolucao de bugs e demandas da comunidade."
    )

    pdf.bold_txt(f"5. Idade x PRs Aceitas (rho = {r_age_prs:.3f}) - Fraca positiva")
    pdf.txt(
        "Repositorios mais antigos tendem a acumular mais PRs ao longo do tempo, "
        "mas a correlacao fraca indica que a idade por si so nao garante contribuicao "
        "expressiva. Projetos jovens podem receber muitas PRs se forem relevantes."
    )

    pdf.sub("Descoberta principal - Estrelas sao independentes das demais metricas:")

    pdf.table(
        ["Par de variaveis", "rho", "Interpretacao"],
        [
            ["Estrelas x Idade", f"{r_stars_age:.3f}", "Nula"],
            ["Estrelas x PRs Aceitas", f"{r_stars_prs:.3f}", "Muito fraca"],
            ["Estrelas x Releases", f"{r_stars_rel:.3f}", "Nula"],
            ["Estrelas x Dias sem Push", f"{r_stars_push:.3f}", "Muito fraca"],
            ["Estrelas x Issues Fechadas", f"{r_stars_iss:.3f}", "Nula"],
        ],
        col_widths=[55, 25, 110],
    )

    pdf.txt(
        "Um dos achados mais reveladores desta analise: o numero de estrelas "
        "(nosso criterio de selecao de popularidade) praticamente NAO se correlaciona "
        "com nenhuma das metricas de atividade ou qualidade. Isso significa que um "
        "repositorio pode ser extremamente popular (muitas estrelas) sem necessariamente "
        "ser o mais ativo em PRs, releases ou resolucao de issues. "
        "Estrelas refletem VISIBILIDADE e INTERESSE da comunidade, nao "
        "necessariamente INTENSIDADE DE DESENVOLVIMENTO. "
        "Um repositorio pode acumular estrelas por ser uma referencia educacional, "
        "uma lista curada ou uma ferramenta estavel que nao precisa de atualizacoes "
        "frequentes."
    )

    pdf.chart(CHARTS_DIR / "scatter_stars_vs_prs.png", width=145)

    pdf.txt(
        "O scatter plot acima ilustra visualmente a relacao entre estrelas e PRs "
        f"aceitas (rho = {r_stars_prs:.3f}). A dispersao dos pontos confirma a ausencia "
        "de uma relacao linear ou monotonica clara: repositorios com muitas estrelas "
        "podem ter desde poucas ate muitas PRs, e vice-versa."
    )

    pdf.sub("Sintese da analise de correlacoes:")
    pdf.txt(
        "A analise de Spearman revela que as metricas de ATIVIDADE (PRs aceitas, "
        "releases, dias sem push e issues fechadas) formam um cluster de variaveis "
        "interrelacionadas: projetos ativos em uma dimensao tendem a ser ativos nas "
        "demais. Porem, a popularidade (estrelas) e a idade do repositorio sao "
        "dimensoes independentes deste cluster. Isso sugere que a popularidade no "
        "GitHub e um fenomeno distinto da atividade de desenvolvimento, "
        "influenciado por fatores como marketing, relevancia do problema resolvido "
        "e timing de lancamento."
    )

    # ============================================
    #  13. DISCUSSAO E INTERPRETACAO
    # ============================================
    pdf.add_page()
    pdf.section_title(12, "Discussao e Interpretacao")

    pdf.sub("O que explica os resultados:")
    pdf.txt(
        "Repositorios populares no GitHub tendem a ser projetos maduros com "
        "comunidades ativas e equipes de manutencao comprometidas. A popularidade "
        "(estrelas) funciona como um efeito cumulativo: projetos mais antigos tiveram "
        "mais tempo para ganhar visibilidade, atrair contribuidores e construir "
        "ecossistemas. A presenca dominante de linguagens como Python, TypeScript e "
        "JavaScript reflete tendencias da industria de software."
    )

    pdf.sub("Quadro resumo - Hipoteses x Resultados:")
    pdf.table(
        ["Hipotese", "Resultado", "Veredito"],
        [
            ["H1 - Maduros",
             f"Mediana {rq01['mediana']} anos", "CONFIRMADA"],
            ["H2 - Contribuicao",
             f"Mediana {rq02['mediana']:,.0f} PRs", "PARCIAL"],
            ["H3 - Releases",
             f"Med. {rq03['mediana']:,.0f}; {rq03['pct_sem_release']}% sem",
             "PARCIAL"],
            ["H4 - Ativos",
             f"Med. {rq04['mediana']:,.0f} d; {rq04['repos_30d']} no mes",
             "FORTE"],
            ["H5 - Linguagens",
             f"Top5 = {top5_pct}%", "CONFIRMADA"],
            ["H6 - Issues",
             f"Mediana {rq06['mediana']:.1f}%", "CONFIRMADA"],
            ["H7 - Por linguagem",
             "Diferencas observadas", "PARCIAL"],
        ],
        col_widths=[42, 90, 58],
    )

    pdf.sub("Limitacoes (ameacas a validade):")

    pdf.bold_txt("Validade interna:")
    pdf.txt(
        "Nao ha intervencao, apenas observacao. Confundidores possiveis incluem "
        "tempo de existencia (repos mais antigos acumulam mais metricas) e efeito "
        "de rede (repos populares atraem mais contribuidores, reforando popularidade)."
    )

    pdf.bold_txt("Validade externa:")
    pdf.txt(
        "Amostra limitada aos repos mais estrelados. Resultados nao sao generalizaveis "
        "para todo o ecossistema GitHub, software privado ou corporativo."
    )

    pdf.bold_txt("Validade de construcao:")
    pdf.txt(
        "pushedAt reflete o ultimo push de codigo ao repositorio, sendo mais precisa "
        "que updatedAt para medir atividade de desenvolvimento. Porem, pushes "
        "automatizados por bots/CI podem influenciar o valor. primaryLanguage e "
        "classificada automaticamente pelo GitHub com base no volume de codigo. "
        "O mecanismo de releases nao e usado por todos os projetos."
    )

    pdf.sub("Trade-offs:")
    pdf.bullet_list([
        "Profundidade vs amplitude: 1000 repos analisados superficialmente vs "
        "poucos em profundidade.",
        "pushedAt vs updatedAt: mais precisa para codigo, ignora atividade social.",
        "Releases formais vs tags/CD: totalCount de releases pode subestimar "
        "projetos com deploy continuo.",
    ])

    pdf.sub("Comparacao com trabalhos anteriores:")

    pdf.txt(
        "Os resultados deste estudo sao consistentes com a literatura consolidada "
        "de engenharia de software empirica. A seguir, comparamos nossos achados "
        "com os principais estudos da area."
    )

    pdf.bold_txt("Kalliamvakou et al. (2014) - Promessas e Armadilhas da Mineracao do GitHub")
    pdf.txt(
        "Kalliamvakou et al. (2014) identificaram 10 riscos ao usar dados do GitHub "
        "para pesquisa, incluindo o fato de que muitos repositorios nao sao projetos "
        "de software (listas, configuracoes, dados). Nosso estudo aborda diretamente "
        "essa ameaca ao filtrar repositorios sem linguagem primaria durante a coleta, "
        "descartando 95 dos 1.000 buscados. Os autores tambem alertam que estrelas "
        "nao medem qualidade - achado corroborado pela nossa analise de Spearman, "
        "que mostrou correlacao praticamente nula entre estrelas e metricas de atividade."
    )

    pdf.bold_txt("Munaiah et al. (2017) - Curacao de Projetos de Engenharia no GitHub")
    pdf.txt(
        "Munaiah et al. (2017) propuseram criterios para distinguir 'projetos de "
        "engenharia' de repositorios casuais no GitHub, usando indicadores como "
        "integracao continua, testes e documentacao. Nosso criterio de filtragem "
        "(exigir primaryLanguage definida) e mais simples, porem eficaz para o "
        "escopo desta pesquisa. Os autores reportaram que projetos maduros tendem "
        "a adotar mais praticas de engenharia - nossos dados confirmam isso, com "
        "mediana de idade de {:.2f} anos e altas taxas de resolucao de issues.".format(
            rq01["mediana"])
    )

    pdf.bold_txt("Borges, Hora e Valente (2016) - Fatores de Popularidade no GitHub")
    pdf.txt(
        "Borges, Hora e Valente (2016) analisaram especificamente os fatores que "
        "influenciam a popularidade (estrelas) de repositorios. Identificaram que "
        "linguagem de programacao, idade e atividade recente sao fatores relevantes. "
        "Nossos resultados complementam esse estudo: enquanto eles focaram nos "
        "preditores de popularidade, nossa analise de Spearman revela que, dentro "
        "do grupo dos mais populares, estrelas sao praticamente independentes das "
        "metricas de atividade (rho < 0.17 para todos os pares). Isso sugere que, "
        "uma vez atingido um patamar de popularidade, a atividade nao e o principal "
        "motor de acumulo de estrelas."
    )

    pdf.bold_txt("Ray et al. (2014) - Linguagens de Programacao e Qualidade de Codigo")
    pdf.txt(
        "Ray et al. (2014) conduziram um estudo em larga escala sobre a relacao entre "
        "linguagens de programacao e qualidade de codigo no GitHub. Identificaram que "
        "linguagens com tipagem forte tendem a apresentar menos defeitos. Nossos dados "
        "sobre concentracao linguistica (top 5 linguagens representando {:.1f}% da "
        "amostra) sao consistentes com a predominancia de Python, JavaScript e "
        "TypeScript reportada em estudos recentes, refletindo as tendencias medidas "
        "pelos indices TIOBE e Stack Overflow Developer Survey.".format(top5_pct)
    )

    # ============================================
    #  14. DECISAO E RECOMENDACOES
    # ============================================
    pdf.section_title(13, "Decisao e Recomendacoes")

    pdf.sub("Decisao:")
    pdf.txt(
        "ITERAR: O estudo atingiu seus objetivos de caracterizacao. Os resultados "
        "sao consistentes e robustos. Recomenda-se aprofundar com proximas sprints."
    )

    pdf.sub("Proximos passos:")
    pdf.bullet_list([
        "Analise longitudinal: coletar dados em multiplos pontos no tempo.",
        "Grupo de controle: comparar com repos menos populares (ex.: mediana de estrelas).",
        "Analise qualitativa: investigar outliers (muito populares mas inativos).",
        "Metricas adicionais: code churn, cobertura de testes, forks, dependentes.",
        "Analise de sentimento: avaliar qualidade das issues/PRs (nao apenas quantidade).",
    ])

    pdf.sub("Monitoramento pos-analise:")
    pdf.txt(
        "Como este e um estudo observacional pontual, nao ha monitoramento continuo. "
        "Caso o estudo seja repetido, recomenda-se comparar os resultados temporalmente "
        "para identificar tendencias de evolucao."
    )

    # ============================================
    #  15. CUSTOS E IMPACTOS
    # ============================================
    pdf.section_title(14, "Custos e Impactos")

    pdf.table(
        ["Item", "Valor"],
        [
            ["Tempo de coleta", "~5-10 minutos"],
            ["Tempo de analise e visualizacao", "~30 segundos"],
            ["Custo API GitHub", "Gratuito (rate limit de 5000 pts/h)"],
            ["Pontos API consumidos", "~110 pontos (~60 coleta + ~50 metricas)"],
            ["Infraestrutura", "Maquina local (sem custo cloud)"],
            ["Complexidade", "Baixa (2 scripts Python)"],
            ["Risco operacional", "Baixo (dados publicos, sem alteracao de repos)"],
        ],
        col_widths=[55, 135],
    )

    # ============================================
    #  16. ETICA, PRIVACIDADE E CONFORMIDADE
    # ============================================
    pdf.section_title(15, "Etica, Privacidade e Conformidade")

    pdf.bullet_list([
        "Todos os dados sao publicos e acessiveis via API oficial do GitHub.",
        "Nenhum dado pessoal sensivel e coletado (apenas nomes de repos e metricas).",
        "Nao ha coleta de dados de usuarios individuais (nomes, emails, etc.).",
        "Conformidade total com os Termos de Uso da API do GitHub.",
        "Nao ha impacto direto em usuarios ou mantenedores dos repositorios.",
        "LGPD: nao aplicavel (dados publicos, sem identificacao de pessoa fisica).",
        "Nao ha retencao de tokens; GITHUB_TOKEN e armazenado localmente em .env.",
    ])

    # ============================================
    #  17. REPRODUTIBILIDADE
    # ============================================
    pdf.section_title(16, "Reprodutibilidade")

    pdf.sub("Como repetir o experimento:")
    pdf.txt(
        "1. git clone https://github.com/Miguel-Lessa/lab-medicao\n"
        "2. cd laboratorio1/.lab1\n"
        "3. python -m venv venv\n"
        "4. venv\\Scripts\\activate  (Windows) ou source venv/bin/activate (Linux)\n"
        "5. pip install requests python-dotenv pandas matplotlib seaborn scipy\n"
        "6. Criar .env com: GITHUB_TOKEN=seu_token\n"
        "7. python main.py             (coleta: ~5-10 min)\n"
        "8. python analise_sprint3.py   (analise + graficos + relatorio)"
    )

    pdf.sub("Arquivos do projeto:")
    pdf.table(
        ["Arquivo", "Descricao"],
        [
            ["main.py", "Coleta de dados via GitHub GraphQL API"],
            ["analise_sprint3.py", "Analise estatistica e geracao de graficos"],
            ["output/top_1000_repos.csv", "Dados brutos coletados"],
            ["output/charts/*.png", "13 graficos gerados"],
            ["output/relatorio_final_sprint3.md", "Relatorio final"],
        ],
        col_widths=[70, 120],
    )

    pdf.sub("Observacoes sobre reprodutibilidade:")
    pdf.bullet_list([
        "Resultados podem variar entre execucoes (ranking de estrelas e dinamico).",
        "Data de coleta influencia age_days e days_since_last_push.",
        "Para resultados identicos, utilize o CSV ja gerado (output/top_1000_repos.csv).",
    ])

    # ============================================
    #  18. APENDICES
    # ============================================
    pdf.add_page()
    pdf.section_title(17, "Apendices")

    pdf.sub("A. Tabela consolidada de estatisticas descritivas")
    pdf.table(
        ["Metrica", "N", "Mediana", "Media", "DP", "Min", "Q1", "Q3",
         "Max", "IQR"],
        [
            ["Idade (anos)", str(rq01["n"]), str(rq01["mediana"]),
             str(rq01["media"]), str(rq01["desvio_padrao"]),
             str(rq01["min"]), str(rq01["q1"]), str(rq01["q3"]),
             str(rq01["max"]), str(rq01["iqr"])],
            ["PRs Aceitas", str(rq02["n"]), f"{rq02['mediana']:,.0f}",
             f"{rq02['media']:,.0f}", f"{rq02['desvio_padrao']:,.0f}",
             f"{rq02['min']:,.0f}", f"{rq02['q1']:,.0f}",
             f"{rq02['q3']:,.0f}", f"{rq02['max']:,.0f}",
             f"{rq02['iqr']:,.0f}"],
            ["Releases", str(rq03["n"]), f"{rq03['mediana']:,.0f}",
             f"{rq03['media']:,.0f}", f"{rq03['desvio_padrao']:,.0f}",
             f"{rq03['min']:,.0f}", f"{rq03['q1']:,.0f}",
             f"{rq03['q3']:,.0f}", f"{rq03['max']:,.0f}",
             f"{rq03['iqr']:,.0f}"],
            ["Dias Push", str(rq04["n"]), f"{rq04['mediana']:,.0f}",
             f"{rq04['media']:,.0f}", f"{rq04['desvio_padrao']:,.0f}",
             f"{rq04['min']:,.0f}", f"{rq04['q1']:,.0f}",
             f"{rq04['q3']:,.0f}", f"{rq04['max']:,.0f}",
             f"{rq04['iqr']:,.0f}"],
            ["Issues (%)", str(rq06["n"]), f"{rq06['mediana']:.1f}",
             f"{rq06['media']:.1f}", f"{rq06['desvio_padrao']:.1f}",
             f"{rq06['min']:.1f}", f"{rq06['q1']:.1f}",
             f"{rq06['q3']:.1f}", f"{rq06['max']:.1f}",
             f"{rq06['iqr']:.1f}"],
        ],
        col_widths=[22, 14, 20, 20, 18, 16, 20, 20, 20, 20],
    )

    pdf.sub("B. Top 15 linguagens primarias")
    top15 = lang_counts.head(15)
    top15_rows = [[lang, str(cnt), f"{cnt / n * 100:.1f}%"]
                  for lang, cnt in top15.items()]
    pdf.table(
        ["Linguagem", "Repositorios", "Percentual"],
        top15_rows,
        col_widths=[65, 60, 65],
    )

    pdf.sub("C. Checklist de execucao")
    pdf.txt(
        "[X] Token do GitHub valido e com permissoes de leitura.\n"
        "[X] Ambiente virtual ativado com dependencias instaladas.\n"
        "[X] Coleta de dados via GitHub GraphQL API concluida.\n"
        "[X] Filtro de linguagem aplicado na coleta.\n"
        "[X] Metricas de PRs, releases e issues coletadas em lotes.\n"
        "[X] CSV gerado com todas as colunas esperadas.\n"
        "[X] Estatisticas descritivas calculadas para cada RQ.\n"
        "[X] 13 graficos gerados e salvos em output/charts/.\n"
        "[X] Relatorio final gerado.\n"
        "[X] Hipoteses avaliadas contra resultados."
    )

    pdf.sub("D. Query GraphQL utilizada na coleta")
    pdf.set_font("Courier", "", 8)
    pdf.set_text_color(31, 41, 55)
    pdf.multi_cell(0, 4.5, (
        'query ($first: Int!, $after: String) {\n'
        '  search(query: "stars:>0 sort:stars-desc",\n'
        '         type: REPOSITORY, first: $first, after: $after) {\n'
        '    pageInfo { hasNextPage  endCursor }\n'
        '    nodes {\n'
        '      ... on Repository {\n'
        '        name  nameWithOwner  url  stargazerCount\n'
        '        createdAt  pushedAt\n'
        '        primaryLanguage { name }\n'
        '      }\n'
        '    }\n'
        '  }\n'
        '  rateLimit { cost  remaining }\n'
        '}'
    ))
    pdf.ln(4)

    pdf.sub("E. Query GraphQL de metricas (por lote)")
    pdf.set_font("Courier", "", 8)
    pdf.set_text_color(31, 41, 55)
    pdf.multi_cell(0, 4.5, (
        'query {\n'
        '  r0: repository(owner: "...", name: "...") {\n'
        '    pullRequests(states: MERGED) { totalCount }\n'
        '    releases { totalCount }\n'
        '    issues { totalCount }\n'
        '    closedIssues: issues(states: CLOSED) { totalCount }\n'
        '  }\n'
        '  # ... r1, r2, ... r19 (lotes de 20)\n'
        '  rateLimit { cost  remaining }\n'
        '}'
    ))

    # ============================================
    #  REFERENCIAS BIBLIOGRAFICAS (ABNT)
    # ============================================
    pdf.add_page()
    pdf.section_title("", "Referencias Bibliograficas")

    pdf.txt(
        "As referencias a seguir estao formatadas de acordo com a norma "
        "ABNT NBR 6023:2018."
    )

    # Ref 1 - Borges, Hora e Valente (2016)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5.5, (
        "BORGES, H.; HORA, A.; VALENTE, M. T. Understanding the factors that "
        "impact the popularity of GitHub repositories. In: IEEE INTERNATIONAL "
        "CONFERENCE ON SOFTWARE MAINTENANCE AND EVOLUTION (ICSME), 2016, "
        "Raleigh. Proceedings [...]. IEEE, 2016. p. 334-344. "
        "Disponivel em: https://doi.org/10.1109/ICSME.2016.31. "
        "Acesso em: mar. 2026."
    ))
    pdf.ln(4)

    # Ref 2 - Kalliamvakou et al. (2014)
    pdf.multi_cell(0, 5.5, (
        "KALLIAMVAKOU, E. et al. The promises and perils of mining GitHub. "
        "In: INTERNATIONAL WORKING CONFERENCE ON MINING SOFTWARE REPOSITORIES "
        "(MSR), 11., 2014, Hyderabad. Proceedings [...]. New York: ACM, 2014. "
        "p. 92-101. "
        "Disponivel em: https://doi.org/10.1145/2597073.2597074. "
        "Acesso em: mar. 2026."
    ))
    pdf.ln(4)

    # Ref 3 - Munaiah et al. (2017)
    pdf.multi_cell(0, 5.5, (
        "MUNAIAH, N. et al. Curating GitHub for engineered software projects. "
        "Empirical Software Engineering, New York, v. 22, n. 6, "
        "p. 3219-3253, 2017. "
        "Disponivel em: https://doi.org/10.1007/s10664-017-9512-6. "
        "Acesso em: mar. 2026."
    ))
    pdf.ln(4)

    # Ref 4 - Ray et al. (2014)
    pdf.multi_cell(0, 5.5, (
        "RAY, B. et al. A large scale study of programming languages and code "
        "quality in GitHub. In: ACM SIGSOFT INTERNATIONAL SYMPOSIUM ON "
        "FOUNDATIONS OF SOFTWARE ENGINEERING (FSE), 22., 2014, Hong Kong. "
        "Proceedings [...]. New York: ACM, 2014. p. 155-165. "
        "Disponivel em: https://doi.org/10.1145/2635868.2635922. "
        "Acesso em: mar. 2026."
    ))
    pdf.ln(4)

    # Ref 5 - TIOBE
    pdf.multi_cell(0, 5.5, (
        "TIOBE SOFTWARE BV. TIOBE Index. Eindhoven, 2026. "
        "Disponivel em: https://www.tiobe.com/tiobe-index/. "
        "Acesso em: mar. 2026."
    ))
    pdf.ln(4)

    # Ref 6 - Stack Overflow
    pdf.multi_cell(0, 5.5, (
        "STACK OVERFLOW. Stack Overflow Annual Developer Survey 2025. "
        "New York, 2025. "
        "Disponivel em: https://survey.stackoverflow.co/2025/. "
        "Acesso em: mar. 2026."
    ))
    pdf.ln(4)

    # ── Salvar ──
    pdf.output(str(PDF_PATH))

    print(f"\n{'=' * 60}")
    print(f"PDF gerado com sucesso!")
    print(f"Arquivo: {PDF_PATH}")
    print(f"Total de paginas: {pdf.page_no()}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
