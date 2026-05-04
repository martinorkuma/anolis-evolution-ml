#!/usr/bin/env bash
# Script to download Anolis data

set -euo pipefail

ARTICLE_ID=4587259
RAW_DIR="data/raw"
mkdir -p "$RAW_DIR"

echo "[1/2] Fetching file list from Figshare API..."
META=$(curl -sSL "https://api.figshare.com/v2/articles/${ARTICLE_ID}")

# Parse out (download_url, name) pairs
mapfile -t FILES < <(echo "$META" | python3 -c "
import json, sys
for f in json.load(sys.stdin)['files']:
    print(f\"{f['download_url']}\t{f['name']}\")
")

echo "Found ${#FILES[@]} files."

echo "[2/2] Downloading files..."
for entry in "${FILES[@]}"; do
    url="${entry%%$'\t'*}"
    name="${entry##*$'\t'}"
    echo " -> $name"
    curl -sSL --retry 5 --retry-delay 3 -o "$RAW_DIR/$name" "$url"
done

echo "Done."
ls -lh "$RAW_DIR"