from __future__ import annotations

import argparse
import hashlib
import io
import json
import platform
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from .features import FEATURES, LEAKAGE_FEATURES, TARGET

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
ZIP_PATH = RAW_DIR / "bank.zip"
CSV_PATH = RAW_DIR / "bank-full.csv"
DOWNLOAD_URL = "https://archive.ics.uci.edu/static/public/222/bank%2Bmarketing.zip"
EXPECTED_COLUMNS = FEATURES + LEAKAGE_FEATURES + [TARGET]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_data(force: bool = False) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if force or not ZIP_PATH.exists():
        urllib.request.urlretrieve(DOWNLOAD_URL, ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH) as outer:
        direct_member = next((name for name in outer.namelist() if name.endswith("bank-full.csv")), None)
        if direct_member is not None:
            csv_bytes = outer.read(direct_member)
        elif "bank.zip" in outer.namelist():
            with zipfile.ZipFile(io.BytesIO(outer.read("bank.zip"))) as inner:
                member = next((name for name in inner.namelist() if name.endswith("bank-full.csv")), None)
                if member is None:
                    raise RuntimeError("Không tìm thấy bank-full.csv trong gói bank.zip lồng nhau.")
                csv_bytes = inner.read(member)
        else:
            raise RuntimeError("Không tìm thấy bank-full.csv trong gói dữ liệu UCI.")
        if force or not CSV_PATH.exists():
            CSV_PATH.write_bytes(csv_bytes)
    return CSV_PATH


def load_raw() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError("Chưa có dữ liệu. Chạy: python -m src.data --download")
    frame = pd.read_csv(CSV_PATH, sep=";")
    missing = sorted(set(EXPECTED_COLUMNS) - set(frame.columns))
    extra = sorted(set(frame.columns) - set(EXPECTED_COLUMNS))
    if missing or extra:
        raise ValueError(f"Schema không hợp lệ. Thiếu={missing}, thừa={extra}")
    if len(frame) != 45_211:
        raise ValueError(f"Số dòng không đúng bản bank-full: {len(frame)}")
    if not set(frame[TARGET].unique()).issubset({"yes", "no"}):
        raise ValueError("Target y phải chỉ gồm yes/no.")
    return frame


def create_splits(frame: pd.DataFrame, random_state: int = 42) -> dict[str, pd.DataFrame]:
    train, remainder = train_test_split(
        frame, test_size=0.4, stratify=frame[TARGET], random_state=random_state
    )
    validation, test = train_test_split(
        remainder, test_size=0.5, stratify=remainder[TARGET], random_state=random_state
    )
    return {"train": train.copy(), "validation": validation.copy(), "test": test.copy()}


def save_splits(splits: dict[str, pd.DataFrame]) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in splits.items():
        frame.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)


def build_quality_report(frame: pd.DataFrame, splits: dict[str, pd.DataFrame]) -> dict:
    unknown_counts = {
        column: int((frame[column].astype(str).str.lower() == "unknown").sum())
        for column in frame.select_dtypes(include="object").columns
        if column != TARGET
    }
    return {
        "rows": len(frame),
        "columns": len(frame.columns),
        "null_cells": int(frame.isna().sum().sum()),
        "exact_duplicate_rows": int(frame.duplicated().sum()),
        "rows_removed": 0,
        "removal_reasons": [],
        "target_counts": frame[TARGET].value_counts().to_dict(),
        "target_positive_rate": float((frame[TARGET] == "yes").mean()),
        "unknown_counts": unknown_counts,
        "numeric_ranges": {
            column: {"min": float(frame[column].min()), "max": float(frame[column].max())}
            for column in frame.select_dtypes(include="number").columns
        },
        "outlier_policy": "Không tự động loại theo miền số; giữ dữ liệu gốc và báo min/max để tránh xóa trường hợp hợp lệ hiếm.",
        "split_rows": {name: len(part) for name, part in splits.items()},
        "split_positive_rate": {
            name: float((part[TARGET] == "yes").mean()) for name, part in splits.items()
        },
    }


def write_manifest(frame: pd.DataFrame, splits: dict[str, pd.DataFrame]) -> None:
    manifest = {
        "source_url": DOWNLOAD_URL,
        "source_doi": "10.24432/C5K306",
        "license": "CC BY 4.0",
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "zip_sha256": sha256(ZIP_PATH),
        "csv_sha256": sha256(CSV_PATH),
        "python": sys.version,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "quality": build_quality_report(frame, splits),
        "leakage_excluded": LEAKAGE_FEATURES,
    }
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "data_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Tải dữ liệu từ UCI nếu chưa có.")
    parser.add_argument("--force-download", action="store_true")
    args = parser.parse_args()
    if args.download or args.force_download:
        download_data(force=args.force_download)
    frame = load_raw()
    splits = create_splits(frame)
    save_splits(splits)
    write_manifest(frame, splits)
    quality = build_quality_report(frame, splits)
    print(json.dumps(quality, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
