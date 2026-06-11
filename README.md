# AI-NIDS

AI-NIDS 是一个基于 CICIDS2017 数据集的网络入侵检测实验项目。

项目当前阶段主要完成了基于 Flow 特征的二分类入侵检测任务，即：

- BENIGN：正常流量
- ATTACK：攻击流量

当前 Baseline 模型为 Random Forest。

---





## Project Structure

```txt
AI-NIDS/
├── .venv/                         # Python virtual environment
├── data/
│   ├── raw/
│   │   └── MachineLearningCSV/
│   │       └── MachineLearningCVE/ # Original CICIDS2017 CSV files
│   └── processed/
│       └── binary_dataset.csv      # Cleaned binary classification dataset
│
├── docs/
│   ├── Day1.md
│   ├── Day2.md
│   ├── glossary.md
│   └── scripts.md
│
├── models/
│   └── random_forest_binary.pkl    # Saved Random Forest binary classifier
│
├── results/
│   └── random_forest/
│       ├── random_forest_binary_report.txt
│       ├── random_forest_binary_metrics.csv
│       ├── random_forest_binary_metrics.png
│       ├── random_forest_binary_confusion_matrix.png
│       ├── feature_importance_top20.csv
│       ├── feature_importance_top20.png
│       └── sample_predictions.csv
│
├── scripts/
│   ├── eda/
│   │   ├── eda.py
│   │   ├── dataset_overview.py
│   │   ├── label_overview.py
│   │   └── binary_label_overview.py
│   │
│   ├── data/
│   │   ├── build_binary_dataset.py
│   │   ├── check_binary_dataset.py
│   │   ├── prepare_xy_check.py
│   │   └── train_test_split_check.py
│   │
│   └── models/
│       ├── train_random_forest.py
│       └── predict_with_random_forest.py
│
├── requirements.txt
└── README.md
```
