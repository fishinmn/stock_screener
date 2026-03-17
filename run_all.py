import subprocess
import sys
from pathlib import Path

scripts = [
#    "fundamentals_screener_all_caps.py",
#    "merge_fundamentals_only.py",
#    "algo10_data_all.py",
#    "compare_ps_adj_decreases.py",
    "publish_json_holds_all.py"
]

base_path = Path(__file__).parent

for script in scripts:
    script_path = base_path / script
    print(f"\n{'='*60}")
    print(f"Running: {script}")
    print(f"{'='*60}\n")
    
    result = subprocess.run([sys.executable, str(script_path)], check=False)
    
    if result.returncode != 0:
        print(f"\n❌ ERROR: {script} failed with return code {result.returncode}")
        sys.exit(1)
    
    print(f"\n✓ Completed: {script}")

print(f"\n{'='*60}")
print("✓ All scripts completed successfully!")
print(f"{'='*60}")