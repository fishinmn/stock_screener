import os
import subprocess
import sys
from pathlib import Path

scripts = [
    "fundamentals_screener_all_caps.py",
    "merge_fundamentals_only.py",
    "algo10_data_all.py",
    "compare_ps_adj_decreases.py",
    "publish_json_holds_all.py",
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