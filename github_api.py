import base64
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()


class GitHubConfigError(Exception):
    pass


class GitHubUploadError(Exception):
    pass


def github_repository():
    repository = os.getenv("GITHUB_REPOSITORY")
    if repository:
        return repository.strip()

    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    if owner and repo:
        return f"{owner.strip()}/{repo.strip()}"

    return None


def is_enabled():
    return bool(os.getenv("GITHUB_TOKEN") and github_repository())


def upload_file(local_path, repo_path, commit_message=None):
    token = os.getenv("GITHUB_TOKEN")
    repository = github_repository()
    branch = os.getenv("GITHUB_BRANCH", "main")
    api_base_url = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com").rstrip("/")

    if not token:
        raise GitHubConfigError("GITHUB_TOKEN is not set")
    if not repository:
        raise GitHubConfigError("GITHUB_REPOSITORY or GITHUB_OWNER/GITHUB_REPO is not set")

    local_path = Path(local_path)
    repo_path = repo_path.replace("\\", "/").lstrip("/")
    content = base64.b64encode(local_path.read_bytes()).decode("ascii")
    message = commit_message or f"Add LINE uploaded image {repo_path}"

    url = f"{api_base_url}/repos/{repository}/contents/{repo_path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "message": message,
        "content": content,
        "branch": branch,
    }

    existing_sha = get_existing_sha(url, headers, branch)
    if existing_sha:
        payload["sha"] = existing_sha

    committer = github_committer()
    if committer:
        payload["committer"] = committer

    response = requests.put(url, headers=headers, json=payload, timeout=30)
    if response.status_code not in (200, 201):
        raise GitHubUploadError(f"GitHub upload failed: {response.status_code} {response.text}")

    return response.json()


def get_existing_sha(url, headers, branch):
    response = requests.get(url, headers=headers, params={"ref": branch}, timeout=30)
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise GitHubUploadError(f"GitHub lookup failed: {response.status_code} {response.text}")

    data = response.json()
    return data.get("sha")


def github_committer():
    name = os.getenv("GITHUB_COMMITTER_NAME")
    email = os.getenv("GITHUB_COMMITTER_EMAIL")
    if name and email:
        return {"name": name, "email": email}
    return None
