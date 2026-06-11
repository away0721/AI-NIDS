from pathlib import Path
import pandas as pd

DATA_DIR = Path(
    r"D:\Projects\ai-nids\data\raw\MachineLearningCSV\MachineLearningCVE"
)

benign_count = 0
attack_count = 0

for csv_file in DATA_DIR.glob("*.csv"):
    print(f"正在读取：{csv_file.name}")

    df = pd.read_csv(csv_file)

    labels = df[" Label"]

    benign_count += (labels == "BENIGN").sum()
    attack_count += (labels != "BENIGN").sum()

total_count = benign_count + attack_count

print("\n二分类 Label 分布：")
print(f"BENIGN / 0: {benign_count}")
print(f"ATTACK / 1: {attack_count}")
print(f"TOTAL: {total_count}")

print("\n比例：")
print(f"BENIGN: {benign_count / total_count:.4f}")
print(f"ATTACK: {attack_count / total_count:.4f}")