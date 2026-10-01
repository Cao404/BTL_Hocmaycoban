from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    auc,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)


def pr_auc_score(y_true, probability) -> float:
    """Tính diện tích hình thang dưới đường Precision–Recall."""
    precision, recall, _ = precision_recall_curve(y_true, probability)
    return float(auc(recall, precision))


def classification_metrics(y_true, probability, threshold: float) -> dict[str, float | int]:
    probability = np.asarray(probability, dtype=float)
    prediction = (probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    try:
        roc_auc = float(roc_auc_score(y_true, probability))
    except ValueError:
        roc_auc = float("nan")
    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, prediction)),
        "precision": float(precision_score(y_true, prediction, zero_division=0)),
        "recall": float(recall_score(y_true, prediction, zero_division=0)),
        "f1": float(f1_score(y_true, prediction, zero_division=0)),
        "average_precision": float(average_precision_score(y_true, probability)),
        "pr_auc": pr_auc_score(y_true, probability),
        "roc_auc": roc_auc,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "contact_rate": float(prediction.mean()),
    }


def random_scores_at_contact_count(
    row_count: int, contact_count: int, random_state: int
) -> tuple[np.ndarray, float]:
    """Tạo điểm ngẫu nhiên và ngưỡng gọi đúng số lượng khách hàng yêu cầu."""
    if not 0 <= contact_count <= row_count:
        raise ValueError("contact_count phải nằm trong [0, row_count].")
    scores = np.random.default_rng(random_state).random(row_count)
    if contact_count == 0:
        return scores, float(np.nextafter(scores.max(), np.inf))
    if contact_count == row_count:
        return scores, float(scores.min())
    threshold = float(np.partition(scores, row_count - contact_count)[row_count - contact_count])
    return scores, threshold


def threshold_table(y_true, probability, thresholds: Iterable[float]) -> pd.DataFrame:
    return pd.DataFrame([classification_metrics(y_true, probability, t) for t in thresholds])


def choose_threshold(table: pd.DataFrame, minimum_recall: float) -> float:
    eligible = table.loc[table["recall"] >= minimum_recall]
    candidate = eligible if not eligible.empty else table
    best = candidate.sort_values(["f1", "precision", "threshold"], ascending=[False, False, False]).iloc[0]
    return float(best["threshold"])
