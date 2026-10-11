from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "data/README.md",
    "docs/data_dictionary.md",
    "docs/model_card.md",
    "docs/api.md",
    "docs/phan_cong_nhom.md",
    "docs/nhat_ky_6_tuan.md",
    "models/bank_marketing_pipeline.joblib",
    "models/model_metadata.json",
    "reports/results/validation_candidates.csv",
    "reports/results/validation_thresholds.csv",
    "reports/results/validation_cross_validation.csv",
    "reports/results/validation_cross_validation_summary.json",
    "reports/results/final_test_metrics.json",
    "reports/results/test_model_comparison.csv",
    "reports/results/test_error_analysis.csv",
    "reports/figures/test_precision_recall.png",
    "reports/figures/test_confusion_matrix.png",
]


def main() -> None:
    missing = [relative for relative in REQUIRED_FILES if not (ROOT / relative).exists()]
    if missing:
        raise SystemExit("Thiếu artifact bàn giao:\n- " + "\n- ".join(missing))

    metadata = json.loads((ROOT / "models/model_metadata.json").read_text(encoding="utf-8"))
    final = json.loads((ROOT / "reports/results/final_test_metrics.json").read_text(encoding="utf-8"))
    if not metadata.get("duration_excluded"):
        raise SystemExit("Metadata chưa xác nhận loại duration.")
    if not metadata.get("test_accessed"):
        raise SystemExit("Chưa có lần đánh giá test cuối.")
    if final["selected_threshold_frozen_on_validation"] != metadata["selected_threshold"]:
        raise SystemExit("Ngưỡng test không khớp ngưỡng đã đóng băng trên validation.")
    if not {"pr_auc", "average_precision"}.issubset(final["metrics"]):
        raise SystemExit("Kết quả test chưa tách riêng PR-AUC và Average Precision.")

    comparison = pd.read_csv(ROOT / "reports/results/test_model_comparison.csv")
    model_rate = float(
        comparison.loc[comparison["candidate"] == final["selected_candidate"], "contact_rate"].iloc[0]
    )
    random_rate = float(
        comparison.loc[comparison["candidate"] == "random_equal_contact_rate", "contact_rate"].iloc[0]
    )
    if abs(model_rate - random_rate) > 1e-12:
        raise SystemExit("Random baseline chưa dùng cùng tỷ lệ liên hệ với mô hình.")

    print("Release check: ĐẠT")
    print(f"Mô hình: {final['selected_candidate']}")
    print(f"Ngưỡng: {final['selected_threshold_frozen_on_validation']}")
    print(f"PR-AUC test: {final['metrics']['pr_auc']:.3f}")
    print(f"Average Precision test: {final['metrics']['average_precision']:.3f}")
    print(f"Recall test: {final['metrics']['recall']:.3f}")


if __name__ == "__main__":
    main()
