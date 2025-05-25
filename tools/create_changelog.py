import argparse
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()

parser = argparse.ArgumentParser(description="Generate changelog for the release")
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Generate the changelog but don't write it to the file",
)
args = parser.parse_args()

CHANGELOG_FILE = ROOT_DIR / "CHANGELOG.md"
INNER_DESC = """A fork/modified version of [unrar-cffi](https://pypi.org/project/unrar-cffi/) that supports modern Python starting from 3.9+
This build also target unrar 7.x instead of unrar 5.x from the original unrar-cffi project.

Install with `pip3 install -U unrar2-cffi=={version}`

## Changes
"""  # noqa: E501

# ref/tags/v1.0.0
GIT_TAGS = os.getenv("VERSION")
if not GIT_TAGS:
    raise ValueError("No git tags found")

# v1.0.0
if not GIT_TAGS.startswith("refs/tags/"):
    raise ValueError("Invalid git tag format")

VERSION = GIT_TAGS.split("/")[-1]

if VERSION.startswith("v"):
    VERSION = VERSION[1:]

EXTRACTED_CHANGELOG = ""
START = False
for line in CHANGELOG_FILE.read_text().splitlines():
    if line.startswith("## [") and START:
        break
    if line.startswith(f"## [{VERSION}]"):
        line = INNER_DESC
        START = True

    if START:
        EXTRACTED_CHANGELOG += line + "\n"

EXTRACTED_CHANGELOG = EXTRACTED_CHANGELOG.strip()

# Write into CHANGELOG-GENERATED.md
if not EXTRACTED_CHANGELOG:
    EXTRACTED_CHANGELOG = f"{INNER_DESC}\n\nNo changelog found for version {VERSION}"

EXTRACTED_CHANGELOG = EXTRACTED_CHANGELOG.format(version=VERSION)
if args.dry_run:
    print(EXTRACTED_CHANGELOG)
    sys.exit(0)
CHANGELOG_GENERATED_FILE = ROOT_DIR / "CHANGELOG-GENERATED.md"
CHANGELOG_GENERATED_FILE.write_text(EXTRACTED_CHANGELOG)
