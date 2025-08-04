from github import Github

def auto_merge_pr(repo_name: str, branch: str, base_branch: str = "main"):
    """
    Automatically merges a PR from `branch` into `main` if it exists.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("Missing GITHUB_TOKEN")

    gh = Github(token)
    user = gh.get_user()
    repo = user.get_repo(repo_name)

    pulls = repo.get_pulls(state='open', base=base_branch, head=f"{user.login}:{branch}")

    for pr in pulls:
        try:
            pr.merge(commit_message="Auto-merging PR created by AutoDock 🚀")
            print(f"✅ PR #{pr.number} merged successfully!")
            return True
        except Exception as e:
            raise RuntimeError(f"❌ Failed to merge PR #{pr.number}: {e}")

    raise RuntimeError("❌ No matching open PR found to merge.")
