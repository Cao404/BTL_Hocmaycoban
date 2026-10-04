from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from .eda import save_eda_figures
from .features import FEATURES, TARGET, build_preprocessor
from .metrics import (
    classification_metrics,
    choose_threshold,
    random_scores_at_contact_count,
    threshold_table,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "config.json"
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "reports" / "results"


def load_split(name: str) -> tuple[pd.DataFrame, pd.Series]:
    path = PROCESSED_DIR / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError("Chưa có split. Chạy: python -m src.data --download")
    frame = pd.read_csv(path)
    return frame[FEATURES], (frame[TARGET] == "yes").astype(int)


def make_pipeline(estimator) -> Pipeline:
    return Pipeline([("preprocessor", build_preprocessor()), ("model", estimator)])


def cross_validate_selected_model(
    pipeline: Pipeline, X: pd.DataFrame, y: pd.Series, folds: int, seed: int
) -> tuple[pd.DataFrame, dict]:
    """Đo độ biến thiên của mô hình đã chọn chỉ trên tập train."""
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    rows: list[dict] = []
    for fold, (fit_index, score_index) in enumerate(splitter.split(X, y), start=1):
        candidate = clone(pipeline)
        candidate.fit(X.iloc[fit_index], y.iloc[fit_index])
        probability = candidate.predict_proba(X.iloc[score_index])[:, 1]
        metrics = classification_metrics(y.iloc[score_index], probability, 0.5)
        rows.append(
            {
                "fold": fold,
                "rows": len(score_index),
                "positive_rate": float(y.iloc[score_index].mean()),
                "pr_auc": metrics["pr_auc"],
                "average_precision": metrics["average_precision"],
                "roc_auc": metrics["roc_auc"],
            }
        )
    frame = pd.DataFrame(rows)
    summary = {
        "folds": folds,
        "scope": "train_only",
        "purpose": "Độ biến thiên của mô hình đã chọn; không dùng test.",
        "pr_auc_mean": float(frame["pr_auc"].mean()),
        "pr_auc_std": float(frame["pr_auc"].std(ddof=1)),
        "average_precision_mean": float(frame["average_precision"].mean()),
        "average_precision_std": float(frame["average_precision"].std(ddof=1)),
        "roc_auc_mean": float(frame["roc_auc"].mean()),
        "roc_auc_std": float(frame["roc_auc"].std(ddof=1)),
    }
    return frame, summary


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    seed = int(config["random_state"])
    selection = config["model_selection"]
    X_train, y_train = load_split("train")
    X_validation, y_validation = load_split("validation")
    train_frame = pd.read_csv(PROCESSED_DIR / "train.csv")
    save_eda_figures(train_frame)

    candidates: list[dict] = []
    fitted: dict[str, Pipeline] = {}
    for class_weight in selection["class_weights"]:
        for c_value in selection["c_values"]:
            name = f"logistic_C={c_value}_weight={class_weight or 'none'}"
            pipeline = make_pipeline(
                LogisticRegression(
                    C=float(c_value),
                    class_weight=class_weight,
                    max_iter=2_000,
                    solver="liblinear",
                    random_state=seed,
                )
            )
            pipeline.fit(X_train, y_train)
            probability = pipeline.predict_proba(X_validation)[:, 1]
            row = {"candidate": name, "family": "logistic_regression"}
            row.update(classification_metrics(y_validation, probability, 0.5))
            candidates.append(row)
            fitted[name] = pipeline

    tree_name = "decision_tree_depth=4"
    tree = make_pipeline(
        DecisionTreeClassifier(max_depth=4, min_samples_leaf=50, class_weight="balanced", random_state=seed)
    )
    tree.fit(X_train, y_train)
    tree_probability = tree.predict_proba(X_validation)[:, 1]
    tree_row = {"candidate": tree_name, "family": "decision_tree"}
    tree_row.update(classification_metrics(y_validation, tree_probability, 0.5))
    candidates.append(tree_row)
    fitted[tree_name] = tree

    result_frame = pd.DataFrame(candidates).sort_values(
        [selection["primary_metric"], "f1"], ascending=False
    )
    selected_name = str(result_frame.iloc[0]["candidate"])
    selected_pipeline = fitted[selected_name]
    validation_probability = selected_pipeline.predict_proba(X_validation)[:, 1]
    thresholds = threshold_table(y_validation, validation_probability, selection["thresholds"])
    selected_threshold = choose_threshold(thresholds, float(selection["minimum_recall"]))

    cv_frame, cv_summary = cross_validate_selected_model(
        selected_pipeline,
        X_train,
        y_train,
        int(selection.get("cross_validation_folds", 5)),
        seed,
    )

    positive_rate = float(y_train.mean())
    selected_contact_count = int((validation_probability >= selected_threshold).sum())
    random_probability, random_threshold = random_scores_at_contact_count(
        len(y_validation), selected_contact_count, seed
    )
    all_negative = classification_metrics(y_validation, np.zeros(len(y_validation)), 0.5)
    all_negative["pr_auc"] = float("nan")
    baselines = [
        {"candidate": "all_negative", "family": "baseline", **all_negative},
        {"candidate": "random_equal_contact_rate", "family": "baseline", **classification_metrics(y_validation, random_probability, random_threshold)},
    ]

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "pipeline": selected_pipeline,
        "threshold": selected_threshold,
        "features": FEATURES,
        "target": TARGET,
        "selected_candidate": selected_name,
        "random_state": seed,
        "validation_primary_metric": selection["primary_metric"],
        "cross_validation": cv_summary,
    }
    joblib.dump(artifact, MODELS_DIR / "bank_marketing_pipeline.joblib")
    result_frame.to_csv(RESULTS_DIR / "validation_candidates.csv", index=False)
    thresholds.to_csv(RESULTS_DIR / "validation_thresholds.csv", index=False)
    pd.DataFrame(baselines).to_csv(RESULTS_DIR / "validation_baselines.csv", index=False)
    cv_frame.to_csv(RESULTS_DIR / "validation_cross_validation.csv", index=False)
    (RESULTS_DIR / "validation_cross_validation_summary.json").write_text(
        json.dumps(cv_summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    metadata = {
        "selected_candidate": selected_name,
        "selected_threshold": selected_threshold,
        "selection_rule": "Tối đa F1 trong các ngưỡng có recall validation >= minimum_recall; mô hình chọn theo PR-AUC.",
        "minimum_recall": selection["minimum_recall"],
        "train_rows": len(X_train),
        "validation_rows": len(X_validation),
        "train_positive_rate": positive_rate,
        "cross_validation": cv_summary,
        "duration_excluded": True,
        "test_accessed": False,
    }
    (MODELS_DIR / "model_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
