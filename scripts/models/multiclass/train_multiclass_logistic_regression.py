from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\multiclass_dataset.csv"
)

RESULT_DIR = Path(
    r"D:\Projects\ai-nids\results\multiclass\logistic_regression"
)

MODEL_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\logistic_regression_multiclass.pkl"
)

SCALER_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\logistic_regression_multiclass_scaler.pkl"
)

LABEL_ENCODER_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\multiclass_label_encoder.pkl"
)

RANDOM_STATE = 42
TEST_SIZE = 0.2


def main():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("正在读取多分类数据集...")
    df = pd.read_csv(DATA_PATH)

    print("\n数据规模：")
    print(df.shape)

    print("\n类别分布：")
    print(df["attack_category"].value_counts())

    X = df.drop(columns=["attack_category"])
    y_text = df["attack_category"]

    print("\n正在编码多分类标签...")

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_text)

    print("\n类别编码映射：")
    for class_id, class_name in enumerate(label_encoder.classes_):
        print(f"{class_id}: {class_name}")

    joblib.dump(label_encoder, LABEL_ENCODER_PATH)

    print("\n正在划分训练集和测试集...")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    print("\n数据划分结果：")
    print(f"X_train: {X_train.shape}")
    print(f"X_test:  {X_test.shape}")
    print(f"y_train: {y_train.shape}")
    print(f"y_test:  {y_test.shape}")

    print("\n正在标准化特征...")

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    joblib.dump(scaler, SCALER_PATH)

    print("\n正在训练多分类 Logistic Regression...")

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        solver="saga",
        verbose=1,
    )

    model.fit(X_train_scaled, y_train)

    print("\n正在测试集上预测...")

    y_pred = model.predict(X_test_scaled)

    accuracy = accuracy_score(y_test, y_pred)

    macro_precision = precision_score(
        y_test,
        y_pred,
        average="macro",
        zero_division=0,
    )

    macro_recall = recall_score(
        y_test,
        y_pred,
        average="macro",
        zero_division=0,
    )

    macro_f1 = f1_score(
        y_test,
        y_pred,
        average="macro",
        zero_division=0,
    )

    weighted_precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    weighted_recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    class_names = label_encoder.classes_

    report = classification_report(
        y_test,
        y_pred,
        target_names=class_names,
        digits=4,
        zero_division=0,
    )

    cm = confusion_matrix(y_test, y_pred)

    print("\n多分类评估结果：")
    print(f"Accuracy:           {accuracy:.4f}")
    print(f"Macro Precision:    {macro_precision:.4f}")
    print(f"Macro Recall:       {macro_recall:.4f}")
    print(f"Macro F1 Score:     {macro_f1:.4f}")
    print(f"Weighted Precision: {weighted_precision:.4f}")
    print(f"Weighted Recall:    {weighted_recall:.4f}")
    print(f"Weighted F1 Score:  {weighted_f1:.4f}")

    print("\nClassification Report:")
    print(report)

    print("\nConfusion Matrix:")
    print(cm)

    print("\n正在保存模型和结果...")

    joblib.dump(model, MODEL_PATH)

    report_path = RESULT_DIR / "logistic_regression_multiclass_report.txt"
    metrics_csv_path = RESULT_DIR / "logistic_regression_multiclass_metrics.csv"
    metrics_png_path = RESULT_DIR / "logistic_regression_multiclass_metrics.png"
    cm_png_path = RESULT_DIR / "logistic_regression_multiclass_confusion_matrix.png"

    result_text = f"""Logistic Regression Multi-Class Classification Report

Dataset:
- Data path: {DATA_PATH}
- Samples: {len(df)}
- Feature count: {X.shape[1]}
- Label column: attack_category
- Classes: {list(class_names)}

Data Split:
- Train set: {X_train.shape}
- Test set: {X_test.shape}
- test_size: {TEST_SIZE}
- random_state: {RANDOM_STATE}
- stratify: y

Preprocessing:
- StandardScaler
- Scaler is fitted only on training set
- Test set is transformed using the same scaler

Model:
- LogisticRegression
- max_iter: 1000
- class_weight: balanced
- solver: saga

Metrics:
- Accuracy:           {accuracy:.4f}
- Macro Precision:    {macro_precision:.4f}
- Macro Recall:       {macro_recall:.4f}
- Macro F1 Score:     {macro_f1:.4f}
- Weighted Precision: {weighted_precision:.4f}
- Weighted Recall:    {weighted_recall:.4f}
- Weighted F1 Score:  {weighted_f1:.4f}

Classification Report:
{report}

Confusion Matrix:
{cm}
"""

    report_path.write_text(result_text, encoding="utf-8")

    metrics_df = pd.DataFrame(
        [
            {
                "model": "Logistic Regression",
                "task": "multiclass",
                "accuracy": accuracy,
                "macro_precision": macro_precision,
                "macro_recall": macro_recall,
                "macro_f1": macro_f1,
                "weighted_precision": weighted_precision,
                "weighted_recall": weighted_recall,
                "weighted_f1": weighted_f1,
            }
        ]
    )

    metrics_df.to_csv(
        metrics_csv_path,
        index=False,
        encoding="utf-8-sig",
    )

    metric_names = [
        "Accuracy",
        "Macro Precision",
        "Macro Recall",
        "Macro F1",
        "Weighted Precision",
        "Weighted Recall",
        "Weighted F1",
    ]

    metric_values = [
        accuracy,
        macro_precision,
        macro_recall,
        macro_f1,
        weighted_precision,
        weighted_recall,
        weighted_f1,
    ]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(metric_names, metric_values)
    plt.ylim(0.0, 1.05)
    plt.title("Logistic Regression Multi-Class Metrics")
    plt.ylabel("Score")
    plt.xticks(rotation=30, ha="right")

    for bar, value in zip(bars, metric_values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.01,
            f"{value:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(metrics_png_path, dpi=300)
    plt.close()

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=class_names,
    )

    fig, ax = plt.subplots(figsize=(12, 10))
    disp.plot(
        ax=ax,
        cmap="Blues",
        colorbar=False,
        xticks_rotation=45,
    )
    plt.title("Logistic Regression Multi-Class Confusion Matrix")
    plt.tight_layout()
    plt.savefig(cm_png_path, dpi=300)
    plt.close()

    print(f"\n模型已保存到：{MODEL_PATH}")
    print(f"Scaler 已保存到：{SCALER_PATH}")
    print(f"LabelEncoder 已保存到：{LABEL_ENCODER_PATH}")
    print(f"文本报告已保存到：{report_path}")
    print(f"指标 CSV 已保存到：{metrics_csv_path}")
    print(f"指标图已保存到：{metrics_png_path}")
    print(f"混淆矩阵图已保存到：{cm_png_path}")


if __name__ == "__main__":
    main()