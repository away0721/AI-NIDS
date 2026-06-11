from pathlib import Path

import numpy as np
import pandas as pd


RAW_DATA_DIR = Path(
    r"D:\Projects\ai-nids\data\raw\MachineLearningCSV\MachineLearningCVE"
)

OUTPUT_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\binary_dataset.csv"
)


def main():
    dataframes = []

    for csv_file in RAW_DATA_DIR.glob("*.csv"):
        print(f"正在读取：{csv_file.name}")

        df = pd.read_csv(csv_file)

        # 去掉列名前后的空格
        # CICIDS2017 里有些列名像 " Label"，前面带空格
        df.columns = df.columns.str.strip()

        # 原始 Label 转换为二分类标签
        # BENIGN -> 0
        # 其它所有攻击类型 -> 1
        df["binary_label"] = df["Label"].apply(
            lambda label: 0 if label == "BENIGN" else 1
        )

        dataframes.append(df)

    print("\n正在合并全部 CSV...")
    all_data = pd.concat(dataframes, ignore_index=True)

    print("合并后数据规模：")
    print(all_data.shape)

    print("\n开始基础数据清洗...")

    before_rows = len(all_data)

    # 将 Infinity 和 -Infinity 替换为 NaN
    all_data = all_data.replace([np.inf, -np.inf], np.nan)

    # 删除存在 NaN 的行
    all_data = all_data.dropna()

    # 删除 Flow Duration 小于 0 的异常行
    all_data = all_data[all_data["Flow Duration"] >= 0]

    after_rows = len(all_data)

    print(f"清洗前行数：{before_rows}")
    print(f"清洗后行数：{after_rows}")
    print(f"删除行数：{before_rows - after_rows}")

    print("\n清洗后二分类 Label 分布：")
    print(all_data["binary_label"].value_counts())

    # 删除原始多分类 Label
    # 最终训练二分类模型时，只保留特征列 + binary_label
    all_data = all_data.drop(columns=["Label"])

    print("\n最终数据规模：")
    print(all_data.shape)

    print("\n正在保存处理后的二分类数据集...")
    all_data.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"保存完成：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()