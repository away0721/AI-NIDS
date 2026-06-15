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

OUTPUT_DIR = RESULT_ROOT / "error_pattern_comparison"

OUTPUT_SUMMARY_CSV_PATH = OUTPUT_DIR / "model_error_pattern_comparison.csv"
OUTPUT_ATTACK_TO_BENIGN_CSV_PATH = OUTPUT_DIR / "attack_to_benign_comparison.csv"
OUTPUT_BENIGN_TO_ATTACK_CSV_PATH = OUTPUT_DIR / "benign_to_attack_comparison.csv"

OUTPUT_TOTAL_ERROR_FIG_PATH = OUTPUT_DIR / "total_error_count_comparison.png"
OUTPUT_ATTACK_TO_BENIGN_FIG_PATH = OUTPUT_DIR / "attack_to_benign_count_comparison.png"
OUTPUT_BENIGN_TO_ATTACK_FIG_PATH = OUTPUT_DIR / "benign_to_attack_count_comparison.png"
OUTPUT_TOP_PATTERNS_FIG_PATH = OUTPUT_DIR / "top_error_patterns_comparison.png"


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


def summarize_model_errors(model_name: str, df: pd.DataFrame) -> dict:
    total_errors = int(df["count"].sum())

    attack_to_benign_count = int(
        df[
            (df["true_label"] != "BENIGN")
            & (df["predicted_label"] == "BENIGN")
        ]["count"].sum()
    )

    benign_to_attack_count = int(
        df[
            (df["true_label"] == "BENIGN")
            & (df["predicted_label"] != "BENIGN")
        ]["count"].sum()
    )

    attack_to_attack_count = int(
        df[
            (df["true_label"] != "BENIGN")
            & (df["predicted_label"] != "BENIGN")
        ]["count"].sum()
    )

    return {
        "model": model_name,
        "total_errors": total_errors,
        "attack_to_benign_errors": attack_to_benign_count,
        "benign_to_attack_errors": benign_to_attack_count,
        "attack_to_attack_errors": attack_to_attack_count,
    }


def plot_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    plt.figure(figsize=(10, 6))
    plt.bar(df[x_col], df[y_col])
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Model")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_top_patterns(all_patterns_df: pd.DataFrame) -> None:
    top_df = (
        all_patterns_df.sort_values(by="count", ascending=False)
        .head(20)
        .copy()
    )

    labels = (
        top_df["model"].astype(str)
        + " | "
        + top_df["error_type"].astype(str)
    )

    plt.figure(figsize=(14, 8))
    plt.barh(labels[::-1], top_df["count"][::-1])
    plt.title("Top Error Patterns Across Models")
    plt.xlabel("Error Count")
    plt.ylabel("Model | True Label -> Predicted Label")
    plt.tight_layout()
    plt.savefig(OUTPUT_TOP_PATTERNS_FIG_PATH)
    plt.close()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("正在读取各模型错误模式文件...")

    all_pattern_dfs = []
    summary_rows = []

    for model_name, csv_path in ERROR_PATTERN_FILES.items():
        print(f"读取 {model_name}: {csv_path}")

        df = load_error_patterns(model_name, csv_path)
        all_pattern_dfs.append(df)

        summary_rows.append(
            summarize_model_errors(
                model_name=model_name,
                df=df,
            )
        )

    all_patterns_df = pd.concat(all_pattern_dfs, ignore_index=True)
    summary_df = pd.DataFrame(summary_rows)

    print("\n模型错误总览：")
    print(summary_df)

    attack_to_benign_df = all_patterns_df[
        (all_patterns_df["true_label"] != "BENIGN")
        & (all_patterns_df["predicted_label"] == "BENIGN")
    ].copy()

    benign_to_attack_df = all_patterns_df[
        (all_patterns_df["true_label"] == "BENIGN")
        & (all_patterns_df["predicted_label"] != "BENIGN")
    ].copy()

    print("\nAttack -> BENIGN 漏报对比：")
    print(
        attack_to_benign_df[
            ["model", "true_label", "predicted_label", "error_type", "count"]
        ].sort_values(by=["model", "count"], ascending=[True, False])
    )

    print("\nBENIGN -> Attack 误报对比：")
    print(
        benign_to_attack_df[
            ["model", "true_label", "predicted_label", "error_type", "count"]
        ].sort_values(by=["model", "count"], ascending=[True, False])
    )

    summary_df.to_csv(
        OUTPUT_SUMMARY_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    attack_to_benign_df.to_csv(
        OUTPUT_ATTACK_TO_BENIGN_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    benign_to_attack_df.to_csv(
        OUTPUT_BENIGN_TO_ATTACK_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    plot_bar(
        df=summary_df,
        x_col="model",
        y_col="total_errors",
        title="Total Error Count Comparison",
        ylabel="Total Errors",
        output_path=OUTPUT_TOTAL_ERROR_FIG_PATH,
    )

    plot_bar(
        df=summary_df,
        x_col="model",
        y_col="attack_to_benign_errors",
        title="Attack -> BENIGN Error Count Comparison",
        ylabel="Attack -> BENIGN Errors",
        output_path=OUTPUT_ATTACK_TO_BENIGN_FIG_PATH,
    )

    plot_bar(
        df=summary_df,
        x_col="model",
        y_col="benign_to_attack_errors",
        title="BENIGN -> Attack Error Count Comparison",
        ylabel="BENIGN -> Attack Errors",
        output_path=OUTPUT_BENIGN_TO_ATTACK_FIG_PATH,
    )

    plot_top_patterns(all_patterns_df)

    print(f"\n错误总览 CSV 已保存到：{OUTPUT_SUMMARY_CSV_PATH}")
    print(f"Attack -> BENIGN 对比 CSV 已保存到：{OUTPUT_ATTACK_TO_BENIGN_CSV_PATH}")
    print(f"BENIGN -> Attack 对比 CSV 已保存到：{OUTPUT_BENIGN_TO_ATTACK_CSV_PATH}")
    print(f"错误总数对比图已保存到：{OUTPUT_TOTAL_ERROR_FIG_PATH}")
    print(f"Attack -> BENIGN 对比图已保存到：{OUTPUT_ATTACK_TO_BENIGN_FIG_PATH}")
    print(f"BENIGN -> Attack 对比图已保存到：{OUTPUT_BENIGN_TO_ATTACK_FIG_PATH}")
    print(f"Top 错误模式对比图已保存到：{OUTPUT_TOP_PATTERNS_FIG_PATH}")

    best_total = summary_df.loc[summary_df["total_errors"].idxmin(), "model"]
    best_attack_to_benign = summary_df.loc[
        summary_df["attack_to_benign_errors"].idxmin(),
        "model",
    ]
    best_benign_to_attack = summary_df.loc[
        summary_df["benign_to_attack_errors"].idxmin(),
        "model",
    ]

    print("\n最佳错误表现：")
    print(f"总错误数最少：{best_total}")
    print(f"攻击漏报最少：{best_attack_to_benign}")
    print(f"正常流量误报最少：{best_benign_to_attack}")


if __name__ == "__main__":
    main()