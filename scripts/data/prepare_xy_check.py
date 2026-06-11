from pathlib import Path
import pandas as pd

DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\binary_dataset.csv"
)

df = pd.read_csv(DATA_PATH)

X = df.drop(columns=["binary_label"])
y = df["binary_label"]

print("原始数据规模：")
print(df.shape)

print("\n特征矩阵 X 的规模：")
print(X.shape)

print("\n标签 y 的规模：")
print(y.shape)

print("\nX 的前 5 个列名：")
print(X.columns[:5].tolist())

print("\ny 的前 5 个值：")
print(y.head().tolist())

print("\ny 的分布：")
print(y.value_counts())