import requests
import os
from dotenv import load_dotenv

def get_popular_repos(num_repos):
    if num_repos <= 0 or num_repos > 10000:
        raise ValueError("Número de repositórios deve estar entre 1 e 10000.")
        
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

if __name__ == "__main__":
    num_repos = 10  
    try:
        popular_repos = get_popular_repos(num_repos)
        for repo in popular_repos:
            print(f"Repository: {repo['node']['name']}, Owner: {repo['node']['owner']['login']}, Stars: {repo['node']['stargazerCount']}, URL: {repo['node']['url']}")
    except Exception as e:
        print(e)
