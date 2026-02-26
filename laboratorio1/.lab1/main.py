import requests
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import time

# Carrega variáveis de ambiente
load_dotenv()
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN não encontrado. Crie um arquivo .env com GITHUB_TOKEN=seu_token")

# Termos a excluir na busca (livros, documentação, etc.)
EXCLUDED_TERMS = ["book", "ebook", "tutorial", "guide", "awesome-list", 
                  "awesome", "curated", "learning", "course"]

URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {token}"}

def run_query(query):
    """Executa uma query GraphQL e retorna o resultado."""
    response = requests.post(URL, json={"query": query}, headers=HEADERS)
    if response.status_code == 200:
        result = response.json()
        if "errors" in result:
            raise Exception(f"Erros GraphQL: {result['errors']}")
        return result
    else:
        raise Exception(f"Query falhou: {response.status_code}, {response.json()}")

#REPOSITORIOS (com paginação, máximo 100 por página)
def get_popular_repos(total):        
    """Busca repositórios populares ordenados por estrelas com paginação."""
    all_repos = []
    cursor = None
    
    while len(all_repos) < total:
        cursor_str = f', after: "{cursor}"' if cursor else ""
        query = f"""
        {{
          search(query: "stars:>0 sort:stars-desc", type: REPOSITORY, first: 100{cursor_str}) {{
            pageInfo {{
              hasNextPage
              endCursor
            }}
            edges {{
              node {{
                ... on Repository {{
                  name
                  owner {{
                    login
                  }}
                  stargazerCount
                  url
                  createdAt
                  updatedAt
                  primaryLanguage {{
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        data = run_query(query)
        search_data = data["data"]["search"]
        all_repos.extend(search_data["edges"])
        
        if not search_data["pageInfo"]["hasNextPage"]:
            break
        cursor = search_data["pageInfo"]["endCursor"]
        time.sleep(0.5)
    
    return all_repos

# COLETA TODAS AS MÉTRICAS DE UM REPOSITÓRIO EM UMA ÚNICA QUERY
def get_repo_metrics(owner, repo):
    """
    Coleta PRs aceitas, total de releases e issues (abertas/fechadas)
    em UMA ÚNICA requisição GraphQL usando totalCount.
    """
    query = f"""
    {{
      repository(owner: "{owner}", name: "{repo}") {{
        pullRequests(states: MERGED) {{
          totalCount
        }}
        releases {{
          totalCount
        }}
        issues {{
          totalCount
        }}
        closedIssues: issues(states: CLOSED) {{
          totalCount
        }}
      }}
    }}
    """
    data = run_query(query)
    repo_data = data["data"]["repository"]
    
    return {
        "merged_prs": repo_data["pullRequests"]["totalCount"],
        "total_releases": repo_data["releases"]["totalCount"],
        "total_issues": repo_data["issues"]["totalCount"],
        "closed_issues": repo_data["closedIssues"]["totalCount"],
    }

#MAIN
if __name__ == "__main__":
    num_repos = 100  # Lab01S01: 100 repositórios

    try:
        # Busca mais repositórios para compensar os que serão filtrados
        fetch_count = num_repos * 2
        print(f"Coletando dados de {num_repos} repositórios mais populares (apenas programação)...")
        print(f"Buscando {fetch_count} repositórios da API (para filtrar depois)...")
        popular_repos = get_popular_repos(fetch_count)
        print(f"Total de repositórios obtidos da API: {len(popular_repos)}")
        print("Filtrando apenas repositórios de programação...\n")

        repos_processed = 0
        for idx, repo in enumerate(popular_repos, 1):
            # Para quando coletar os repositórios necessários
            if repos_processed >= num_repos:
                break
            
            try:
                node = repo['node']
                language_info = node['primaryLanguage']
                
                # Pula repositórios sem linguagem
                if not language_info:
                    continue
                
                # Pula repositórios com linguagem Markdown (não são código)
                if language_info['name'] == "Markdown":
                    continue
                
                # Filtra repositórios que parecem ser livros/documentação pelo nome
                repo_name = node['name'].lower()
                if any(term in repo_name for term in EXCLUDED_TERMS):
                    continue

                owner = node['owner']['login']
                name = node['name']
                language = language_info['name']
                
                # RQ 01: Calcular idade do repositório
                created_at_str = node['createdAt']
                created_at = datetime.fromisoformat(
                    created_at_str.replace("Z", "+00:00")
                )
                now = datetime.now(timezone.utc)
                age_delta = now - created_at
                repo_age_days = age_delta.days
                repo_age_years = repo_age_days / 365.25
                
                # RQ 04: Tempo até última atualização
                updated_at_str = node['updatedAt']
                updated_at = datetime.fromisoformat(
                    updated_at_str.replace("Z", "+00:00")
                )
                update_delta = now - updated_at
                days_since_update = update_delta.days
                hours_since_update = update_delta.total_seconds() / 3600
                
                # Coleta PRs, Releases e Issues em UMA ÚNICA query
                metrics = get_repo_metrics(owner, name)
                
                # RQ 06: Taxa de fechamento de issues
                total_issues = metrics["total_issues"]
                closed_issues = metrics["closed_issues"]
                issues_close_rate = (closed_issues / total_issues * 100) if total_issues > 0 else 0
                
                repos_processed += 1
                
                # Exibe resultados
                print(f"\n[{repos_processed}/{num_repos}] ==============================")
                print(f"Repository: {name}")
                print(f"Owner: {owner}")
                print(f"Stars: {node['stargazerCount']}")
                print(f"Linguagem primária: {language} [RQ 05]")
                print(f"Idade do repositório: {repo_age_days} dias ({repo_age_years:.2f} anos) [RQ 01]")
                print(f"Total de PRs aceitas (MERGED): {metrics['merged_prs']} [RQ 02]")
                print(f"Total de releases: {metrics['total_releases']} [RQ 03]")
                print(f"Dias desde última atualização: {days_since_update} [RQ 04]")
                print(f"Issues fechadas/total: {closed_issues}/{total_issues} ({issues_close_rate:.2f}%) [RQ 06]")
                print("==============================")
                
            except Exception as e:
                print(f"Erro ao processar repositório: {e}")
                continue

        print(f"\n\nProcessamento concluído! Total de repositórios processados: {repos_processed}")

    except Exception as e:
        print(f"Erro geral: {e}")
