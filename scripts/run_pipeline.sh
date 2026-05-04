#!/usr/bin/env bash
set -euo pipefail

EXPECTED_ENV="anolis-evolution-ml"

if [[ "${CONDA_DEFAULT_ENV:-}" != "$EXPECTED_ENV" ]]; then
    echo "ERROR: conda env '$EXPECTED_ENV' is not active." >&2
    echo "Activate it first, then re-run:" >&2
    echo "    conda activate $EXPECTED_ENV" >&2
    echo "    bash scripts/run_pipeline.sh" >&2
    exit 1
fi

echo "Using conda env: $CONDA_DEFAULT_ENV"
echo "Python: $(which python)"

CONFIG="configs/dataset.yaml"
LOG_DIR="outputs/logs"
mkdir -p "$LOG_DIR"

echo "[1/4] Verifying data..."
bash scripts/verify_data.sh 2>&1 | tee "$LOG_DIR/01_verify.log"

echo "[2/4] Ingesting data..."
python src/ingest.py --config "$CONFIG" 2>&1 | tee "$LOG_DIR/02_ingest.log"

echo "[3/4] Cleaning data..."
python src/clean.py --config "$CONFIG" 2>&1 | tee "$LOG_DIR/03_clean.log"

echo "[4/4] Training model..."
python src/train.py --config "$CONFIG" 2>&1 | tee "$LOG_DIR/04_train.log"

echo "Pipeline complete."
