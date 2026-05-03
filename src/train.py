# Machine Learning Script

# Load libraries
from pathlib import Path
import argparse
import json
import joblib
import pandas as pd
import yaml
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def infer_target_column(df: pd.DataFrame, preferred: str) -> str:
    if preferred in df.columns:
        return preferred

    candidates = ["ecomorph", "ecotype", "habitat", "island", "group"]

    for col in candidates:
        if col in df.columns:
            return col

    raise ValueError(
        f"Target column not found. Preferred target was '{preferred}'.\n"
        f"Available columns:\n{list(df.columns)}"
    )


def main(config_path: str) -> None:
    cfg = load_config(config_path)

    cleaned_csv = Path(cfg["data"]["cleaned_csv"])
    metrics_json = Path(cfg["outputs"]["metrics_json"])
    cm_png = Path(cfg["outputs"]["confusion_matrix_png"])
    model_path = Path(cfg["outputs"]["model_path"])

    target_preferred = cfg["model"]["target_column"]
    test_size = cfg["model"]["test_size"]
    random_state = cfg["model"]["random_state"]

    df = pd.read_csv(cleaned_csv)
    target_col = infer_target_column(df, target_preferred)

    y = df[target_col].astype(str)
    X = df.drop(columns=[target_col])

    # Keep usable predictors only
    X = X.drop(columns=[c for c in X.columns if X[c].nunique(dropna=True) <= 1])

    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()

    if len(numeric_cols) + len(categorical_cols) == 0:
        raise ValueError("No usable feature columns found.")

    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipe, numeric_cols),
        ("categorical", categorical_pipe, categorical_cols),
    ])

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=random_state,
        class_weight="balanced",
    )

    pipeline = Pipeline([
        ("preprocess", preprocessor),
        ("model", model),
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y if y.nunique() > 1 else None,
    )

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    metrics = {
        "target_column": target_col,
        "n_rows": int(df.shape[0]),
        "n_features": int(X.shape[1]),
        "n_classes": int(y.nunique()),
        "classes": sorted(y.unique().tolist()),
        "accuracy": float(accuracy_score(y_test, preds)),
        "macro_f1": float(f1_score(y_test, preds, average="macro")),
        "weighted_f1": float(f1_score(y_test, preds, average="weighted")),
        "classification_report": classification_report(y_test, preds, output_dict=True),
        "numeric_features": numeric_cols,
        "categorical_features": categorical_cols,
    }

    metrics_json.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_json, "w") as f:
        json.dump(metrics, f, indent=2)

    cm_png.parent.mkdir(parents=True, exist_ok=True)
    cm = confusion_matrix(y_test, preds, labels=sorted(y.unique()))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=sorted(y.unique()))
    disp.plot(xticks_rotation=45)
    plt.tight_layout()
    plt.savefig(cm_png, dpi=300)
    plt.close()

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)

    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"Macro F1: {metrics['macro_f1']:.3f}")
    print(f"Wrote metrics: {metrics_json}")
    print(f"Wrote confusion matrix: {cm_png}")
    print(f"Wrote model: {model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/dataset.yaml")
    args = parser.parse_args()

    main(args.config)