# 🚀 AutoDock – One-Click Dockerized Deployment to AWS EC2

**AutoDock** automates the deployment of any project to an AWS EC2 instance using Docker. It provisions EC2, connects via SSH, installs Docker, clones your repo, builds the Docker container, and launches the app — all with a single command.

---

## 📦 Features

- 🏗️ Launches a fresh EC2 instance automatically  
- 🔐 SSH access using your own `.pem` key  
- 🐳 Installs Docker and Docker Compose  
- 📥 Clones your GitHub repo  
- 🔧 Auto-detects project stack (e.g., Python, Node.js)  
- 🛠️ Builds Docker image and runs container  
- 🌐 Returns public EC2 IP with live app  

---

## 🧰 Folder Structure

AutoDock/
│
├── main.py # Entrypoint – coordinates full deployment
├── utils/
│ ├── aws_deploy.py # EC2 setup, SSH, Docker install, deployment
│ ├── repo_cloner.py # Clones the GitHub repo
│ ├── detect_stack.py # Detects tech stack (Node/Python/etc.)
│ └── dockerfile_generator.py # Generates Dockerfile based on stack
├── requirements.txt # Python dependencies
├── README.md # You're reading this!

yaml
Copy
Edit

---

## 🔧 Prerequisites

- Python 3.8+  
- AWS IAM credentials (Access Key + Secret)  
- A valid `.pem` SSH key with access to EC2  
- GitHub repo with a valid project (e.g., Python FastAPI, Node.js Express)

---

## 📥 Install
git clone https://github.com/your-username/AutoDock.git
cd AutoDock
pip install -r requirements.txt
🚀 Usage
bash
Copy
Edit
python main.py
You'll be prompted to enter:

Your AWS Access Key and Secret Key

Your AWS region (e.g., us-east-1)

Your GitHub repo URL

Your local path to .pem file

🔄 How It Works — Step-by-Step
1. 🧠 Project Type Detection
File: utils/detect_stack.py

Scans your repo files for keywords to detect the tech stack:

Looks for app.py, main.py, requirements.txt → Python

Looks for index.js, package.json → Node.js

This determines how your Dockerfile will be generated.

2. 📁 GitHub Repo Cloning
File: utils/repo_cloner.py

Uses GitPython to:

Clone your GitHub repo to a temp directory

Return the path so other scripts can work on it

3. 📄 Dockerfile Generation
File: utils/dockerfile_generator.py

Creates a tailored Dockerfile based on the detected stack:

For Python:

dockerfile
Copy
Edit
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
For Node.js:

dockerfile
Copy
Edit
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
CMD ["node", "index.js"]
You can extend support to other languages like Go, Java, etc.

4. ☁️ AWS EC2 Provisioning + SSH + Docker
File: utils/aws_deploy.py

The core of AutoDock:

Uses boto3 to launch an EC2 instance (Ubuntu)

SSH into the instance using .pem key (via paramiko)

Installs:

Git

Docker

Docker Compose

Clones your GitHub project onto EC2

Writes Dockerfile

Builds and runs Docker container

Exposes app on port 80

Returns public EC2 IP

5. 🌍 Deployment Complete
Once running, you’ll see:

cpp
Copy
Edit
✅ Deployed successfully! Visit: http://<EC2-PUBLIC-IP>
🧪 Example Output
bash
Copy
Edit
Enter AWS Access Key: ********************
Enter AWS Secret Key: ********************
Enter AWS Region: us-east-1
Enter GitHub Repo URL: https://github.com/yourname/my-fastapi-app
Enter Path to .pem Key: ~/.ssh/my-key.pem

Detecting stack... ✅ Python detected.
Cloning repo... ✅ Success.
Generating Dockerfile... ✅ Done.
Launching EC2... ✅ Instance running.
Connecting via SSH... ✅ Connected.
Installing Docker... ✅ Done.
Cloning repo to EC2... ✅
Building Docker image... ✅
Running container... ✅

🌐 Visit your app: http://54.167.xx.xx
🛠️ Tech Stack
Python

boto3 (AWS SDK)

paramiko (SSH)

GitPython

Docker

EC2 (Ubuntu AMI)

🧠 Ideas for Improvements
Add HTTPS via Nginx + Certbot

Add CI/CD from GitHub

Add support for S3, RDS, Load Balancer

Add web UI for easier input

Auto shutdown EC2 after idle time

📄 License
MIT License