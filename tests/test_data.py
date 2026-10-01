import pandas as pd
import numpy as np

from src.data import create_splits
from src.features import FEATURES, LEAKAGE_FEATURES
from src.metrics import classification_metrics, random_scores_at_contact_count


def test_duration_is_not_a_serving_feature():
    assert "duration" not in FEATURES
    assert LEAKAGE_FEATURES == ["duration"]


def test_split_is_disjoint_and_complete():
    frame = pd.DataFrame({"x": range(100), "y": ["yes", "no"] * 50})
    splits = create_splits(frame, random_state=42)
    indices = [set(part.index) for part in splits.values()]
    assert not (indices[0] & indices[1])
    assert not (indices[0] & indices[2])
    assert not (indices[1] & indices[2])
    assert sum(len(part) for part in splits.values()) == len(frame)


def test_random_baseline_uses_exact_contact_count():
    scores, threshold = random_scores_at_contact_count(100, 37, random_state=42)
    assert int((scores >= threshold).sum()) == 37


def test_metrics_report_pr_auc_separately_from_average_precision():
    metrics = classification_metrics(
        np.array([0, 0, 1, 1]), np.array([0.1, 0.4, 0.35, 0.8]), 0.5
    )
    assert "pr_auc" in metrics
    assert "average_precision" in metrics
    assert 0 <= metrics["pr_auc"] <= 1
