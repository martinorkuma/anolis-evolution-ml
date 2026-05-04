#!/usr/bin/env bash
# Verify that the Anolis dataset zip has been manually downloaded and placed at the expected path.

set -euo pipefail

CONFIG="${CONFIG:-configs/dataset.yaml}"

# Pull the expected zip path from the config so it stays the single source of truth.
RAW_ZIP=$(python3 -c "
import yaml
with open('${CONFIG}') as f:
    cfg = yaml.safe_load(f)
print(cfg['data']['raw_zip'])
")

DATASET_URL="https://datadryad.org/dataset/doi:10.5061/dryad.9g182"

if [ ! -f "$RAW_ZIP" ]; then
    cat >&2 <<EOF
ERROR: Dataset zip not found at: $RAW_ZIP

This pipeline expects you to download the dataset manually,
because Dryad blocks automated downloads.

To get the data:
  1. Open the dataset page in a browser:
       $DATASET_URL
  2. Click "Download dataset" to get the zip.
  3. Move the downloaded file to:
       $RAW_ZIP
     (rename it if the downloaded filename differs)
  4. Re-run the pipeline.
EOF
    exit 1
fi

if ! file "$RAW_ZIP" | grep -q "Zip archive"; then
    echo "ERROR: $RAW_ZIP exists but is not a valid zip archive." >&2
    echo "Detected type: $(file -b "$RAW_ZIP")" >&2
    echo "Re-download from $DATASET_URL and try again." >&2
    exit 1
fi

echo "Found valid dataset zip: $RAW_ZIP ($(du -h "$RAW_ZIP" | cut -f1))"
