# Data cleaning

from pathlib import Path
import argparse
import zipfile
import pandas as pd
import yaml


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def build_manifest(extract_dir: Path, manifest_csv: Path) -> None:
    files = []

    for path in extract_dir.rglob("*"):
        if path.is_file():
            files.append({
                "file_name": path.name,
                "relative_path": str(path),
                "suffix": path.suffix.lower(),
                "size_bytes": path.stat().st_size
            })

    manifest = pd.DataFrame(files)
    manifest_csv.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(manifest_csv, index=False)

    print(f"Wrote manifest: {manifest_csv}")
    print(f"Files found: {len(manifest)}")


def extract_zip(raw_zip: Path, extract_dir: Path) -> None:
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(raw_zip, "r") as z:
        z.extractall(extract_dir)

    print(f"Extracted: {raw_zip} -> {extract_dir}")


def main(config_path: str) -> None:
    cfg = load_config(config_path)

    raw_zip = Path(cfg["data"]["raw_zip"])
    extract_dir = Path(cfg["data"]["extract_dir"])
    manifest_csv = Path(cfg["data"]["manifest_csv"])

    if not raw_zip.exists():
        raise FileNotFoundError(
            f"Missing raw zip: {raw_zip}\n"
            "Run scripts/download_data.sh first."
        )

    extract_zip(raw_zip, extract_dir)
    build_manifest(extract_dir, manifest_csv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/dataset.yaml")
    args = parser.parse_args()

    main(args.config)
