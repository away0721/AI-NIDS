from pathlib import Path
import pandas as pd

DATA_DIR = Path(
    r"D:\Projects\ai-nids\data\raw\MachineLearningCSV\MachineLearningCVE"
)

total_labels = {}

for csv_file in DATA_DIR.glob("*.csv"):
    print(f"正在读取：{csv_file.name}")
    df = pd.read_csv(csv_file)
    counts = df[" Label"].value_counts()

    for label, count in counts.items():
        total_labels[label] = total_labels.get(label, 0) + int(count)

print("\n整个 CICIDS2017 数据集 Label 总分布：")
for label, count in sorted(total_labels.items(), key=lambda x: x[1], reverse=True):
    print(f"{label}: {count}")