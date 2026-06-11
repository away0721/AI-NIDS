from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(
    r"D:\Projects\ai-nids\models\random_forest_binary.pkl"
)

DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\binary_dataset.csv"
)

RESULT_PATH = Path(
    r"D:\Projects\ai-nids\results\random_forest\sample_predictions.csv"
)


def main():
    print("正在加载 Random Forest 模型...")
    model = joblib.load(MODEL_PATH)

    print("正在读取二分类数据集...")
    df = pd.read_csv(DATA_PATH)

    benign_samples = df[df["binary_label"] == 0].sample(
        n=5,
        random_state=42,
    )

    attack_samples = df[df["binary_label"] == 1].sample(
        n=5,
        random_state=42,
    )

    sample_df = pd.concat(
        [benign_samples, attack_samples],
        ignore_index=True,
    )

    sample_X = sample_df.drop(columns=["binary_label"])
    sample_y = sample_df["binary_label"]

    print("\n正在预测 10 条 Flow...")
    predictions = model.predict(sample_X)

    result_df = pd.DataFrame({
        "true_label": sample_y.values,
        "predicted_label": predictions,
    })

    result_df["true_name"] = result_df["true_label"].map({
        0: "BENIGN",
        1: "ATTACK",
    })

    result_df["predicted_name"] = result_df["predicted_label"].map({
        0: "BENIGN",
        1: "ATTACK",
    })

    result_df["is_correct"] = (
        result_df["true_label"] == result_df["predicted_label"]
    )

    print("\n预测结果：")
    print(result_df)

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(RESULT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n预测结果已保存到：{RESULT_PATH}")


if __name__ == "__main__":
    main()