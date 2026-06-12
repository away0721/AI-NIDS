from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\binary_dataset.csv"
)

RESULT_DIR = Path(
    r"D:\Projects\ai-nids\results\logistic_regression"
)

MODEL_PATH = Path(
    r"D:\Projects\ai-nids\models\logistic_regression_binary.pkl"
)


def main():
    print("正在读取二分类数据集...")
    df = pd.read_csv(DATA_PATH)

    X = df.drop(columns=["binary_label"])
    y = df["binary_label"]

    print("正在划分训练集和测试集...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("正在训练 Logistic Regression Baseline...")

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)

    print("正在预测测试集...")
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    report = classification_report(
        y_test,
        y_pred,
        target_names=["BENIGN", "ATTACK"],
        digits=4,
    )

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    result_text = f"""Logistic Regression Binary Classification Baseline

Dataset:
- Data path: {DATA_PATH}
- Total samples: {len(df)}
- Feature count: {X.shape[1]}
- Task: Binary Classification
- Label mapping:
  - BENIGN -> 0
  - ATTACK -> 1

Train/Test Split:
- test_size: 0.2
- random_state: 42
- stratify: y
- X_train: {X_train.shape}
- X_test: {X_test.shape}
- y_train: {y_train.shape}
- y_test: {y_test.shape}

Model:
- Pipeline
- StandardScaler
- LogisticRegression
- max_iter: 1000
- class_weight: balanced
- random_state: 42

Metrics:
- Accuracy:  {accuracy:.4f}
- Precision: {precision:.4f}
- Recall:    {recall:.4f}
- F1 Score:  {f1:.4f}

Confusion Matrix:
{cm}

Classification Report:
{report}
"""

    report_path = RESULT_DIR / "logistic_regression_binary_report.txt"
    metrics_csv_path = RESULT_DIR / "logistic_regression_binary_metrics.csv"
    metrics_png_path = RESULT_DIR / "logistic_regression_binary_metrics.png"
    cm_png_path = RESULT_DIR / "logistic_regression_binary_confusion_matrix.png"

    report_path.write_text(result_text, encoding="utf-8")

    metrics_df = pd.DataFrame(
        [
            {
                "model": "Logistic Regression",
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
            }
        ]
    )
    metrics_df.to_csv(metrics_csv_path, index=False, encoding="utf-8-sig")

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["BENIGN", "ATTACK"],
    )
    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, colorbar=False)
    plt.title("Logistic Regression Confusion Matrix")
    plt.tight_layout()
    plt.savefig(cm_png_path, dpi=300)
    plt.close()

    metric_names = ["Accuracy", "Precision", "Recall", "F1 Score"]
    metric_values = [accuracy, precision, recall, f1]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(metric_names, metric_values)
    plt.ylim(0.0, 1.05)
    plt.title("Logistic Regression Binary Classification Metrics")
    plt.ylabel("Score")

    for bar, value in zip(bars, metric_values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.01,
            f"{value:.4f}",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    plt.savefig(metrics_png_path, dpi=300)
    plt.close()

    print("\n评估结果：")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    print("\nConfusion Matrix:")
    print(cm)

    print(f"\n模型已保存到：{MODEL_PATH}")
    print(f"文本报告已保存到：{report_path}")
    print(f"指标 CSV 已保存到：{metrics_csv_path}")
    print(f"指标图已保存到：{metrics_png_path}")
    print(f"混淆矩阵图已保存到：{cm_png_path}")


if __name__ == "__main__":
    main()