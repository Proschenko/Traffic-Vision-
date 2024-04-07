from os.path import dirname
from pathlib import Path
import subprocess

if __name__ == "__main__":
    folder = Path(dirname(__file__))
    for file in ("run_bot.py", "run_tracker.py"):
        path = str(folder / file)
        subprocess.Popen(["python", path])
