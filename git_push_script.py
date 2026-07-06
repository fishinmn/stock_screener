import os
import subprocess
import sys
from pathlib import Path


def run_git(args, repo_root):
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )


def git_push_shortcut(commit_message):
    repo_root = Path(__file__).resolve().parent

    if os.getenv("GITHUB_ACTIONS") == "true":
        actor = os.getenv("GITHUB_ACTOR", "github-actions[bot]")
        run_git(["config", "user.name", actor], repo_root)
        run_git(["config", "user.email", f"{actor}@users.noreply.github.com"], repo_root)

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    if not status.strip():
        print("No changes to commit.")
        return

    try:
        run_git(["add", "-A"], repo_root)
        run_git(["commit", "-m", commit_message], repo_root)
        run_git(["push"], repo_root)
        print("🚀 Successfully staged, committed, and pushed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during Git operation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "automated commit from script"
    git_push_shortcut(msg)