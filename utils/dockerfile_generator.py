import os

def generate_dockerfile(repo_path: str, tech_stack: str) -> str:
    """
    Generate a Dockerfile based on the detected tech stack.
    Writes the file inside the repo and returns the path.
    """
    tech_stack = tech_stack.lower()
    dockerfile_path = os.path.join(repo_path, "Dockerfile")

    if tech_stack == "nodejs":
        content = """
        FROM node:18-alpine
        WORKDIR /app
        COPY package*.json ./
        RUN npm install
        COPY . .
        EXPOSE 3000
        CMD ["npm", "start"]
        """

    elif tech_stack == "flask":
        content = """
        FROM python:3.11-slim
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install -r requirements.txt
        COPY . .
        EXPOSE 5000
        CMD ["python", "app.py"]
        """

    elif tech_stack == "springboot":
        content = """
        FROM openjdk:17-jdk-slim
        WORKDIR /app
        COPY target/*.jar app.jar
        EXPOSE 8080
        CMD ["java", "-jar", "app.jar"]
        """

    else:
        raise ValueError(f"❌ No Dockerfile template available for tech stack: '{tech_stack}'")

    try:
        with open(dockerfile_path, "w") as f:
            f.write(content.strip() + "\n")
        print(f"✅ Dockerfile successfully generated at: {dockerfile_path}")
        return dockerfile_path
    except Exception as e:
        print(f"❌ Failed to write Dockerfile: {e}")
        return None
