from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .features import TARGET

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "reports" / "figures"


def save_eda_figures(train_frame: pd.DataFrame) -> None:
    """Tạo EDA chỉ từ tập train để không nhìn validation/test."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    counts = train_frame[TARGET].value_counts().reindex(["no", "yes"])
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars = ax.bar(["Không đăng ký", "Đăng ký"], counts.values, color=["#334155", "#0f766e"])
    ax.set_title("Phân bố lớp trên tập huấn luyện")
    ax.set_ylabel("Số quan sát")
    for bar, value in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:,}", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "train_target_distribution.png", dpi=180)
    plt.close(fig)

    job_rate = (
        train_frame.assign(target=(train_frame[TARGET] == "yes").astype(int))
        .groupby("job", observed=True)["target"]
        .agg(["mean", "count"])
        .sort_values("mean")
    )
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    ax.barh(job_rate.index, job_rate["mean"], color="#2563eb")
    ax.set_title("Tỷ lệ đăng ký theo nghề nghiệp trên train")
    ax.set_xlabel("Tỷ lệ đăng ký")
    ax.xaxis.set_major_formatter(lambda value, _pos: f"{value:.0%}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "train_job_positive_rate.png", dpi=180)
    plt.close(fig)


def main() -> None:
    train_path = PROCESSED_DIR / "train.csv"
    if not train_path.exists():
        raise FileNotFoundError("Chưa có train.csv. Chạy tuần 2 từ bước tải dữ liệu trước.")
    train_frame = pd.read_csv(train_path)
    save_eda_figures(train_frame)
    print(f"Đã tạo EDA từ {len(train_frame):,} dòng train tại {FIGURES_DIR}")


if __name__ == "__main__":
    main()
