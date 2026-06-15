from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split


DATA_PATH = Path(r"D:\Projects\ai-nids\data\processed\multiclass_dataset.csv")

MODEL_PATH = Path(r"D:\Projects\ai-nids\models\multiclass\random_forest_multiclass.pkl")
LABEL_ENCODER_PATH = Path(r"D:\Projects\ai-nids\models\multiclass\multiclass_label_encoder.pkl")

RESULT_DIR = Path(r"D:\Projects\ai-nids\results\multiclass\random_forest_error_patterns")

ERROR_DETAIL_CSV_PATH = RESULT_DIR / "random_forest_error_details.csv"
ERROR_PATTERN_CSV_PATH = RESULT_DIR / "random_forest_error_pattern_summary.csv"
ERROR_PATTERN_FIG_PATH = RESULT_DIR / "random_forest_top_error_patterns.png"
ATTACK_TO_BENIGN_CSV_PATH = RESULT_DIR / "random_forest_attack_to_benign_errors.csv"
BENIGN_TO_ATTACK_CSV_PATH = RESULT_DIR / "random_forest_benign_to_attack_errors.csv"

LABEL_COLUMN = "attack_category"

RANDOM_STATE = 42
TEST_SIZE = 0.2


def plot_top_error_patterns(error_pattern_df: pd.DataFrame) -> None:
    top_df = error_pattern_df.head(15).copy()

    labels = (
        top_df["true_label"].astype(str)
        + " -> "
        + top_df["predicted_label"].astype(str)
    )

    plt.figure(figsize=(12, 7))
    plt.barh(labels[::-1], top_df["count"][::-1])
    plt.title("Top Random Forest Error Patterns")
    plt.xlabel("Error Count")
    plt.ylabel("True Label -> Predicted Label")
    plt.tight_layout()
    plt.savefig(ERROR_PATTERN_FIG_PATH)
    plt.close()


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    print("正在加载多分类数据集...")
    df = pd.read_csv(DATA_PATH)

    if LABEL_COLUMN not in df.columns:
        raise ValueError(f"数据集中没有找到标签列：{LABEL_COLUMN}")

    print(f"数据规模：{df.shape}")

    X = df.drop(columns=[LABEL_COLUMN])
    y_text = df[LABEL_COLUMN]

    print("\n正在加载 LabelEncoder...")
    label_encoder = joblib.load(LABEL_ENCODER_PATH)

    y = label_encoder.transform(y_text)
    class_names = label_encoder.classes_

    print("类别映射：")
    for index, class_name in enumerate(class_names):
        print(f"{index}: {class_name}")

    print("\n正在划分训练集和测试集...")
    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    print(f"X_test: {X_test.shape}")

    print("\n正在加载 Random Forest 模型...")
    model = joblib.load(MODEL_PATH)

    print("\n正在预测测试集...")
    y_pred = model.predict(X_test)

    print("\n正在统计错误样本...")
    result_df = pd.DataFrame(
        {
            "original_index": X_test.index,
            "true_label_id": y_test,
            "predicted_label_id": y_pred,
        }
    )

    result_df["true_label"] = result_df["true_label_id"].apply(
        lambda index: class_names[index]
    )

    result_df["predicted_label"] = result_df["predicted_label_id"].apply(
        lambda index: class_names[index]
    )

    result_df["is_correct"] = (
        result_df["true_label_id"] == result_df["predicted_label_id"]
    )

    error_df = result_df[result_df["is_correct"] == False].copy()

    error_df["error_type"] = (
        error_df["true_label"].astype(str)
        + " -> "
        + error_df["predicted_label"].astype(str)
    )

    error_pattern_df = (
        error_df.groupby(["true_label", "predicted_label", "error_type"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    total_samples = len(result_df)
    total_errors = len(error_df)
    error_rate = total_errors / total_samples

    print(f"测试集样本数：{total_samples}")
    print(f"错误样本数：{total_errors}")
    print(f"错误率：{error_rate:.4f}")

    print("\nTop 15 错误模式：")
    print(error_pattern_df.head(15))

    print("\n正在统计 Attack -> BENIGN 漏报...")
    attack_to_benign_df = error_pattern_df[
        (error_pattern_df["true_label"] != "BENIGN")
        & (error_pattern_df["predicted_label"] == "BENIGN")
    ].copy()

    print(attack_to_benign_df)

    print("\n正在统计 BENIGN -> Attack 误报...")
    benign_to_attack_df = error_pattern_df[
        (error_pattern_df["true_label"] == "BENIGN")
        & (error_pattern_df["predicted_label"] != "BENIGN")
    ].copy()

    print(benign_to_attack_df)

    print("\n正在保存结果...")

    error_df.to_csv(
        ERROR_DETAIL_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    error_pattern_df.to_csv(
        ERROR_PATTERN_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    attack_to_benign_df.to_csv(
        ATTACK_TO_BENIGN_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    benign_to_attack_df.to_csv(
        BENIGN_TO_ATTACK_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    plot_top_error_patterns(error_pattern_df)

    print(f"\n错误样本明细已保存到：{ERROR_DETAIL_CSV_PATH}")
    print(f"错误模式汇总已保存到：{ERROR_PATTERN_CSV_PATH}")
    print(f"Top 错误模式图已保存到：{ERROR_PATTERN_FIG_PATH}")
    print(f"Attack -> BENIGN 漏报统计已保存到：{ATTACK_TO_BENIGN_CSV_PATH}")
    print(f"BENIGN -> Attack 误报统计已保存到：{BENIGN_TO_ATTACK_CSV_PATH}")


if __name__ == "__main__":
    main()