# backend/main.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from utils.repo_cloner import clone_repo
from utils.analyzer import detect_project_type
from utils.dockerfile_generator import generate_dockerfile
from utils.github_push import create_pr_with_dockerfile
from utils.aws_deploy import deploy_to_aws_ec2
import os

app = FastAPI()

class DeployRequest(BaseModel):
    github_url: str
    aws_access_key: str
    aws_secret_key: str
    aws_region: str = "us-east-1"
    github_pat: str  # <-- NEW FIELD


@app.get("/")
async def root():
    return {"message": "Welcome to AutoDock AI! Use /deploy to deploy your app."}

@app.post("/deploy")
async def deploy_app(req: DeployRequest):
    try:
        # locally analyze:
        repo_path = clone_repo(req.github_url)
        print("📁 Cloned repo contents:", os.listdir(repo_path))

        tech_stack = detect_project_type(repo_path)
        dockerfile_path = generate_dockerfile(repo_path, tech_stack)
        pr_url = create_pr_with_dockerfile(req.github_url, dockerfile_path, req.github_pat)

        # deploy using the GITHUB URL directly:
        public_ip = deploy_to_aws_ec2(
            aws_access_key=req.aws_access_key,
            aws_secret_key=req.aws_secret_key,
            region=req.aws_region,
            repo_path=req.github_url,     # <=== pass URL here
            tech_stack=tech_stack
        )

        print(f"[INFO] App deployed and accessible at: http://{public_ip}")
        return {
            "message": "Deployed successfully",
            "url": f"http://{public_ip}",
            "pr_url": pr_url,
            "status": "Dockerfile PR created and auto-merged ✅"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
