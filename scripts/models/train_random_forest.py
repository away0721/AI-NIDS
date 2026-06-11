from pathlib import Path

import matplotlib.pyplot as plt
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split

MODEL_PATH = Path(
    r"D:\Projects\ai-nids\models\random_forest_binary.pkl"
)

DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\binary_dataset.csv"
)

RESULT_DIR = Path(
    r"D:\Projects\ai-nids\results\random_forest"
)

REPORT_PATH = RESULT_DIR / "random_forest_binary_report.txt"
METRICS_CSV_PATH = RESULT_DIR / "random_forest_binary_metrics.csv"
METRICS_FIG_PATH = RESULT_DIR / "random_forest_binary_metrics.png"
CONFUSION_MATRIX_FIG_PATH = RESULT_DIR / "random_forest_binary_confusion_matrix.png"


def plot_metrics(metrics: dict[str, float]) -> None:
    names = list(metrics.keys())
    values = list(metrics.values())

    plt.figure(figsize=(8, 5))
    plt.bar(names, values)
    plt.ylim(0, 1.05)
    plt.title("Random Forest Binary Classification Metrics")
    plt.ylabel("Score")

    for index, value in enumerate(values):
        plt.text(index, value + 0.01, f"{value:.4f}", ha="center")

    plt.tight_layout()
    plt.savefig(METRICS_FIG_PATH, dpi=300)
    plt.close()


def plot_confusion_matrix(cm) -> None:
    plt.figure(figsize=(6, 5))
    plt.imshow(cm)
    plt.title("Random Forest Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")

    labels = ["BENIGN", "ATTACK"]
    plt.xticks([0, 1], labels)
    plt.yticks([0, 1], labels)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center")

    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_FIG_PATH, dpi=300)
    plt.close()


def main():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

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

    print("正在训练 Random Forest Baseline...")

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"模型已保存到：{MODEL_PATH}")
    
    print("正在预测测试集...")
    y_pred = model.predict(X_test)

    # 4. 保存特征重要性 Top 20
    feature_importance_path = RESULT_DIR / "feature_importance_top20.png"
    feature_importance_csv_path = RESULT_DIR / "feature_importance_top20.csv"

    feature_importance_df = pd.DataFrame({
        "feature": X.columns,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)

    top20 = feature_importance_df.head(20)

    top20.to_csv(
        feature_importance_csv_path,
        index=False,
        encoding="utf-8-sig",
    )

    plt.figure(figsize=(10, 8))
    plt.barh(top20["feature"][::-1], top20["importance"][::-1])
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title("Random Forest Top 20 Feature Importance")
    plt.tight_layout()
    plt.savefig(feature_importance_path, dpi=300)
    plt.close()

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    metrics = {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
    }

    report = classification_report(
        y_test,
        y_pred,
        target_names=["BENIGN", "ATTACK"],
        digits=4,
    )

    result_text = f"""Random Forest Binary Classification Baseline

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
- RandomForestClassifier
- n_estimators: 100
- random_state: 42
- n_jobs: -1
- class_weight: balanced

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

    print("\n评估结果：")
    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")

    print("\nConfusion Matrix:")
    print(cm)

    REPORT_PATH.write_text(result_text, encoding="utf-8")

    metrics_df = pd.DataFrame(
        [{"metric": name, "score": value} for name, value in metrics.items()]
    )
    metrics_df.to_csv(METRICS_CSV_PATH, index=False, encoding="utf-8-sig")

    plot_metrics(metrics)
    plot_confusion_matrix(cm)

    print("\n实验结果已保存：")
    print(REPORT_PATH)
    print(METRICS_CSV_PATH)
    print(METRICS_FIG_PATH)
    print(CONFUSION_MATRIX_FIG_PATH)
    print(f"特征重要性图已保存到：{feature_importance_path}")
    print(f"特征重要性 CSV 已保存到：{feature_importance_csv_path}")

if __name__ == "__main__":
    main()