from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


METRICS_FILES = [
    Path(r"D:\Projects\ai-nids\results\random_forest\random_forest_binary_metrics.csv"),
    Path(r"D:\Projects\ai-nids\results\logistic_regression\logistic_regression_binary_metrics.csv"),
    Path(r"D:\Projects\ai-nids\results\mlp_torch\mlp_torch_binary_metrics.csv"),
    Path(r"D:\Projects\ai-nids\results\cnn_torch\cnn_torch_binary_metrics.csv"),
]

RESULT_DIR = Path(
    r"D:\Projects\ai-nids\results\model_comparison"
)


def load_metrics(metrics_file: Path) -> pd.DataFrame:
    df = pd.read_csv(metrics_file)

    # 情况 1：Random Forest 当前格式：metric / score
    if "metric" in df.columns and "score" in df.columns:
        metrics = {
            "model": "Random Forest",
            "accuracy": df.loc[df["metric"] == "Accuracy", "score"].iloc[0],
            "precision": df.loc[df["metric"] == "Precision", "score"].iloc[0],
            "recall": df.loc[df["metric"] == "Recall", "score"].iloc[0],
            "f1_score": df.loc[df["metric"] == "F1 Score", "score"].iloc[0],
        }
        return pd.DataFrame([metrics])

    # 情况 2：其它模型格式：model / accuracy / precision / recall / f1_score
    return df[["model", "accuracy", "precision", "recall", "f1_score"]]


def main():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    metrics_dfs = []

    for metrics_file in METRICS_FILES:
        print(f"正在读取：{metrics_file}")
        metrics_dfs.append(load_metrics(metrics_file))

    comparison_df = pd.concat(metrics_dfs, ignore_index=True)

    output_csv = RESULT_DIR / "binary_model_comparison.csv"
    comparison_df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print("\n二分类模型对比表：")
    print(comparison_df)

    metric_columns = ["accuracy", "precision", "recall", "f1_score"]

    plt.figure(figsize=(11, 6))

    x = range(len(comparison_df))
    width = 0.18

    for i, metric in enumerate(metric_columns):
        positions = [pos + i * width for pos in x]
        plt.bar(
            positions,
            comparison_df[metric],
            width=width,
            label=metric,
        )

    center_positions = [
        pos + width * (len(metric_columns) - 1) / 2
        for pos in x
    ]

    plt.xticks(
        center_positions,
        comparison_df["model"],
        rotation=20,
        ha="right",
    )

    plt.ylim(0.0, 1.05)
    plt.ylabel("Score")
    plt.title("Binary Classification Model Comparison")
    plt.legend()
    plt.tight_layout()

    output_png = RESULT_DIR / "binary_model_comparison.png"
    plt.savefig(output_png, dpi=300)
    plt.close()

    print(f"\n模型对比 CSV 已保存到：{output_csv}")
    print(f"模型对比图已保存到：{output_png}")


if __name__ == "__main__":
    main()