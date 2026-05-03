bash
#!/usr/bin/env bash
set -euo pipefail

CONFIG="configs/dataset.yaml"
LOG_DIR="outputs/logs"
mkdir -p "$LOG_DIR"

echo "[1/4] Downloading data..."
bash scripts/download_data.sh 2>&1 | tee "$LOG_DIR/01_download.log"

echo "[2/4] Ingesting data..."
python src/ingest.py --config "$CONFIG" 2>&1 | tee "$LOG_DIR/02_ingest.log"

echo "[3/4] Cleaning data..."
python src/clean.py --config "$CONFIG" 2>&1 | tee "$LOG_DIR/03_clean.log"

echo "[4/4] Training model..."
python src/train.py --config "$CONFIG" 2>&1 | tee "$LOG_DIR/04_train.log"

echo "Pipeline complete."
