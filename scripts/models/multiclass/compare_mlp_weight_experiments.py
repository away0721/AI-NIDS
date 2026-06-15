from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


RESULT_ROOT = Path(r"D:\Projects\ai-nids\results\multiclass")

MODEL_METRICS_FILES = {
    "MLP": RESULT_ROOT / "mlp_torch" / "mlp_torch_multiclass_metrics.csv",
    "Weighted MLP": RESULT_ROOT
    / "mlp_torch_weighted"
    / "mlp_torch_weighted_multiclass_metrics.csv",
    "Clipped Weighted MLP": RESULT_ROOT
    / "mlp_torch_weighted_clipped"
    / "mlp_torch_weighted_clipped_multiclass_metrics.csv",
}

OUTPUT_DIR = RESULT_ROOT / "mlp_weight_experiments"
OUTPUT_CSV_PATH = OUTPUT_DIR / "mlp_weight_experiments_comparison.csv"
OUTPUT_FIG_PATH = OUTPUT_DIR / "mlp_weight_experiments_comparison.png"


def get_metric_value(row, *possible_names: str) -> float:
    for name in possible_names:
        if name in row.index:
            return float(row[name])

    raise KeyError(
        f"找不到指标列，候选列名：{possible_names}，当前列名：{row.index.tolist()}"
    )


def load_metrics(model_name: str, metrics_path: Path) -> dict:
    if not metrics_path.exists():
        raise FileNotFoundError(f"找不到指标文件：{metrics_path}")

    df = pd.read_csv(metrics_path)
    df.columns = [column.strip() for column in df.columns]

    if "accuracy" not in df.columns:
        raise ValueError(
            f"无法识别指标文件格式：{metrics_path}\n"
            f"当前列名：{df.columns.tolist()}"
        )

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


def plot_comparison(comparison_df: pd.DataFrame) -> None:
    plot_df = comparison_df.set_index("model")[
        [
            "accuracy",
            "macro_precision",
            "macro_recall",
            "macro_f1_score",
            "weighted_f1_score",
        ]
    ]

    plt.figure(figsize=(12, 6))
    plot_df.plot(kind="bar", figsize=(12, 6))

    plt.title("MLP Weight Experiment Comparison")
    plt.ylabel("Score")
    plt.ylim(0, 1)
    plt.xlabel("Experiment")
    plt.xticks(rotation=20, ha="right")
    plt.legend(
        [
            "Accuracy",
            "Macro Precision",
            "Macro Recall",
            "Macro F1",
            "Weighted F1",
        ]
    )
    plt.tight_layout()
    plt.savefig(OUTPUT_FIG_PATH)
    plt.close()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("正在读取 MLP 权重实验指标...")

    rows = []

    for model_name, metrics_path in MODEL_METRICS_FILES.items():
        print(f"读取 {model_name}: {metrics_path}")
        rows.append(load_metrics(model_name, metrics_path))

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

    print("\nMLP 权重实验对比结果：")
    print(comparison_df)

    comparison_df.to_csv(
        OUTPUT_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    plot_comparison(comparison_df)

    print(f"\n对比 CSV 已保存到：{OUTPUT_CSV_PATH}")
    print(f"对比图已保存到：{OUTPUT_FIG_PATH}")

    best_accuracy = comparison_df.loc[
        comparison_df["accuracy"].idxmax(),
        "model",
    ]
    best_macro_recall = comparison_df.loc[
        comparison_df["macro_recall"].idxmax(),
        "model",
    ]
    best_macro_f1 = comparison_df.loc[
        comparison_df["macro_f1_score"].idxmax(),
        "model",
    ]
    best_weighted_f1 = comparison_df.loc[
        comparison_df["weighted_f1_score"].idxmax(),
        "model",
    ]

    print("\n最佳实验：")
    print(f"Accuracy 最佳：{best_accuracy}")
    print(f"Macro Recall 最佳：{best_macro_recall}")
    print(f"Macro F1 最佳：{best_macro_f1}")
    print(f"Weighted F1 最佳：{best_weighted_f1}")


if __name__ == "__main__":
    main()