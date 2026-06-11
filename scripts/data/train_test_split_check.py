from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\binary_dataset.csv"
)


def main():
    df = pd.read_csv(DATA_PATH)

    X = df.drop(columns=["binary_label"])
    y = df["binary_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("原始数据规模：")
    print(df.shape)

    print("\n特征矩阵 X：")
    print(X.shape)

    print("\n标签 y：")
    print(y.shape)

    print("\n训练集 X_train：")
    print(X_train.shape)

    print("\n测试集 X_test：")
    print(X_test.shape)

    print("\n训练集 y_train：")
    print(y_train.shape)

    print("\n测试集 y_test：")
    print(y_test.shape)

    print("\n训练集 Label 分布：")
    print(y_train.value_counts())
    print(y_train.value_counts(normalize=True))

    print("\n测试集 Label 分布：")
    print(y_test.value_counts())
    print(y_test.value_counts(normalize=True))


if __name__ == "__main__":
    main()