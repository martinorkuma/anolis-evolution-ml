## Anolis Evolution ML

**End-to-End Biological Data Science Pipeline**

This project builds a reproducible machine learning pipeline to classify Anolis lizard ecological groups (ecomorphs) from morphological traits. 
It uses the publicly available morphology dataset from Mahler et al. (2013), hosted on Dryad. 
The workflow covers data ingestion, validation, cleaning, feature engineering, model training, and evaluation.

The pipeline is config-driven and orchestrated by Bash and Python, producing versioned outputs (cleaned data, trained models, metrics, and figures). 
A Random Forest classifier is used as a baseline to quantify how well morphology predicts ecological adaptation, with results interpreted in an evolutionary context.

**Key components**

- Bash-orchestrated pipeline (`scripts/run_pipeline.sh`)
- Config-driven workflow (`configs/dataset.yaml`)
- Data verification + manifest generation
- Supervised ML (Random Forest)
- Metrics + confusion matrix outputs


**Goal**

Demonstrate an end-to-end biological data science workflow that connects phenotype → ecology using machine learning, in a format suitable for extension to comparative or evolutionary genomics projects.


### Quickstart 

```Bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Manually download the dataset (see "Get the Data" below) and place the zip at: data/raw/Mahler_et_al_2013_Data.zip

# 3. Run the full pipeline
bash scripts/run_pipeline.sh
```

### Get the Data

The dataset is not auto-downloaded. Dryad's file-download endpoint sits behind a JavaScript anti-bot challenge that command-line tools
(curl, wget) cannot bypass, so the pipeline expects the zip to be placed manually.

To get the data:

1. Open the dataset page in a browser: https://datadryad.org/dataset/doi:10.5061/dryad.9g182
2. Click Download dataset to get the zip.
3. Move the file to: data/raw/Mahler_et_al_2013_Data.zip (rename it if the downloaded filename differs)

`scripts/verify_data.sh` runs as the first pipeline step and will fail fast with these instructions if the zip is missing or malformed.


### Pipeline Overview

The pipeline is organized into four reproducible stages, all driven by `scripts/run_pipeline.sh` and configured via `configs/dataset.yaml`. 
Each stage logs to `outputs/logs/`.

1. **Verify data** (`scripts/verify_data.sh`)
   - Confirms the manually-downloaded dataset zip exists at the configured path.
   - Validates that the file is a real zip archive (not a stray HTML challenge page).
   - Fails fast with download instructions if anything is wrong. 

2. Ingest data (`src/ingest.py`)
   - Extracts the raw zip to `data/raw/Mahler_et_al_2013_Data/`.
   - Walks the extracted tree and writes a manifest of every file (name, path, type, size) to `data/interim/manifest.csv`.

3. Clean data (`src/clean.py`)
   - Loads the relevant raw morphology table from the extracted dataset.
   - Selects morphological trait columns and encodes the ecomorph label.
   - Writes the modeling-ready table to `data/processed/anolis_cleaned.csv`.

4. Train and evaluate model (`src/train.py`)

   - Splits the cleaned data into train/test sets.
   - Builds a ColumnTransformer + Random Forest pipeline (median imputation + scaling for numerics, mode imputation + one-hot for categoricals).
   - Saves the fitted pipeline to outputs/models/random_forest_anolis.joblib.
   - Writes accuracy, macro/weighted F1, and a full classification report to outputs/metrics/model_metrics.json.
   - Saves a confusion matrix figure to outputs/figures/confusion_matrix.png.

### Repository Structure

```text
anolis-evolution-ml/
├── configs/
│   └── dataset.yaml
├── data/
│   ├── raw/              # input data (gitignored)
│   ├── interim/          # manifests, intermediate files (gitignored)
│   └── processed/        # cleaned modeling tables (gitignored)
├── outputs/
│   ├── figures/          # confusion matrix, plots
│   ├── logs/             # per-stage stdout/stderr
│   ├── metrics/          # model_metrics.json
│   └── models/           # serialized .joblib pipelines
├── scripts/
│   ├── verify_data.sh    # checks manual download is in place
│   └── run_pipeline.sh   # orchestrates all four stages
├── src/
│   ├── ingest.py         # unzip + manifest
│   ├── clean.py          # build modeling-ready CSV
│   └── train.py          # train + evaluate + serialize
├── requirements.txt
├── LICENSE
└── README.md
```

### References

Mahler, D. L., Ingram, T., Revell, L. J., & Losos, J. B. (2013). 
Exceptional convergence on the macroevolutionary landscape in island lizard radiations. Science, 341(6143), 292–295. 
https://doi.org/10.1126/science.1232392

Data package: https://doi.org/10.5061/dryad.9g182

### License

This project is released under the Apache License 2.0. See `LICENSE` for the full text.