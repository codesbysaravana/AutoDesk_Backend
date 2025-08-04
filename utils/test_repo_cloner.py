# test/test_github_push.py

import unittest
import tempfile
import os
from github_push import create_pr_with_dockerfile

class TestGitHubPush(unittest.TestCase):

    def test_create_pr_with_dockerfile(self):
        # Setup: create dummy Dockerfile
        temp_dir = tempfile.TemporaryDirectory()
        dockerfile_path = os.path.join(temp_dir.name, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write("FROM alpine\nCMD [\"echo\", \"Hello from test\"]\n")

        # Use a test repo you control
        github_url = "https://github.com/codesbysaravana/autodock-test-repo"

        # Run the actual PR creation
        pr_url = create_pr_with_dockerfile(github_url, dockerfile_path)

        print(f"✅ PR created: {pr_url}")
        self.assertTrue("github.com" in pr_url)

        temp_dir.cleanup()

if __name__ == "__main__":
    unittest.main()
