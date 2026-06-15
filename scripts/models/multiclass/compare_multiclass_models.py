from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


RESULT_ROOT = Path(r"D:\Projects\ai-nids\results\multiclass")

MODEL_METRICS_FILES = {
    "Random Forest": RESULT_ROOT / "random_forest" / "random_forest_multiclass_metrics.csv",
    "Logistic Regression": RESULT_ROOT
    / "logistic_regression"
    / "logistic_regression_multiclass_metrics.csv",
    "PyTorch MLP": RESULT_ROOT / "mlp_torch" / "mlp_torch_multiclass_metrics.csv",
    "PyTorch CNN": RESULT_ROOT / "cnn_torch" / "cnn_torch_multiclass_metrics.csv",
}

OUTPUT_DIR = RESULT_ROOT / "model_comparison"
OUTPUT_CSV_PATH = OUTPUT_DIR / "multiclass_model_comparison.csv"
OUTPUT_FIG_PATH = OUTPUT_DIR / "multiclass_model_comparison.png"


def get_metric_value(row, *possible_names: str) -> float:
    for name in possible_names:
        if name in row.index:
            return float(row[name])
    raise KeyError(f"找不到指标列，候选列名：{possible_names}，当前列名：{row.index.tolist()}")


def load_metrics(model_name: str, metrics_path: Path) -> dict:
    if not metrics_path.exists():
        raise FileNotFoundError(f"找不到指标文件：{metrics_path}")

    df = pd.read_csv(metrics_path)

    # 清理列名，避免 ' weighted_f1' 这种空格问题
    df.columns = [column.strip() for column in df.columns]

    # 情况 1：一行保存所有指标
    if "accuracy" in df.columns:
        row = df.iloc[0]

        return {
            "model": model_name,
            "accuracy": get_metric_value(row, "accuracy"),
            "macro_precision": get_metric_value(row, "macro_precision"),
            "macro_recall": get_metric_value(row, "macro_recall"),
            "macro_f1_score": get_metric_value(row, "macro_f1_score", "macro_f1"),
            "weighted_precision": get_metric_value(row, "weighted_precision"),
            "weighted_recall": get_metric_value(row, "weighted_recall"),
            "weighted_f1_score": get_metric_value(
                row,
                "weighted_f1_score",
                "weighted_f1",
            ),
        }

    # 情况 2：metric,score 旧格式
    if {"metric", "score"}.issubset(df.columns):
        metrics_dict = dict(zip(df["metric"], df["score"]))

        return {
            "model": model_name,
            "accuracy": float(metrics_dict.get("accuracy", 0.0)),
            "macro_precision": float(metrics_dict.get("macro_precision", 0.0)),
            "macro_recall": float(metrics_dict.get("macro_recall", 0.0)),
            "macro_f1_score": float(
                metrics_dict.get(
                    "macro_f1_score",
                    metrics_dict.get("macro_f1", 0.0),
                )
            ),
            "weighted_precision": float(metrics_dict.get("weighted_precision", 0.0)),
            "weighted_recall": float(metrics_dict.get("weighted_recall", 0.0)),
            "weighted_f1_score": float(
                metrics_dict.get(
                    "weighted_f1_score",
                    metrics_dict.get("weighted_f1", 0.0),
                )
            ),
        }

    raise ValueError(
        f"无法识别指标文件格式：{metrics_path}\n"
        f"当前列名：{df.columns.tolist()}"
    )


def plot_model_comparison(comparison_df: pd.DataFrame) -> None:
    plot_df = comparison_df.set_index("model")[
        [
            "accuracy",
            "macro_f1_score",
            "weighted_f1_score",
        ]
    ]

    plt.figure(figsize=(10, 6))
    plot_df.plot(kind="bar", figsize=(10, 6))

    plt.title("Multiclass Model Comparison")
    plt.ylabel("Score")
    plt.ylim(0, 1)
    plt.xlabel("Model")
    plt.xticks(rotation=20, ha="right")
    plt.legend(["Accuracy", "Macro F1", "Weighted F1"])
    plt.tight_layout()
    plt.savefig(OUTPUT_FIG_PATH)
    plt.close()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("正在读取多分类模型指标...")

    rows = []

    for model_name, metrics_path in MODEL_METRICS_FILES.items():
        print(f"读取 {model_name}: {metrics_path}")
        row = load_metrics(model_name, metrics_path)
        rows.append(row)

    comparison_df = pd.DataFrame(rows)

    comparison_df = comparison_df[
        [
            "model",
            "accuracy",
            "macro_precision",
            "macro_recall",
            "macro_f1_score",
            "weighted_precision",
            "weighted_recall",
            "weighted_f1_score",
        ]
    ]

    print("\n多分类模型对比结果：")
    print(comparison_df)

    comparison_df.to_csv(
        OUTPUT_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    plot_model_comparison(comparison_df)

    print(f"\n对比 CSV 已保存到：{OUTPUT_CSV_PATH}")
    print(f"对比图已保存到：{OUTPUT_FIG_PATH}")

    best_accuracy_model = comparison_df.loc[
        comparison_df["accuracy"].idxmax(), "model"
    ]
    best_macro_f1_model = comparison_df.loc[
        comparison_df["macro_f1_score"].idxmax(), "model"
    ]
    best_weighted_f1_model = comparison_df.loc[
        comparison_df["weighted_f1_score"].idxmax(), "model"
    ]

    print("\n最佳模型：")
    print(f"Accuracy 最佳：{best_accuracy_model}")
    print(f"Macro F1 最佳：{best_macro_f1_model}")
    print(f"Weighted F1 最佳：{best_weighted_f1_model}")


if __name__ == "__main__":
    main()