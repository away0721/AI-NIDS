import pandas as pd

file_path = r"D:\Projects\ai-nids\data\raw\MachineLearningCSV\MachineLearningCVE\Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv"

df = pd.read_csv(file_path)

print(df[" Flow Duration"].min())

print((df[" Flow Duration"] < 0).sum())