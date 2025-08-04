# utils/repo_cloner.py

import os
import tempfile
from git import Repo

def clone_repo(github_url: str) -> str:
    temp_dir = tempfile.mkdtemp()
    try:
        Repo.clone_from(github_url, temp_dir)
        print(f"[clone_repo] Cloning into temp dir: {temp_dir}")
        return temp_dir
    except Exception as e:
        raise RuntimeError(f"Failed to clone repo: {e}")

