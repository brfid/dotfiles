#!/opt/homebrew/bin/python3.11
import subprocess
import os
from pathlib import Path

# Load environment variables from your env file
env_path = Path("~/.config/shell/env").expanduser()
if env_path.exists():
    with env_path.open() as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

subprocess.run(
    ["/opt/homebrew/bin/python3.11", os.path.join(os.path.dirname(__file__), "push_config.py")]
)

# Add additional sync scripts here, e.g.:
# subprocess.run(["/opt/homebrew/bin/python3.11", os.path.expanduser("~/your-project/sync_script.py")])
