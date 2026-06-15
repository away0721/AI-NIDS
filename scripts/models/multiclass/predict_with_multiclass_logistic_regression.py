from pathlib import Path

import joblib
import pandas as pd


DATA_PATH = Path(r"D:\Projects\ai-nids\data\processed\multiclass_dataset.csv")

MODEL_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\logistic_regression_multiclass.pkl"
)
SCALER_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\logistic_regression_multiclass_scaler.pkl"
)
LABEL_ENCODER_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\multiclass_label_encoder.pkl"
)

RESULT_DIR = Path(
    r"D:\Projects\ai-nids\results\multiclass\logistic_regression"
)
OUTPUT_PATH = RESULT_DIR / "sample_predictions.csv"

LABEL_COLUMN = "attack_category"
SAMPLES_PER_CLASS = 5
RANDOM_STATE = 42


def main() -> None:
    print("正在加载数据...")
    df = pd.read_csv(DATA_PATH)

    if LABEL_COLUMN not in df.columns:
        raise ValueError(
            f"数据集中没有找到标签列：{LABEL_COLUMN}\n"
            f"当前数据列名为：{df.columns.tolist()}"
        )

    print("正在加载模型、Scaler 和 LabelEncoder...")
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)

    feature_columns = [col for col in df.columns if col != LABEL_COLUMN]

    print("正在从每个类别中抽取样本...")

    sample_parts = []

    for class_name, group in df.groupby(LABEL_COLUMN):
        sampled_group = group.sample(
            n=min(SAMPLES_PER_CLASS, len(group)),
            random_state=RANDOM_STATE,
        )
        sample_parts.append(sampled_group)

    sample_df = pd.concat(sample_parts, axis=0).reset_index(drop=True)

    if LABEL_COLUMN not in sample_df.columns:
        raise ValueError(
            f"抽样后的数据中没有找到标签列：{LABEL_COLUMN}\n"
            f"抽样后数据列名为：{sample_df.columns.tolist()}"
        )

    X_sample = sample_df[feature_columns]
    y_true_text = sample_df[LABEL_COLUMN]

    print("正在使用训练阶段保存的 Scaler 标准化样本...")
    X_sample_scaled = scaler.transform(X_sample)

    print("正在预测...")
    y_pred_encoded = model.predict(X_sample_scaled)
    y_pred_text = label_encoder.inverse_transform(y_pred_encoded)

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X_sample_scaled)
        confidence = probabilities.max(axis=1)
    else:
        confidence = [None] * len(y_pred_text)

    result_df = pd.DataFrame(
        {
            "true_label": y_true_text.values,
            "predicted_label": y_pred_text,
            "confidence": confidence,
            "is_correct": y_true_text.values == y_pred_text,
        }
    )

    print("\n预测结果：")
    print(result_df)

    print("\n预测正确数量：")
    print(result_df["is_correct"].value_counts())

    print("\n按类别统计预测结果：")
    class_summary = (
        result_df.groupby("true_label")["is_correct"]
        .agg(["count", "sum"])
        .rename(columns={"count": "total", "sum": "correct"})
    )
    class_summary["accuracy"] = class_summary["correct"] / class_summary["total"]
    print(class_summary)

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n样本预测结果已保存到：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()