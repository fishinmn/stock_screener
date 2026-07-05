import os
import subprocess
import sys
from pathlib import Path

scripts = [
    "get_earnings.py",
    "get_upcoming_earnings.py",
    "fundamentals_screener_recent_earnings.py",
    "prep_recent_earnings_data.py",
    "compare_ps_adj_recent_earnings.py",
    "publish_json_recent_earnings.py",
    "publish_json_upcoming_earnings.py",
    "git_push_script.py",
]

repo_root = Path(__file__).resolve().parent
env = os.environ.copy()
env["REPO_ROOT"] = str(repo_root)
pythonpath_entries = [str(repo_root), env.get("PYTHONPATH", "")]
env["PYTHONPATH"] = os.pathsep.join([entry for entry in pythonpath_entries if entry])

for script in scripts:
    script_path = repo_root / script
    print(f"\n{'=' * 60}")
    print(f"Running: {script}")
    print(f"{'=' * 60}\n")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=repo_root,
        env=env,
        check=False,
    )

    if result.returncode != 0:
        print(f"\n❌ ERROR: {script} failed with return code {result.returncode}")
        sys.exit(1)

    print(f"\n✓ Completed: {script}")

print(f"\n{'=' * 60}")
print("✓ All scripts completed successfully!")
print(f"{'=' * 60}")