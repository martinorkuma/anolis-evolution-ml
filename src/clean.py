# Data cleaning: load raw morphology data, merge ecomorph labels, save processed CSV.

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
    """Pick the best candidate tabular file containing morphology traits."""
    if not manifest_csv.exists():
        raise FileNotFoundError(
            f"Missing manifest: {manifest_csv}\nRun src/ingest.py first."
        )

    manifest = pd.read_csv(manifest_csv)
    tabular = manifest[manifest["suffix"].isin([".csv", ".tsv", ".txt"])]

    # Exclude macOS resource-fork files (._*) that hide in archives zipped on Macs
    tabular = tabular[~tabular["file_name"].str.startswith("._")]

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

    # Rank: most numeric trait cols, then largest file
    candidates.sort(
        key=lambda c: (c["n_numeric"], c["size_bytes"]),
        reverse=True,
    )
    best = candidates[0]
    print(f"Selected morphology file: {best['path']} (sep='{best['sep']}')")
    return best["path"], best["sep"]


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize columns and drop empty rows/cols."""
    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Drop fully-empty rows / cols
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")

    # Strip whitespace from string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    return df.reset_index(drop=True)


def load_ecomorph_table(extract_dir: Path) -> pd.DataFrame:
    """Load the traditional ecomorph classification (no header in source file).

    Source file format: species,idx,ecomorph_code
    Ecomorph codes: CG (crown-giant), GB (grass-bush), TC (trunk-crown),
    TG (trunk-ground), TR (trunk), TW (twig), U (unique / unclassified).
    """
    ecomorph_path = (
        extract_dir / "Mahler_et_al_2013_Data" / "GA_Anolis_trad_ecomorph_class.csv"
    )
    if not ecomorph_path.exists():
        raise FileNotFoundError(
            f"Missing ecomorph classification file: {ecomorph_path}"
        )

    ecomorph_df = pd.read_csv(
        ecomorph_path,
        header=None,
        names=["species", "idx", "ecomorph"],
    )

    # Normalize whitespace in string columns
    for col in ["species", "ecomorph"]:
        ecomorph_df[col] = ecomorph_df[col].astype(str).str.strip()

    # Drop "unique" species — they're not part of any ecomorph class
    n_before = len(ecomorph_df)
    ecomorph_df = ecomorph_df[ecomorph_df["ecomorph"] != "U"].copy()
    print(
        f"Ecomorph table: {len(ecomorph_df)} classified species "
        f"({n_before - len(ecomorph_df)} 'U'/unique dropped)"
    )

    return ecomorph_df[["species", "ecomorph"]]


def main(config_path: str) -> None:
    cfg = load_config(config_path)

    manifest_csv = Path(cfg["data"]["manifest_csv"])
    cleaned_csv = Path(cfg["data"]["cleaned_csv"])
    extract_dir = Path(cfg["data"]["extract_dir"])

    # 1. Load + clean the morphology table
    src_path, sep = find_morphology_csv(manifest_csv)
    traits_df = pd.read_csv(src_path, sep=sep, engine="python")
    print(f"Loaded raw morphology: {traits_df.shape[0]} rows x {traits_df.shape[1]} cols")
    traits_df = clean_dataframe(traits_df)

    if "species" not in traits_df.columns:
        raise ValueError(
            f"No 'species' column in morphology file. Found: {list(traits_df.columns)}"
        )

    # 2. Load the ecomorph classification (separate file, no header)
    ecomorph_df = load_ecomorph_table(extract_dir)

    # 3. Inner-join on species — keep only rows with both traits and a label
    cleaned = traits_df.merge(ecomorph_df, on="species", how="inner")
    print(
        f"Merged: {len(cleaned)} rows "
        f"(traits had {len(traits_df)}, ecomorph had {len(ecomorph_df)})"
    )

    if cleaned.empty:
        raise ValueError(
            "Merge produced 0 rows. Check that species names match between "
            "the morphology and ecomorph tables."
        )

    # 4. Sanity check the class distribution before saving
    print("\nEcomorph class counts:")
    print(cleaned["ecomorph"].value_counts().to_string())

    cleaned_csv.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(cleaned_csv, index=False)
    print(f"\nWrote cleaned data: {cleaned_csv}")
    print(f"Final shape: {cleaned.shape[0]} rows x {cleaned.shape[1]} cols")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/dataset.yaml")
    args = parser.parse_args()
    main(args.config)