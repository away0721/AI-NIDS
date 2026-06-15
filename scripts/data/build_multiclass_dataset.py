from pathlib import Path

import numpy as np
import pandas as pd


RAW_DATA_DIR = Path(
    r"D:\Projects\ai-nids\data\raw\MachineLearningCSV\MachineLearningCVE"
)

OUTPUT_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\multiclass_dataset.csv"
)


def map_attack_category(label: str) -> str:
    label = label.strip()

    if label == "BENIGN":
        return "BENIGN"

    if label in {
        "DoS Hulk",
        "DoS GoldenEye",
        "DoS slowloris",
        "DoS Slowhttptest",
    }:
        return "DoS"

    if label == "DDoS":
        return "DDoS"

    if label == "PortScan":
        return "PortScan"

    if label in {
        "FTP-Patator",
        "SSH-Patator",
    }:
        return "BruteForce"

    if label.startswith("Web Attack"):
        return "WebAttack"

    if label == "Bot":
        return "Bot"

    if label == "Infiltration":
        return "Infiltration"

    if label == "Heartbleed":
        return "Heartbleed"

    return "Other"


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"没有找到 CSV 文件：{RAW_DATA_DIR}")

    print("找到 CSV 文件数量：", len(csv_files))

    all_dfs = []

    for csv_file in csv_files:
        print(f"\n正在读取：{csv_file.name}")

        df = pd.read_csv(csv_file)

        # 去除列名前后的空格
        df.columns = df.columns.str.strip()

        if "Label" not in df.columns:
            raise ValueError(f"{csv_file.name} 中没有找到 Label 列")

        print("原始数据规模：", df.shape)

        # 构造攻击大类标签
        df["attack_category"] = df["Label"].apply(map_attack_category)

        print("当前文件攻击大类分布：")
        print(df["attack_category"].value_counts())

        all_dfs.append(df)

    print("\n正在合并全部 CSV 文件...")
    full_df = pd.concat(all_dfs, ignore_index=True)

    print("合并后数据规模：", full_df.shape)

    print("\n清洗前 attack_category 分布：")
    print(full_df["attack_category"].value_counts())

    before_rows = len(full_df)

    print("\n正在清洗 Infinity 和 NaN...")
    full_df = full_df.replace([np.inf, -np.inf], np.nan)
    full_df = full_df.dropna()

    print("正在清洗 Flow Duration < 0 的异常数据...")
    if "Flow Duration" in full_df.columns:
        full_df = full_df[full_df["Flow Duration"] >= 0]

    after_rows = len(full_df)

    print("\n清洗前行数：", before_rows)
    print("清洗后行数：", after_rows)
    print("删除行数：", before_rows - after_rows)

    # 删除原始 Label，保留 attack_category
    if "Label" in full_df.columns:
        full_df = full_df.drop(columns=["Label"])

    print("\n清洗后 attack_category 分布：")
    print(full_df["attack_category"].value_counts())

    print("\n清洗后 attack_category 比例：")
    print(full_df["attack_category"].value_counts(normalize=True))

    print("\n最终数据规模：", full_df.shape)

    full_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\n多分类数据集已保存到：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()