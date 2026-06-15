from pathlib import Path

import pandas as pd


RESULT_ROOT = Path(r"D:\Projects\ai-nids\results\multiclass")

ERROR_OVERVIEW_PATH = (
    RESULT_ROOT
    / "error_pattern_comparison"
    / "model_error_pattern_comparison.csv"
)

CLASS_ERROR_RATE_PATH = (
    RESULT_ROOT
    / "class_error_rate_comparison"
    / "class_error_rate_comparison.csv"
)

OUTPUT_DIR = RESULT_ROOT / "error_analysis_summary"
OUTPUT_MARKDOWN_PATH = OUTPUT_DIR / "day7_error_analysis_summary.md"
OUTPUT_KEY_FINDINGS_CSV_PATH = OUTPUT_DIR / "day7_key_findings.csv"
OUTPUT_HIGHEST_CLASS_ERROR_CSV_PATH = OUTPUT_DIR / "day7_highest_class_errors.csv"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"找不到文件：{path}")

    df = pd.read_csv(path)
    df.columns = [column.strip() for column in df.columns]
    return df


def format_value(value) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def build_markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return ""

    headers = list(df.columns)
    lines = []

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for _, row in df.iterrows():
        values = [format_value(row[column]) for column in headers]
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("正在读取错误分析结果...")

    overview_df = load_csv(ERROR_OVERVIEW_PATH)
    class_error_df = load_csv(CLASS_ERROR_RATE_PATH)

    print("\n模型错误总览：")
    print(overview_df)

    print("\n类别错误率结果：")
    print(class_error_df)

    best_total_error_model = overview_df.loc[
        overview_df["total_errors"].idxmin(),
        "model",
    ]

    best_attack_to_benign_model = overview_df.loc[
        overview_df["attack_to_benign_errors"].idxmin(),
        "model",
    ]

    best_benign_to_attack_model = overview_df.loc[
        overview_df["benign_to_attack_errors"].idxmin(),
        "model",
    ]

    worst_total_error_model = overview_df.loc[
        overview_df["total_errors"].idxmax(),
        "model",
    ]

    key_findings = [
        {
            "finding": "Total errors fewest",
            "model": best_total_error_model,
            "meaning": "整体错误数量最少，综合稳定性最好",
        },
        {
            "finding": "Attack -> BENIGN errors fewest",
            "model": best_attack_to_benign_model,
            "meaning": "攻击漏报最少，更适合减少漏报",
        },
        {
            "finding": "BENIGN -> Attack errors fewest",
            "model": best_benign_to_attack_model,
            "meaning": "正常流量误报最少，更适合降低告警噪声",
        },
        {
            "finding": "Total errors most",
            "model": worst_total_error_model,
            "meaning": "整体错误数量最多，需要关注误报或漏报副作用",
        },
    ]

    key_findings_df = pd.DataFrame(key_findings)

    highest_class_error_rows = []

    for model_name in overview_df["model"]:
        model_df = class_error_df[class_error_df["model"] == model_name]

        worst_class_row = model_df.loc[
            model_df["class_error_rate"].idxmax()
        ]

        attack_model_df = model_df[model_df["true_label"] != "BENIGN"]

        worst_attack_to_benign_row = attack_model_df.loc[
            attack_model_df["predicted_as_benign_rate"].idxmax()
        ]

        highest_class_error_rows.append(
            {
                "model": model_name,
                "highest_error_class": worst_class_row["true_label"],
                "highest_error_rate": worst_class_row["class_error_rate"],
                "highest_error_count": int(worst_class_row["total_error_count"]),
                "highest_error_support": int(worst_class_row["support"]),
                "highest_attack_to_benign_class": worst_attack_to_benign_row[
                    "true_label"
                ],
                "highest_attack_to_benign_rate": worst_attack_to_benign_row[
                    "predicted_as_benign_rate"
                ],
                "highest_attack_to_benign_count": int(
                    worst_attack_to_benign_row["predicted_as_benign_count"]
                ),
                "highest_attack_to_benign_support": int(
                    worst_attack_to_benign_row["support"]
                ),
            }
        )

    highest_class_error_df = pd.DataFrame(highest_class_error_rows)

    key_findings_df.to_csv(
        OUTPUT_KEY_FINDINGS_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    highest_class_error_df.to_csv(
        OUTPUT_HIGHEST_CLASS_ERROR_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    markdown_lines = [
        "# Day7 Error Analysis Summary",
        "",
        "## 1. Model Error Overview",
        "",
        "This summary compares the error patterns of CNN, Random Forest, and Clipped Weighted CNN.",
        "",
        build_markdown_table(overview_df),
        "",
        "## 2. Key Findings",
        "",
        build_markdown_table(key_findings_df),
        "",
        "## 3. Highest Error Classes by Model",
        "",
        build_markdown_table(highest_class_error_df),
        "",
        "## 4. Main Observations",
        "",
        "- Random Forest has the fewest total errors and the fewest BENIGN -> Attack false positives.",
        "- Clipped Weighted CNN has the fewest Attack -> BENIGN false negatives, which means it is more sensitive to attacks.",
        "- CNN has higher total errors than Random Forest and shows obvious minority-class false negatives, especially for WebAttack and Bot.",
        "- Clipped Weighted CNN greatly reduces attack missed detection, but it introduces many BENIGN -> Attack false positives.",
        "- The results confirm a clear trade-off: reducing false negatives usually increases false positives.",
        "",
        "## 5. Generated Result Files",
        "",
        "```txt",
        "results/multiclass/cnn_error_patterns/",
        "results/multiclass/random_forest_error_patterns/",
        "results/multiclass/clipped_weighted_cnn_error_patterns/",
        "results/multiclass/error_pattern_comparison/",
        "results/multiclass/class_error_rate_comparison/",
        "results/multiclass/error_analysis_summary/",
        "```",
        "",
    ]

    markdown = "\n".join(markdown_lines)

    OUTPUT_MARKDOWN_PATH.write_text(markdown, encoding="utf-8")

    print("\n关键发现：")
    print(key_findings_df)

    print("\n各模型错误率最高类别：")
    print(highest_class_error_df)

    print(f"\nDay7 错误分析 Markdown 已保存到：{OUTPUT_MARKDOWN_PATH}")
    print(f"Day7 关键发现 CSV 已保存到：{OUTPUT_KEY_FINDINGS_CSV_PATH}")
    print(f"Day7 最高错误类别 CSV 已保存到：{OUTPUT_HIGHEST_CLASS_ERROR_CSV_PATH}")


if __name__ == "__main__":
    main()