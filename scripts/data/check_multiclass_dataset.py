from pathlib import Path

import pandas as pd


DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\multiclass_dataset.csv"
)


def main():
    print("正在读取多分类数据集...")
    df = pd.read_csv(DATA_PATH)

    print("\n数据规模：")
    print(df.shape)

    print("\n前 5 行数据：")
    print(df.head())

    print("\n列名数量：")
    print(len(df.columns))

    print("\n标签列是否存在：")
    print("attack_category" in df.columns)

    print("\n特征列数量：")
    feature_columns = [col for col in df.columns if col != "attack_category"]
    print(len(feature_columns))

    print("\n类别数量：")
    print(df["attack_category"].nunique())

    print("\n类别名称：")
    print(sorted(df["attack_category"].unique()))

    print("\n类别分布：")
    print(df["attack_category"].value_counts())

    print("\n类别比例：")
    print(df["attack_category"].value_counts(normalize=True))

    print("\n缺失值总数：")
    print(df.isna().sum().sum())

    print("\n检查完成。")


if __name__ == "__main__":
    main()