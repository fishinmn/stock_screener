import os
import subprocess
import sys


def git_push_shortcut(commit_message):
    if os.getenv("GITHUB_ACTIONS") == "true":
        print("Skipping git push in GitHub Actions; generated files remain in the workspace.")
        return

    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Successfully staged, committed, and pushed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during Git operation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "automated commit from script"
    git_push_shortcut(msg)