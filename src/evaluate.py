from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay, precision_recall_curve

from .features import FEATURES, TARGET
from .metrics import classification_metrics, random_scores_at_contact_count, threshold_table

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "reports" / "results"
FIGURES_DIR = ROOT / "reports" / "figures"
LOCK_PATH = RESULTS_DIR / "final_test.lock"


def plot_results(y_true, probability, threshold: float) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    PrecisionRecallDisplay.from_predictions(y_true, probability, ax=ax, color="#0f766e")
    ax.set_title("Precision–Recall trên tập kiểm thử độc lập")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "test_precision_recall.png", dpi=180)
    plt.close(fig)

    prediction = (probability >= threshold).astype(int)
    fig, ax = plt.subplots(figsize=(5.6, 4.8))
    ConfusionMatrixDisplay.from_predictions(
        y_true, prediction, display_labels=["Không", "Có"], cmap="Blues", colorbar=False, ax=ax
    )
    ax.set_title(f"Ma trận nhầm lẫn trên test, ngưỡng {threshold:.2f}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "test_confusion_matrix.png", dpi=180)
    plt.close(fig)

    precision, recall, thresholds = precision_recall_curve(y_true, probability)
    curve = pd.DataFrame(
        {"threshold": np.r_[thresholds, np.nan], "precision": precision, "recall": recall}
    )
    curve.to_csv(RESULTS_DIR / "test_precision_recall_curve.csv", index=False)


def error_analysis(frame: pd.DataFrame, y_true, probability, threshold: float) -> pd.DataFrame:
    analyzed = frame[["age", "job"]].copy()
    analyzed["actual"] = np.asarray(y_true)
    analyzed["probability"] = np.asarray(probability)
    analyzed["predicted"] = (np.asarray(probability) >= threshold).astype(int)
    analyzed["age_group"] = pd.cut(
        analyzed["age"], bins=[0, 29, 39, 49, 59, 200], labels=["<30", "30-39", "40-49", "50-59", "60+"]
    )
    rows = []
    for dimension in ["age_group", "job"]:
        for value, part in analyzed.groupby(dimension, observed=True):
            if len(part) < 20:
                continue
            m = classification_metrics(part["actual"], part["probability"], threshold)
            rows.append(
                {
                    "dimension": dimension,
                    "group": str(value),
                    "n": len(part),
                    "positive_rate": float(part["actual"].mean()),
                    **m,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Cho phép tái tạo có chủ đích kết quả test.")
    args = parser.parse_args()
    if LOCK_PATH.exists() and not args.force:
        raise RuntimeError(
            "Tập test đã được đánh giá. Không chạy lại để tránh điều chỉnh theo test. "
            "Chỉ dùng --force khi tái tạo có chủ đích."
        )
    artifact_path = MODELS_DIR / "bank_marketing_pipeline.joblib"
    if not artifact_path.exists():
        raise FileNotFoundError("Chưa có model. Chạy: python -m src.train")
    test_path = PROCESSED_DIR / "test.csv"
    if not test_path.exists():
        raise FileNotFoundError("Chưa có split test. Chạy: python -m src.data --download")

    artifact = joblib.load(artifact_path)
    test_frame = pd.read_csv(test_path)
    X_test = test_frame[FEATURES]
    y_test = (test_frame[TARGET] == "yes").astype(int)
    probability = artifact["pipeline"].predict_proba(X_test)[:, 1]
    threshold = float(artifact["threshold"])

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    selected = classification_metrics(y_test, probability, threshold)
    fixed_thresholds = sorted(set([0.2, 0.3, 0.5, threshold]))
    threshold_results = threshold_table(y_test, probability, fixed_thresholds)
    threshold_results.to_csv(RESULTS_DIR / "test_thresholds.csv", index=False)

    selected_contact_count = int((probability >= threshold).sum())
    random_probability, random_threshold = random_scores_at_contact_count(
        len(y_test), selected_contact_count, int(artifact["random_state"])
    )
    all_negative = classification_metrics(y_test, np.zeros(len(y_test)), 0.5)
    all_negative["pr_auc"] = float("nan")
    baselines = pd.DataFrame(
        [
            {"candidate": "all_negative", **all_negative},
            {"candidate": "random_equal_contact_rate", **classification_metrics(y_test, random_probability, random_threshold)},
            {"candidate": artifact["selected_candidate"], **selected},
        ]
    )
    baselines.to_csv(RESULTS_DIR / "test_model_comparison.csv", index=False)
    groups = error_analysis(test_frame, y_test, probability, threshold)
    groups.to_csv(RESULTS_DIR / "test_error_analysis.csv", index=False)
    plot_results(y_test, probability, threshold)

    final = {
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evaluation_mode": (
            "intentional_reproduction_after_metric_code_correction"
            if args.force
            else "first_final_evaluation"
        ),
        "test_used_for_model_or_threshold_selection": False,
        "test_rows": len(X_test),
        "test_positive_rate": float(y_test.mean()),
        "selected_candidate": artifact["selected_candidate"],
        "selected_threshold_frozen_on_validation": threshold,
        "metrics": selected,
        "warning": "Kết quả test chỉ dùng để kết luận, không dùng chọn lại mô hình hoặc ngưỡng.",
    }
    (RESULTS_DIR / "final_test_metrics.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    LOCK_PATH.write_text(final["evaluated_at_utc"], encoding="utf-8")
    metadata_path = MODELS_DIR / "model_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["test_accessed"] = True
    metadata["test_accessed_at_utc"] = final["evaluated_at_utc"]
    metadata["test_evaluation_mode"] = final["evaluation_mode"]
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(final, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
