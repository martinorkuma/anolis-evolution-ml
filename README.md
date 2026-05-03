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
