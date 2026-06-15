from pathlib import Path

import joblib
import pandas as pd


DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\multiclass_dataset.csv"
)

MODEL_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\random_forest_multiclass.pkl"
)

LABEL_ENCODER_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\multiclass_label_encoder.pkl"
)

RESULT_DIR = Path(
    r"D:\Projects\ai-nids\results\multiclass\random_forest"
)

OUTPUT_PATH = RESULT_DIR / "sample_predictions.csv"

RANDOM_STATE = 42
SAMPLES_PER_CLASS = 5


def main():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    print("正在加载多分类 Random Forest 模型...")
    model = joblib.load(MODEL_PATH)

    print("正在加载 LabelEncoder...")
    label_encoder = joblib.load(LABEL_ENCODER_PATH)

    print("正在读取多分类数据集...")
    df = pd.read_csv(DATA_PATH)

    print("\n数据规模：")
    print(df.shape)

    print("\n类别分布：")
    print(df["attack_category"].value_counts())

    sample_dfs = []

    print("\n正在按类别抽样...")

    for class_name in sorted(df["attack_category"].unique()):
        class_df = df[df["attack_category"] == class_name]

        sample_size = min(SAMPLES_PER_CLASS, len(class_df))

        sampled = class_df.sample(
            n=sample_size,
            random_state=RANDOM_STATE,
        )

        sample_dfs.append(sampled)

        print(f"{class_name}: 抽样 {sample_size} 条")

    samples = pd.concat(sample_dfs, ignore_index=True)

    X_sample = samples.drop(columns=["attack_category"])
    y_true_text = samples["attack_category"]

    print("\n正在进行预测...")

    y_pred_encoded = model.predict(X_sample)
    y_pred_text = label_encoder.inverse_transform(y_pred_encoded)

    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_sample)
        max_proba = y_proba.max(axis=1)
    else:
        max_proba = [None] * len(samples)

    result_df = pd.DataFrame(
        {
            "true_label": y_true_text.values,
            "predicted_label": y_pred_text,
            "confidence": max_proba,
        }
    )

    result_df["is_correct"] = (
        result_df["true_label"] == result_df["predicted_label"]
    )

    print("\n预测结果：")
    print(result_df)

    print("\n预测正确数量：")
    print(result_df["is_correct"].value_counts())

    print("\n按类别统计预测结果：")
    summary_df = (
        result_df.groupby("true_label")["is_correct"]
        .agg(["count", "sum"])
        .rename(columns={"count": "total", "sum": "correct"})
    )

    summary_df["accuracy"] = summary_df["correct"] / summary_df["total"]

    print(summary_df)

    result_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\n样本预测结果已保存到：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()