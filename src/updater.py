import subprocess
import sys
import os
from logger import logger

def run_self_update():
    """Pulls latest changes from origin main and runs installer."""
    print("\n[vicious] Checking for updates on GitHub...")
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    try:
        # Fetch and pull latest changes
        logger.info("Executing git pull origin main...")
        pull_result = subprocess.run(
            ["git", "-C", project_dir, "pull", "origin", "main"],
            capture_output=True,
            text=True,
            check=True
        )
        print(pull_result.stdout)

        # Run install.sh to apply any new setup changes
        install_script = os.path.join(project_dir, "install.sh")
        if os.path.exists(install_script):
            print("[vicious] Refreshing local installation...")
            subprocess.run(["bash", install_script], check=True)

        print("\n✨ Vicious CLI updated successfully!")
        sys.exit(0)

    except subprocess.CalledProcessError as e:
        logger.error(f"Update failed: {e}")
        print(f"\n[Error] Update failed: {e.stderr if e.stderr else e}")
        sys.exit(1)
