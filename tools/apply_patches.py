import subprocess as sp
from pathlib import Path

ROOT_DIR = Path(__file__).absolute().parent.parent

PATCH_FOLDER = ROOT_DIR / "patches"

for patches in PATCH_FOLDER.glob("*.patch"):
    sp.run(["git", "apply", str(patches)])
