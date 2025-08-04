# utils/analyzer.py

import os

def detect_project_type(repo_path: str) -> str:
    """
    Detect the project type based on the contents of the repo.
    Currently supports: Node.js, Flask, Spring Boot
    """
    print(f"[INFO] Scanning repository at: {repo_path}")
    
    files = os.listdir(repo_path)
    print(f"[DEBUG] Files in repo: {files}")

    if "package.json" in files:
        print("[INFO] Detected Node.js project (package.json found)")
        return "nodejs"
    elif "requirements.txt" in files or "app.py" in files:
        print("[INFO] Detected Flask project (requirements.txt or app.py found)")
        return "flask"
    elif "pom.xml" in files or "build.gradle" in files:
        print("[INFO] Detected Spring Boot project (pom.xml or build.gradle found)")
        return "springboot"
    else:
        print("[ERROR] Could not detect project type from available files.")
        raise ValueError("Could not detect project type. Please ensure it's a Node.js, Flask, or Java Spring Boot project.")
