import requests
import os
from datetime import datetime, timezone


#REPOSITORIOS
def get_popular_repos(num_repos):        
    query = f"""
    {{
      search(query: "stars:>0", type: REPOSITORY, first: {num_repos}) {{
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
              primaryLanguage {{name
              }}
            }}
          }}
        }}
      }}
    }}
    """
    
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json={"query": query}, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]["search"]["edges"]
    else:
        raise Exception(f"Falha em obter repositórios: {response.status_code}, {response.json()}")
      
#PULL REQUESTS    
def get_repo_pull_requests(owner, repo, num_prs=100):

    query = f"""
    {{
      repository(owner: "{owner}", name: "{repo}") {{
        pullRequests(first: {num_prs}, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
          nodes {{
            state
            createdAt
            mergedAt
          }}
        }}
      }}
    }}
    """

    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(url, json={"query": query}, headers=headers)

    if response.status_code == 200:
        return response.json()["data"]["repository"]["pullRequests"]["nodes"]
    else:
        raise Exception(response.json())
      
#ANALISE DE PULL REQUESTS      
def analyze_pull_requests(prs):

    total_prs = len(prs)
    merged_prs = sum(1 for pr in prs if pr["state"] == "MERGED")
    closed_prs = sum(1 for pr in prs if pr["state"] == "CLOSED")
    open_prs = sum(1 for pr in prs if pr["state"] == "OPEN")

    merge_rate = (merged_prs / total_prs) * 100 if total_prs > 0 else 0

    print(f"Total PRs: {total_prs}")
    print(f"PRs aceitas (MERGED): {merged_prs}")
    print(f"PRs fechadas sem merge: {closed_prs}")
    print(f"PRs abertas: {open_prs}")
    print(f"Taxa de aceitação: {merge_rate:.2f}%")
    
#RELEASES 
def get_repo_releases(owner, repo, num_releases=100):

    query = f"""
    {{
      repository(owner: "{owner}", name: "{repo}") {{
        releases(first: {num_releases}, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
          nodes {{
            name
            tagName
            createdAt
            publishedAt
            isDraft
            isPrerelease
            url
          }}
        }}
      }}
    }}
    """

    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(url, json={"query": query}, headers=headers)

    if response.status_code == 200:
        return response.json()["data"]["repository"]["releases"]["nodes"]
    else:
        raise Exception(response.json())

def get_repo_issues(owner, repo, num_issues = 50):
  
    query = f"""
    {{
      repository(owner: "{owner}", name: "{repo}") {{
        issues(first: {num_issues}, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
          nodes {{
            state
            createdAt
            closedAt
          }}
        }}
      }}
    }}
    """
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(url, json={"query": query}, headers=headers)

    if response.status_code == 200:
        return response.json()["data"]["repository"]["issues"]["nodes"]
    else:
        raise Exception(response.json())
      
#ANALISA ISSUES
def issues_analyzer (issues):
  total = len (issues)
  open_issues = sum (1 for issue in issues if issue["state"] == "OPEN")
  closed_issues = sum (1 for issue in issues if issue["state"] == "CLOSED")
  
  close_rate = (closed_issues / total) *100 if total > 0 else 0
  
  print(f"Total issues analisadas: {total}")
  print(f"Issues abertas: {open_issues}")
  print(f"Issues fechadas: {closed_issues}")
  print(f"Taxa de fechamento: {close_rate:.2f}%")
      
      
#MAIN
if __name__ == "__main__":
    num_repos = 10  

    try:
        popular_repos = get_popular_repos(num_repos)

        for repo in popular_repos:
          
            node = repo['node']
            language_info = node['primaryLanguage']
            
            if not language_info:
              continue
            if language_info['name'] == "Markdown":
              continue

            owner = repo['node']['owner']['login']
            name = repo['node']['name']
            updated_at_str = repo['node']['updatedAt']
            updated_at = datetime.fromisoformat(
              updated_at_str.replace ("Z", "+00:00")
            )
            
            now = datetime.now(timezone.utc)
            delta = now - updated_at
            hours_since_update = delta.total_seconds() / 3600
            days_since_update = delta.days
            
            node = repo ['node']
            if node ['primaryLanguage'] :
              language = node ['primaryLanguage'] ['name'] 
            else :
              language = "Sem linguagem"
                         
            print("\n==============================")
            print(f"Repository: {name}")
            print(f"Owner: {owner}")
            print(f"Stars: {repo['node']['stargazerCount']}")
            print(f"Created At: {repo['node']['createdAt']}")
            print(f"Ultima atualização: {updated_at_str}")
            print(f"Dias desde a ultima atualização: {days_since_update}")
            print(f"Horas desde a ultima atualização: {hours_since_update}")
            print(f"Linguagem primária: {language}")
            print("==============================")

            prs = get_repo_pull_requests(owner, name, 100)
            analyze_pull_requests(prs)

            releases = get_repo_releases(owner, name, 10)

            print(f"Total releases: {len(releases)}")
            
            issues = get_repo_issues(owner, name, 100)
            issues_analyzer(issues)
            
            for release in releases:
                print(
                    f"Release: {release['tagName']} | "
                    f"Published: {release['publishedAt']} | "
                    f"Pre-release: {release['isPrerelease']}"
                )
            
                

    except Exception as e:
        print(e)