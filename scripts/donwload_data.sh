bash
#!/usr/bin/env bash
set -euo pipefail

CONFIG="configs/dataset.yaml"
RAW_DIR="data/raw"
RAW_ZIP="data/raw/anolis_figshare.zip"
URL="https://figshare.com/ndownloader/articles/4587259/versions/1"

mkdir -p "$RAW_DIR"

echo "[1/1] Downloading Anolis Figshare dataset..."
wget -O "$RAW_ZIP" "$URL"

echo "Saved to: $RAW_ZIP"