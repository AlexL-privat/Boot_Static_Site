#!/usr/bin/env bash
# Build script — generate site for production using repo base path
set -euo pipefail

# Replace with your repository name (folder name used as basepath)
REPO_NAME="Boot_Static_Site"

python3 src/main.py "/${REPO_NAME}/"
