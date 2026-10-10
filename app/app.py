from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

from src.features import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "bank_marketing_pipeline.joblib"
MANIFEST_PATH = ROOT / "data" / "processed" / "data_manifest.json"
VALIDATION_THRESHOLDS = ROOT / "reports" / "results" / "validation_thresholds.csv"
FINAL_METRICS = ROOT / "reports" / "results" / "final_test_metrics.json"

CATEGORIES = {
    "job": ["admin.", "blue-collar", "entrepreneur", "housemaid", "management", "retired", "self-employed", "services", "student", "technician", "unemployed", "unknown"],
    "marital": ["divorced", "married", "single"],
    "education": ["primary", "secondary", "tertiary", "unknown"],
    "default": ["no", "yes"],
    "housing": ["no", "yes"],
    "loan": ["no", "yes"],
    "contact": ["cellular", "telephone", "unknown"],
    "month": ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"],
    "poutcome": ["failure", "other", "success", "unknown"],
}
DEFAULTS = {
    "age": 35, "job": "technician", "marital": "married", "education": "secondary",
    "default": "no", "balance": 1200, "housing": "yes", "loan": "no",
    "contact": "cellular", "day": 15, "month": "may", "campaign": 1,
    "pdays": -1, "previous": 0, "poutcome": "unknown",
}
FIELD_META = {
    "age": {"label": "Tuổi", "unit": "năm"},
    "balance": {"label": "Số dư trung bình năm", "unit": "EUR"},
    "day": {"label": "Ngày liên hệ trong tháng", "unit": "ngày"},
    "campaign": {"label": "Số lần liên hệ trong chiến dịch", "unit": "lần"},
    "pdays": {"label": "Số ngày từ lần liên hệ trước", "unit": "ngày; -1 là chưa từng"},
    "previous": {"label": "Số lần liên hệ trước chiến dịch", "unit": "lần"},
    "job": {"label": "Nghề nghiệp"},
    "marital": {"label": "Tình trạng hôn nhân"},
    "education": {"label": "Trình độ học vấn"},
    "default": {"label": "Có nợ quá hạn"},
    "housing": {"label": "Có khoản vay nhà ở"},
    "loan": {"label": "Có khoản vay cá nhân"},
    "contact": {"label": "Kênh liên hệ"},
    "month": {"label": "Tháng liên hệ"},
    "poutcome": {"label": "Kết quả chiến dịch trước"},
}


def load_artifact():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def numeric_ranges() -> dict[str, dict[str, float]]:
    if not MANIFEST_PATH.exists():
        return {
            "age": {"min": 18, "max": 95}, "balance": {"min": -10000, "max": 110000},
            "day": {"min": 1, "max": 31}, "campaign": {"min": 1, "max": 63},
            "pdays": {"min": -1, "max": 871}, "previous": {"min": 0, "max": 275},
        }
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["quality"]["numeric_ranges"]


def validate_payload(payload) -> tuple[dict | None, list[str]]:
    if not isinstance(payload, dict):
        return None, ["Nội dung yêu cầu phải là một JSON object."]
    errors: list[str] = []
    if "duration" in payload:
        errors.append("Không nhận duration vì đây là biến chỉ có sau cuộc gọi và gây leakage.")
    missing = [name for name in FEATURES if name not in payload]
    extra = sorted(set(payload) - set(FEATURES) - {"duration"})
    if missing:
        errors.append("Thiếu trường: " + ", ".join(missing))
    if extra:
        errors.append("Trường không được hỗ trợ: " + ", ".join(extra))
    if errors:
        return None, errors
    cleaned: dict = {}
    ranges = numeric_ranges()
    for name in NUMERIC_FEATURES:
        try:
            value = float(payload[name])
        except (TypeError, ValueError):
            errors.append(f"{name} phải là số.")
            continue
        low, high = float(ranges[name]["min"]), float(ranges[name]["max"])
        if not low <= value <= high:
            errors.append(f"{name} nằm ngoài miền dữ liệu quan sát [{low:g}, {high:g}].")
        cleaned[name] = value
    for name in CATEGORICAL_FEATURES:
        value = str(payload[name]).strip().lower()
        if value not in CATEGORIES[name]:
            errors.append(f"{name} không hợp lệ. Giá trị cho phép: {', '.join(CATEGORIES[name])}.")
        cleaned[name] = value
    return (cleaned if not errors else None), errors


def score_record(payload: dict) -> tuple[dict | None, list[str]]:
    cleaned, errors = validate_payload(payload)
    if errors:
        return None, errors
    artifact = load_artifact()
    if artifact is None:
        return None, ["Chưa có model. Hãy chạy pipeline huấn luyện trước."]
    frame = pd.DataFrame([cleaned], columns=FEATURES)
    probability = float(artifact["pipeline"].predict_proba(frame)[0, 1])
    threshold = float(artifact["threshold"])
    return {
        "probability": round(probability, 6),
        "threshold": threshold,
        "priority_label": "ưu tiên liên hệ" if probability >= threshold else "chưa ưu tiên",
        "model": artifact["selected_candidate"],
        "warning": "Đây là hỗ trợ xếp hạng, không phải mệnh lệnh hoặc căn cứ loại trừ dịch vụ.",
    }, []


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def index():
        return render_template("index.html", active="index")

    @app.route("/score", methods=["GET", "POST"])
    def score():
        values = DEFAULTS.copy()
        result = None
        errors: list[str] = []
        if request.method == "POST":
            values.update(request.form.to_dict())
            result, errors = score_record(values)
        return render_template(
            "score.html", active="score", values=values, categories=CATEGORIES,
            ranges=numeric_ranges(), field_meta=FIELD_META, result=result, errors=errors,
        )

    @app.get("/dashboard")
    def dashboard():
        rows = pd.read_csv(VALIDATION_THRESHOLDS).to_dict(orient="records") if VALIDATION_THRESHOLDS.exists() else []
        final = json.loads(FINAL_METRICS.read_text(encoding="utf-8")) if FINAL_METRICS.exists() else None
        return render_template("dashboard.html", active="dashboard", threshold_rows=rows, final=final)

    @app.get("/model-card")
    def model_card():
        return render_template("model_card.html", active="model-card")

    @app.post("/api/score")
    def api_score():
        result, errors = score_record(request.get_json(silent=True))
        if errors:
            code = 503 if errors == ["Chưa có model. Hãy chạy pipeline huấn luyện trước."] else 422
            return jsonify({"errors": errors}), code
        return jsonify(result), 200

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "model_ready": MODEL_PATH.exists()})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=False)
