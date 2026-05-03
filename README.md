## Anolis Evolution ML

**End-to-End Biological Data Science Pipeline**

This project builds a reproducible machine learning pipeline to classify *Anolis* lizard ecological groups (ecomorphs) from morphological traits. Using publicly available morphology datasets from Figshare, the workflow covers data ingestion, validation, cleaning, feature engineering, model training, and evaluation.

The pipeline is fully automated via Bash and Python, producing versioned outputs (cleaned data, trained models, metrics, and figures). A Random Forest classifier is used as a baseline to quantify how well morphology predicts ecological adaptation, with results interpreted in an evolutionary context.

**Key components**

- Reproducible Bash-driven pipeline (`run_pipeline.sh`)
- Config-driven workflow (`configs/dataset.yaml`)
- Data validation + manifest generation
- Supervised ML (Random Forest)
- Metrics + confusion matrix outputs
- Clean repo structure for team or solo extension


**Goal**

Demonstrate an end-to-end biological data science workflow that connects phenotype → ecology using machine learning, in a format suitable for extension to comparative or evolutionary genomics projects.


## Pipeline Overview

This project uses a Bash-driven, Python-based pipeline for an end-to-end biological data science workflow. The pipeline downloads morphology data, validates the raw files, cleans and prepares the dataset, trains a baseline machine learning model, and saves evaluation outputs.

The workflow is organized into reproducible stages:

1. **Ingest data**
   - Downloads the source morphology dataset.
   - Saves raw input files under `data/raw/`.

2. **Validate data**
   - Checks that expected files exist.
   - Creates a raw data manifest.
   - Flags missing or malformed inputs.

3. **Prepare features**
   - Cleans the raw morphology table.
   - Selects relevant morphological traits.
   - Encodes the target label, such as ecomorph class.
   - Saves processed datasets under `data/processed/`.

4. **Train model**
   - Trains a baseline Random Forest classifier.
   - Uses morphology traits to predict Anolis ecological group/ecomorph.
   - Saves the trained model under `outputs/models/`.

5. **Evaluate model**
   - Generates model performance metrics.
   - Saves confusion matrix and summary outputs.
   - Writes results under `outputs/metrics/` and `outputs/figures/`.

## Repository Structure

```text
anolis-evolution-ml/
├── configs/
│   └── dataset.yaml
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
│   ├── figures/
│   ├── metrics/
│   └── models/
├── scripts/
│   ├── download_data.sh
│   └── run_pipeline.sh
├── src/
│   ├── validate_data.py
│   ├── prepare_features.py
│   ├── train_model.py
│   └── evaluate_model.py
├── environment.yml
└── README.md

