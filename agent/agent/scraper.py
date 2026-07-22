import sys
import requests
import os
import re
import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def extract_username(url):
    raw_input = (url or "").strip()
    if not raw_input:
        return raw_input
    parsed = urlparse(raw_input if "://" in raw_input else f"https://{raw_input}")
    if "://" in raw_input and "github.com" not in parsed.netloc.lower():
        return None
    parts = [p for p in parsed.path.split('/') if p]
    if parts:
        return parts[0]
    return parsed.netloc if parsed.netloc and parsed.netloc.lower() != "github.com" else raw_input

def get_auth_headers():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Warning: GITHUB_TOKEN not found in .env file. Rate limits restricted to 60/hr.")
        return {"Accept": "application/vnd.github.v3+json"}
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_monthly_contributions(username, token):
    if not token:
        return None
    headers = {"Authorization": f"bearer {token}"}
    query = """
    query($userName:String!) {
      user(login: $userName){
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    try:
        response = requests.post(
            'https://api.github.com/graphql',
            json={'query': query, 'variables': {'userName': username}},
            headers=headers
        )
        if response.status_code != 200:
            return {"error": "Failed to fetch"}
        data = response.json()
        if "errors" in data:
            return {"error": "GraphQL returned an error"}
        weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        monthly_commits = {}
        for week in weeks:
            for day in week['contributionDays']:
                count = day['contributionCount']
                date_obj = datetime.datetime.strptime(day['date'], "%Y-%m-%d")
                month_key = date_obj.strftime("%b %Y")
                if month_key not in monthly_commits:
                    monthly_commits[month_key] = 0
                monthly_commits[month_key] += count
        return monthly_commits
    except Exception as e:
        return {"error": str(e)}

def fetch_paginated_data(url, headers):
    results = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break
        results.extend(response.json())
        link_header = response.headers.get('Link', '')
        match = re.search(r'<([^>]+)>; rel="next"', link_header)
        url = match.group(1) if match else None
    return results

def get_commit_data(target_username, owner, repo, headers, known_contributions=0):
    base_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    recent_response = requests.get(f"{base_url}?author={target_username}&per_page=10", headers=headers)
    recent_commits_data = []
    if recent_response.status_code == 200:
        for item in recent_response.json():
            commit_info = item.get("commit", {})
            recent_commits_data.append({
                "sha": item.get("sha"),
                "message": commit_info.get("message", "").split("\n")[0],
                "date": commit_info.get("author", {}).get("date")
            })
    downloaded_count = len(recent_commits_data)
    total_commits = max(known_contributions, downloaded_count)
    if downloaded_count == 10 and known_contributions < 11:
        count_response = requests.get(f"{base_url}?author={target_username}&per_page=1", headers=headers)
        if count_response.status_code == 200:
            link_header = count_response.headers.get('Link', '')
            match = re.search(r'<([^>]+)>;\\s*rel="last"', link_header)
            if match:
                last_url = match.group(1)
                page_match = re.search(r'[?&]page=(\\d+)', last_url)
                if page_match:
                    api_total = int(page_match.group(1))
                    total_commits = max(total_commits, api_total)
    return {"user_commits_count": total_commits, "recent_user_commits": recent_commits_data}

def get_repo_languages(owner, repo, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return {}

def get_repo_details(target_username, owner, repo, headers):
    readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    has_readme = requests.get(readme_url, headers=headers).status_code == 200
    contributors_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    contributors_data = fetch_paginated_data(contributors_url, headers)
    contributors = [{"login": c.get("login"), "contributions": c.get("contributions")} for c in contributors_data] if contributors_data else []
    user_contributions = 0
    total_repo_commits = 0
    for c in contributors:
        contrib_count = c.get("contributions", 0)
        total_repo_commits += contrib_count
        if c.get("login", "").lower() == target_username.lower():
            user_contributions = contrib_count
    commits_data = get_commit_data(target_username, owner, repo, headers, known_contributions=user_contributions)
    total_repo_commits = max(total_repo_commits, commits_data["user_commits_count"])
    commits_data["total_repo_commits"] = total_repo_commits
    commits_data["user_commit_ratio"] = round(commits_data["user_commits_count"] / total_repo_commits, 2) if total_repo_commits > 0 else 0.0
    return {"has_readme": has_readme, "contributors": contributors, "commits": commits_data}

def get_fork_details(username, repo_name, headers):
    repo_resp = requests.get(f"https://api.github.com/repos/{username}/{repo_name}", headers=headers)
    if repo_resp.status_code != 200:
        return None
    parent = repo_resp.json().get("parent", {})
    if not parent:
        return None
    original_owner = parent.get("owner", {}).get("login")
    original_forks = parent.get("forks_count", 0)
    original_stars = parent.get("stargazers_count", 0)
    fork_commits = get_commit_data(username, username, repo_name, headers, known_contributions=0)
    return {
        "repo": repo_name,
        "owner": original_owner,
        "size_kb": repo_resp.json().get("size", 0),
        "forks_count": original_forks,
        "stars_count": original_stars,
        "user_commits_count": fork_commits["user_commits_count"],
        "recent_user_commits": fork_commits["recent_user_commits"]
    }

def run_scraper(target_input: str) -> dict:
    username = extract_username(target_input)
    headers = get_auth_headers()
    token = os.environ.get("GITHUB_TOKEN")
    profile_resp = requests.get(f"https://api.github.com/users/{username}", headers=headers)
    if profile_resp.status_code == 404:
        return {"error": f"User '{username}' not found."}
    profile_data = profile_resp.json()
    monthly_contributions = get_monthly_contributions(username, token)
    repos_url = f"https://api.github.com/users/{username}/repos?type=all"
    repos_raw = fetch_paginated_data(repos_url, headers)
    final_output = {
        "profile": {
            "username": profile_data.get("login"),
            "name": profile_data.get("name"),
            "bio": profile_data.get("bio"),
            "public_repos": profile_data.get("public_repos"),
            "followers": profile_data.get("followers"),
            "following": profile_data.get("following"),
            "scraped_repo_count": len(repos_raw),
            "readme_count": 0,
            "readme_ratio": 0.0,
            "technologies": {},
            "monthly_contributions": monthly_contributions,
            "forked_repositories": []
        },
        "repositories": []
    }
    readme_count = 0
    for repo in repos_raw:
        repo_name = repo.get("name")
        is_fork = repo.get("fork")
        owner_login = repo.get("owner", {}).get("login") or username
        if is_fork:
            fork_data = get_fork_details(username, repo_name, headers)
            if fork_data:
                final_output["profile"]["forked_repositories"].append(fork_data)
        else:
            repo_languages_dict = get_repo_languages(owner_login, repo_name, headers)
            repo_languages_list = list(repo_languages_dict.keys())
            for lang in repo_languages_list:
                final_output["profile"]["technologies"][lang] = final_output["profile"]["technologies"].get(lang, 0) + 1
            details = get_repo_details(username, owner_login, repo_name, headers)
            if details.get("has_readme"):
                readme_count += 1
            repo_schema = {
                "name": repo_name,
                "private": repo.get("private"),
                "size_kb": repo.get("size", 0),
                "description": repo.get("description"),
                "primary_language": repo.get("language"),
                "all_languages": repo_languages_list,
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "deep_metrics": details
            }
            final_output["repositories"].append(repo_schema)
    original_repo_count = len(final_output["repositories"])
    readme_ratio = round(readme_count / original_repo_count, 2) if original_repo_count > 0 else 0.0
    final_output["profile"]["readme_count"] = readme_count
    final_output["profile"]["readme_ratio"] = readme_ratio
    techs = final_output["profile"]["technologies"]
    final_output["profile"]["technologies"] = dict(sorted(techs.items(), key=lambda item: item[1], reverse=True))
    return final_output
