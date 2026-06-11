from pathlib import Path
import pandas as pd

DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\binary_dataset.csv"
)

df = pd.read_csv(DATA_PATH)

print("数据规模：")
print(df.shape)

print("\n前 5 行：")
print(df.head())

print("\n列名：")
print(df.columns.tolist())

print("\n二分类 Label 分布：")
print(df["binary_label"].value_counts())

print("\n是否存在缺失值：")
print(df.isnull().sum().sum())