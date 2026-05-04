# Data cleaning: load raw morphology data, clean, and save processed CSV.

from pathlib import Path
import argparse
import pandas as pd
import yaml


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _try_read(path: Path, sep: str, nrows=None) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(path, sep=sep, nrows=nrows, engine="python")
        if df.shape[1] > 1:
            return df
    except Exception:
        return None
    return None


def find_morphology_csv(manifest_csv: Path) -> tuple[Path, str]:
    """Pick the best candidate tabular file containing morphology + ecomorph."""
    if not manifest_csv.exists():
        raise FileNotFoundError(
            f"Missing manifest: {manifest_csv}\nRun src/ingest.py first."
        )

    manifest = pd.read_csv(manifest_csv)
    tabular = manifest[manifest["suffix"].isin([".csv", ".tsv", ".txt"])]

    if tabular.empty:
        raise FileNotFoundError("No CSV/TSV/TXT files found in extracted data.")

    candidates = []
    for _, row in tabular.iterrows():
        path = Path(row["relative_path"])
        for sep in [",", "\t", ";"]:
            df = _try_read(path, sep, nrows=5)
            if df is not None:
                cols_lower = [c.strip().lower() for c in df.columns]
                has_ecomorph = any(
                    "ecomorph" in c or "ecotype" in c for c in cols_lower
                )
                n_numeric = sum(
                    pd.api.types.is_numeric_dtype(df[c]) for c in df.columns
                )
                candidates.append({
                    "path": path,
                    "sep": sep,
                    "has_ecomorph": int(has_ecomorph),
                    "n_numeric": n_numeric,
                    "size_bytes": int(row["size_bytes"]),
                })
                break

    if not candidates:
        raise ValueError("Could not parse any tabular files in extracted data.")

    # Rank: ecomorph column first, then most numeric trait cols, then largest file
    candidates.sort(
        key=lambda c: (c["has_ecomorph"], c["n_numeric"], c["size_bytes"]),
        reverse=True,
    )
    best = candidates[0]
    print(f"Selected source file: {best['path']} (sep='{best['sep']}')")
    return best["path"], best["sep"]


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize columns, drop empties, drop rows missing the target label."""
    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Drop fully-empty rows / cols
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")

    # Strip whitespace from string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # Locate target column and rename to canonical 'ecomorph'
    target_candidates = [c for c in df.columns if "ecomorph" in c or "ecotype" in c]
    if target_candidates:
        target_col = target_candidates[0]
        before = len(df)
        df = df[df[target_col].notna() & (df[target_col].str.lower() != "nan")]
        print(f"Dropped {before - len(df)} rows missing '{target_col}'.")
        if target_col != "ecomorph":
            df = df.rename(columns={target_col: "ecomorph"})
    else:
        print("Warning: no ecomorph/ecotype column found — train.py will fall back to its candidate list.")

    return df.reset_index(drop=True)


def main(config_path: str) -> None:
    cfg = load_config(config_path)

    manifest_csv = Path(cfg["data"]["manifest_csv"])
    cleaned_csv = Path(cfg["data"]["cleaned_csv"])

    src_path, sep = find_morphology_csv(manifest_csv)

    df = pd.read_csv(src_path, sep=sep, engine="python")
    print(f"Loaded raw data: {df.shape[0]} rows x {df.shape[1]} cols")

    cleaned = clean_dataframe(df)
    print(f"Cleaned data:    {cleaned.shape[0]} rows x {cleaned.shape[1]} cols")

    cleaned_csv.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(cleaned_csv, index=False)
    print(f"Wrote cleaned data: {cleaned_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/dataset.yaml")
    args = parser.parse_args()
    main(args.config)