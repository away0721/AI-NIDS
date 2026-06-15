from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


RESULT_ROOT = Path(r"D:\Projects\ai-nids\results\multiclass")

ERROR_PATTERN_FILES = {
    "CNN": RESULT_ROOT
    / "cnn_error_patterns"
    / "cnn_error_pattern_summary.csv",
    "Random Forest": RESULT_ROOT
    / "random_forest_error_patterns"
    / "random_forest_error_pattern_summary.csv",
    "Clipped Weighted CNN": RESULT_ROOT
    / "clipped_weighted_cnn_error_patterns"
    / "clipped_weighted_cnn_error_pattern_summary.csv",
}

OUTPUT_DIR = RESULT_ROOT / "class_error_rate_comparison"

OUTPUT_CSV_PATH = OUTPUT_DIR / "class_error_rate_comparison.csv"
OUTPUT_ERROR_RATE_FIG_PATH = OUTPUT_DIR / "class_error_rate_comparison.png"
OUTPUT_ATTACK_TO_BENIGN_RATE_FIG_PATH = (
    OUTPUT_DIR / "attack_to_benign_rate_comparison.png"
)

# 测试集 support，来自 train_test_split(test_size=0.2, stratify=y) 后的 classification report
CLASS_SUPPORT = {
    "BENIGN": 454242,
    "Bot": 391,
    "BruteForce": 2766,
    "DDoS": 25605,
    "DoS": 50343,
    "Heartbleed": 2,
    "Infiltration": 7,
    "PortScan": 31761,
    "WebAttack": 436,
}


def load_error_patterns(model_name: str, csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"找不到错误模式文件：{csv_path}")

    df = pd.read_csv(csv_path)
    df.columns = [column.strip() for column in df.columns]

    required_columns = {"true_label", "predicted_label", "error_type", "count"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"{csv_path} 缺少必要列：{missing_columns}，当前列：{df.columns.tolist()}"
        )

    df["model"] = model_name
    return df


def build_class_error_summary(model_name: str, error_df: pd.DataFrame) -> list[dict]:
    rows = []

    for class_name, support in CLASS_SUPPORT.items():
        class_error_df = error_df[error_df["true_label"] == class_name]

        total_error_count = int(class_error_df["count"].sum())

        predicted_as_benign_count = int(
            class_error_df[class_error_df["predicted_label"] == "BENIGN"][
                "count"
            ].sum()
        )

        predicted_as_attack_count = int(
            class_error_df[class_error_df["predicted_label"] != "BENIGN"][
                "count"
            ].sum()
        )

        class_error_rate = total_error_count / support if support > 0 else 0.0
        predicted_as_benign_rate = (
            predicted_as_benign_count / support if support > 0 else 0.0
        )
        predicted_as_attack_rate = (
            predicted_as_attack_count / support if support > 0 else 0.0
        )

        rows.append(
            {
                "model": model_name,
                "true_label": class_name,
                "support": support,
                "total_error_count": total_error_count,
                "class_error_rate": class_error_rate,
                "predicted_as_benign_count": predicted_as_benign_count,
                "predicted_as_benign_rate": predicted_as_benign_rate,
                "predicted_as_attack_count": predicted_as_attack_count,
                "predicted_as_attack_rate": predicted_as_attack_rate,
            }
        )

    return rows


def plot_metric_by_class(
    summary_df: pd.DataFrame,
    metric_column: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    pivot_df = summary_df.pivot(
        index="true_label",
        columns="model",
        values=metric_column,
    )

    # 只保留当前图中实际存在的类别，避免 attack_df 过滤掉 BENIGN 后报错
    class_order = [
        class_name
        for class_name in CLASS_SUPPORT.keys()
        if class_name in pivot_df.index
    ]

    pivot_df = pivot_df.loc[class_order]

    plt.figure(figsize=(14, 7))
    pivot_df.plot(kind="bar", figsize=(14, 7))

    plt.title(title)
    plt.xlabel("True Label")
    plt.ylabel(ylabel)
    plt.xticks(rotation=30, ha="right")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("正在读取各模型错误模式文件...")

    rows = []

    for model_name, csv_path in ERROR_PATTERN_FILES.items():
        print(f"读取 {model_name}: {csv_path}")

        error_df = load_error_patterns(
            model_name=model_name,
            csv_path=csv_path,
        )

        rows.extend(
            build_class_error_summary(
                model_name=model_name,
                error_df=error_df,
            )
        )

    summary_df = pd.DataFrame(rows)

    summary_df = summary_df[
        [
            "model",
            "true_label",
            "support",
            "total_error_count",
            "class_error_rate",
            "predicted_as_benign_count",
            "predicted_as_benign_rate",
            "predicted_as_attack_count",
            "predicted_as_attack_rate",
        ]
    ]

    print("\n按真实类别统计错误率：")
    print(summary_df)

    summary_df.to_csv(
        OUTPUT_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    plot_metric_by_class(
        summary_df=summary_df,
        metric_column="class_error_rate",
        title="Class Error Rate Comparison",
        ylabel="Error Rate",
        output_path=OUTPUT_ERROR_RATE_FIG_PATH,
    )

    attack_df = summary_df[summary_df["true_label"] != "BENIGN"].copy()

    plot_metric_by_class(
        summary_df=attack_df,
        metric_column="predicted_as_benign_rate",
        title="Attack -> BENIGN Rate Comparison",
        ylabel="Attack -> BENIGN Rate",
        output_path=OUTPUT_ATTACK_TO_BENIGN_RATE_FIG_PATH,
    )

    print(f"\n类别错误率对比 CSV 已保存到：{OUTPUT_CSV_PATH}")
    print(f"类别错误率对比图已保存到：{OUTPUT_ERROR_RATE_FIG_PATH}")
    print(f"Attack -> BENIGN 比例对比图已保存到：{OUTPUT_ATTACK_TO_BENIGN_RATE_FIG_PATH}")

    print("\n每个模型各自错误率最高的类别：")
    for model_name in ERROR_PATTERN_FILES.keys():
        model_df = summary_df[summary_df["model"] == model_name]
        worst_row = model_df.loc[model_df["class_error_rate"].idxmax()]

        print(
            f"{model_name}: "
            f"{worst_row['true_label']} "
            f"error_rate={worst_row['class_error_rate']:.4f}, "
            f"errors={int(worst_row['total_error_count'])}, "
            f"support={int(worst_row['support'])}"
        )

    print("\n每个模型攻击被判成 BENIGN 比例最高的类别：")
    for model_name in ERROR_PATTERN_FILES.keys():
        model_df = summary_df[
            (summary_df["model"] == model_name)
            & (summary_df["true_label"] != "BENIGN")
        ]

        worst_row = model_df.loc[model_df["predicted_as_benign_rate"].idxmax()]

        print(
            f"{model_name}: "
            f"{worst_row['true_label']} "
            f"attack_to_benign_rate={worst_row['predicted_as_benign_rate']:.4f}, "
            f"errors={int(worst_row['predicted_as_benign_count'])}, "
            f"support={int(worst_row['support'])}"
        )


if __name__ == "__main__":
    main()