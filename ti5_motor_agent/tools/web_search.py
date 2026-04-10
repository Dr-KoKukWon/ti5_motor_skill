"""Web and GitHub search tools for TI5 Motor Agent.

Provides real-time search capability for TI5 robot references.
Uses subprocess to call available search tools (gh CLI, curl).
"""

import json
import os
import subprocess
import shutil


def search_github(query: str, repo: str = None) -> dict:
    """Search ti5robot GitHub repositories.

    Uses 'gh' CLI if available, otherwise returns search URL.

    Args:
        query: Search query
        repo: Specific repo name (e.g. 'multiMotorInterfaceCPP')
    """
    gh_path = shutil.which("gh")

    if gh_path is None:
        # Fallback: return search URLs
        if repo:
            url = f"https://github.com/ti5robot/{repo}/search?q={query}"
        else:
            url = f"https://github.com/search?q=org%3Ati5robot+{query}"
        return {
            "success": True,
            "method": "url_only",
            "message": "gh CLI not available. Use these URLs to search manually.",
            "search_url": url,
            "query": query,
        }

    try:
        if repo:
            # Search within a specific repo
            cmd = ["gh", "search", "code", query, f"--repo=ti5robot/{repo}", "--limit=10", "--json=repository,path,textMatch"]
        else:
            # Search across the organization
            cmd = ["gh", "search", "code", query, "--owner=ti5robot", "--limit=10", "--json=repository,path,textMatch"]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                matches = []
                for item in data:
                    match = {
                        "repo": item.get("repository", {}).get("nameWithOwner", ""),
                        "path": item.get("path", ""),
                    }
                    text_matches = item.get("textMatch", [])
                    if text_matches:
                        match["fragment"] = text_matches[0].get("fragment", "")[:200]
                    matches.append(match)

                return {
                    "success": True,
                    "method": "gh_cli",
                    "query": query,
                    "repo_filter": repo,
                    "total": len(matches),
                    "results": matches,
                }
            except json.JSONDecodeError:
                return {"success": True, "method": "gh_cli", "raw_output": result.stdout[:2000]}
        else:
            return {"success": False, "error": result.stderr[:500], "method": "gh_cli"}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "GitHub search timed out after 30s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_web(query: str) -> dict:
    """Search the web for TI5 motor information.

    Uses available tools: curl for basic web fetch, or returns search URLs.
    Automatically prepends 'ti5robot' context to queries.

    Args:
        query: Search query
    """
    # Construct search URLs for manual use
    search_query = f"ti5robot {query}"

    urls = {
        "google": f"https://www.google.com/search?q={search_query.replace(' ', '+')}",
        "github": f"https://github.com/search?q=org%3Ati5robot+{query.replace(' ', '+')}",
        "gitee": f"https://search.gitee.com/?q={search_query.replace(' ', '+')}",
    }

    # Try to fetch GitHub API for repos info
    try:
        cmd = ["curl", "-s", "-H", "Accept: application/vnd.github+json",
               f"https://api.github.com/search/repositories?q={query}+org:ti5robot&per_page=5"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            repos = []
            for item in data.get("items", []):
                repos.append({
                    "name": item["full_name"],
                    "description": item.get("description", ""),
                    "url": item["html_url"],
                    "stars": item.get("stargazers_count", 0),
                    "updated": item.get("updated_at", ""),
                })

            return {
                "success": True,
                "query": search_query,
                "github_repos": repos,
                "search_urls": urls,
            }
    except Exception:
        pass

    return {
        "success": True,
        "method": "urls_only",
        "query": search_query,
        "search_urls": urls,
        "message": "Direct web search not available. Use these URLs to search manually.",
    }
