from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .features import TARGET
from .metrics import classification_metrics, random_scores_at_contact_count

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
RESULTS_DIR = ROOT / "reports" / "results"
CONFIG_PATH = ROOT / "config" / "config.json"


def main() -> None:
    train_path = PROCESSED_DIR / "train.csv"
    validation_path = PROCESSED_DIR / "validation.csv"
    if not train_path.exists() or not validation_path.exists():
        raise FileNotFoundError("Chưa có split. Chạy bước dữ liệu của tuần 2 trước.")

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    seed = int(config["random_state"])
    train = pd.read_csv(train_path)
    validation = pd.read_csv(validation_path)
    y_validation = (validation[TARGET] == "yes").astype(int)
    positive_rate = float((train[TARGET] == "yes").mean())
    contact_count = round(len(validation) * positive_rate)
    random_probability, random_threshold = random_scores_at_contact_count(
        len(validation), contact_count, seed
    )

    all_negative = classification_metrics(y_validation, np.zeros(len(validation)), 0.5)
    all_negative["pr_auc"] = float("nan")
    rows = [
        {"candidate": "all_negative", **all_negative},
        {
            "candidate": "random_at_train_prevalence_contact_rate",
            **classification_metrics(y_validation, random_probability, random_threshold),
        },
    ]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = RESULTS_DIR / "week2_validation_baselines.csv"
    pd.DataFrame(rows).to_csv(output, index=False)
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"\nĐã lưu baseline tuần 2: {output}")


if __name__ == "__main__":
    main()
