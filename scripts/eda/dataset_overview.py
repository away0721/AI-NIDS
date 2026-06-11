from pathlib import Path
import pandas as pd

DATA_DIR = Path(
    r"D:\Projects\ai-nids\data\raw\MachineLearningCSV\MachineLearningCVE"
)

for csv_file in DATA_DIR.glob("*.csv"):
    print("=" * 80)
    print(csv_file.name)

    df = pd.read_csv(csv_file)

    print("Shape:", df.shape)

    labels = df[" Label"].value_counts()

    print("Labels:")
    print(labels)