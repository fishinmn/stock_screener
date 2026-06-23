import subprocess
import sys

def git_push_shortcut(commit_message):
    try:
        # 1. Stage all changes
        subprocess.run(["git", "add", "-A"], check=True)
        
        # 2. Commit with your message
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # 3. Push to remote repository
        subprocess.run(["git", "push"], check=True)
        
        print("🚀 Successfully staged, committed, and pushed!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during Git operation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Uses 'blah' as a default if no message is provided via command line
    msg = sys.argv[1] if len(sys.argv) > 1 else "automated commit from script"
    git_push_shortcut(msg)