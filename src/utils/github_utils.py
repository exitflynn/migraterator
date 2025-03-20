import requests
import os

def get_pr_files(repo_name, pr_number, github_token):
    """
    Get the list of files changed in a PR
    
    Args:
        repo_name: Repository name in format "owner/repo"
        pr_number: PR number
        github_token: GitHub token for authentication
        
    Returns:
        List of file paths changed in the PR
    """
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    files_data = response.json()
    
    # Extract file paths
    file_paths = [file_data["filename"] for file_data in files_data]
    
    return file_paths

def post_pr_comment(repo_name, pr_number, github_token, comment_body):
    """
    Post a comment on a PR
    
    Args:
        repo_name: Repository name in format "owner/repo"
        pr_number: PR number
        github_token: GitHub token for authentication
        comment_body: Comment text
        
    Returns:
        Response from GitHub API
    """
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "body": comment_body
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    return response.json() 