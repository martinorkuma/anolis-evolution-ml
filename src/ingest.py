# Script to ingest data into the pipeline

from pathlib import Path
import argparse
import pandas as pd
import yaml


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def build_manifest(raw_dir: Path, manifest_csv: Path) -> None:
    files = []
    for path in raw_dir.rglob("*"):
        if path.is_file():
            files.append({
                "file_name": path.name,
                "relative_path": str(path),
                "suffix": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
            })

    manifest = pd.DataFrame(files)
    manifest_csv.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(manifest_csv, index=False)
    print(f"Wrote manifest: {manifest_csv} ({len(manifest)} files)")


def main(config_path: str) -> None:
    cfg = load_config(config_path)
    raw_dir = Path(cfg["data"]["raw_dir"])           # add this key to dataset.yaml
    manifest_csv = Path(cfg["data"]["manifest_csv"])

    if not raw_dir.exists() or not any(raw_dir.iterdir()):
        raise FileNotFoundError(
            f"No files in {raw_dir}. Run scripts/download_data.sh first."
        )
    build_manifest(raw_dir, manifest_csv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/dataset.yaml")
    args = parser.parse_args()
    main(args.config)