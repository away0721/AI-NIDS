# Scripts Guide

本文档用于说明 AI-NIDS 项目中 `scripts/` 目录下各类脚本的作用、输入输出和推荐运行顺序。

项目脚本按照功能划分为四类：

```txt
scripts/
├── data/          # 数据集构建与数据检查
├── eda/           # 探索性数据分析
├── models/        # 模型训练、预测与模型对比
└── analysis/      # 错误模式分析、误报漏报分析
```

---

## 1. EDA Scripts

EDA 脚本用于理解 CICIDS2017 原始数据集，包括文件规模、标签分布、异常值和类别不平衡情况。

| Script                                 | Description                                                 |
| -------------------------------------- | ----------------------------------------------------------- |
| `scripts/eda/eda.py`                   | 对单个 CICIDS2017 CSV 文件进行探索性分析，查看数据规模、Label 分布、缺失值、异常值和基础统计信息 |
| `scripts/eda/dataset_overview.py`      | 遍历全部 CICIDS2017 CSV 文件，统计每个文件的数据规模和 Label 分布                |
| `scripts/eda/label_overview.py`        | 统计整个 CICIDS2017 数据集的全局多分类 Label 分布                          |
| `scripts/eda/binary_label_overview.py` | 将原始 Label 映射为 BENIGN / ATTACK，统计二分类标签分布                     |

### Key Findings

EDA 阶段发现：

```txt
1. CICIDS2017 包含 8 个主要 CSV 文件
2. 不同文件对应不同日期和攻击场景
3. BENIGN 样本数量最多
4. DoS Hulk、PortScan、DDoS 样本较多
5. Heartbleed、Infiltration、WebAttack Sql Injection 等类别样本极少
6. 数据集中存在明显类别不平衡问题
7. 原始数据中存在 NaN、Infinity 和 Flow Duration 负数异常值
```

---

## 2. Data Processing Scripts

数据处理脚本用于构建二分类和多分类数据集，并检查数据是否可以作为模型输入。

| Script                                     | Description                       |
| ------------------------------------------ | --------------------------------- |
| `scripts/data/build_binary_dataset.py`     | 构建 BENIGN vs ATTACK 二分类数据集        |
| `scripts/data/check_binary_dataset.py`     | 检查二分类数据集结构、标签分布和缺失值               |
| `scripts/data/prepare_xy_check.py`         | 检查二分类数据集是否可以正确拆分为特征矩阵 `X` 和标签 `y` |
| `scripts/data/train_test_split_check.py`   | 检查训练集和测试集划分是否正确，并验证类别比例是否保持一致     |
| `scripts/data/build_multiclass_dataset.py` | 构建多分类数据集，将原始攻击标签合并为 9 个攻击类别       |
| `scripts/data/check_multiclass_dataset.py` | 检查多分类数据集结构、类别分布、特征数量和缺失值          |

### Binary Dataset

二分类映射规则：

```txt
BENIGN -> 0
All attack labels -> 1
```

输出文件：

```txt
data/processed/binary_dataset.csv
```

数据规模：

```txt
2827761 rows × 79 columns
78 feature columns
1 label column: binary_label
```

清洗后二分类分布：

```txt
BENIGN / 0: 2271205
ATTACK / 1: 556556
```

### Multiclass Dataset

多分类标签列：

```txt
attack_category
```

输出文件：

```txt
data/processed/multiclass_dataset.csv
```

类别定义：

| ID | Class        |
| -: | ------------ |
|  0 | BENIGN       |
|  1 | Bot          |
|  2 | BruteForce   |
|  3 | DDoS         |
|  4 | DoS          |
|  5 | Heartbleed   |
|  6 | Infiltration |
|  7 | PortScan     |
|  8 | WebAttack    |

---

## 3. Binary Model Scripts

二分类模型脚本用于训练和评估 BENIGN vs ATTACK 入侵检测模型。

| Script                                        | Description                                                 |
| --------------------------------------------- | ----------------------------------------------------------- |
| `scripts/models/train_logistic_regression.py` | 训练 Logistic Regression 二分类 baseline 模型                      |
| `scripts/models/train_random_forest.py`       | 训练 Random Forest 二分类模型，并输出特征重要性                             |
| `scripts/models/mlp_torch_binary.py`          | 训练 PyTorch MLP 二分类模型，支持标准化、验证集和 Early Stopping              |
| `scripts/models/cnn_torch_binary.py`          | 训练 PyTorch 1D CNN 二分类模型，将 78 个 Flow 特征视为一维序列                |
| `scripts/models/compare_binary_models.py`     | 汇总 Logistic Regression、Random Forest、MLP 和 CNN 的二分类结果并生成对比图 |

### Binary Prediction Scripts

| Script                                         | Description                                |
| ---------------------------------------------- | ------------------------------------------ |
| `scripts/models/predict_with_random_forest.py` | 加载 Random Forest 二分类模型，对样本 Flow 进行预测       |
| `scripts/models/predict_with_mlp_torch.py`     | 加载 PyTorch MLP 二分类模型和 Scaler，对样本 Flow 进行预测 |
| `scripts/models/predict_with_cnn_torch.py`     | 加载 PyTorch CNN 二分类模型和 Scaler，对样本 Flow 进行预测 |

### Binary Result Files

主要输出目录：

```txt
results/logistic_regression/
results/random_forest/
results/mlp_torch/
results/cnn_torch/
results/model_comparison/
```

核心对比文件：

```txt
results/model_comparison/binary_model_comparison.csv
results/model_comparison/binary_model_comparison.png
```

当前二分类模型对比结果：

| Model               | Accuracy | Precision | Recall | F1 Score |
| ------------------- | -------: | --------: | -----: | -------: |
| Random Forest       |   0.9991 |    0.9967 | 0.9986 |   0.9976 |
| Logistic Regression |   0.9162 |    0.7129 | 0.9614 |   0.8187 |
| PyTorch MLP         |   0.9908 |    0.9921 | 0.9607 |   0.9762 |
| PyTorch CNN         |   0.9702 |    0.9246 | 0.9239 |   0.9243 |

### Binary Stage Conclusion

在二分类任务中，Random Forest 表现最好，PyTorch MLP 是当前深度学习模型中表现最好的模型。CNN 在当前表格型 Flow 特征上没有明显超过 MLP 和 Random Forest。

---

## 4. Multiclass Model Scripts

多分类模型脚本用于训练和评估 9 类网络流量分类模型。

| Script                                                              | Description                                                       |
| ------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `scripts/models/multiclass/train_multiclass_logistic_regression.py` | 训练多分类 Logistic Regression 模型，使用 `StandardScaler` 和 `LabelEncoder` |
| `scripts/models/multiclass/train_multiclass_random_forest.py`       | 训练多分类 Random Forest 模型，并输出特征重要性                                   |
| `scripts/models/multiclass/train_multiclass_mlp.py`                 | 训练 PyTorch MLP 多分类模型，使用 `CrossEntropyLoss`                        |
| `scripts/models/multiclass/train_multiclass_cnn.py`                 | 训练 PyTorch 1D CNN 多分类模型，输入形状为 `[N, 1, 78]`                        |
| `scripts/models/multiclass/compare_multiclass_models.py`            | 汇总 Logistic Regression、Random Forest、MLP 和 CNN 的多分类指标并生成对比图       |

### Multiclass Prediction Scripts

| Script                                                                     | Description                                                |
| -------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `scripts/models/multiclass/predict_with_multiclass_logistic_regression.py` | 加载多分类 Logistic Regression 模型、Scaler 和 LabelEncoder，对样本进行预测 |
| `scripts/models/multiclass/predict_with_multiclass_random_forest.py`       | 加载多分类 Random Forest 模型和 LabelEncoder，对样本进行预测               |
| `scripts/models/multiclass/predict_with_multiclass_mlp.py`                 | 加载多分类 MLP 模型、Scaler 和 LabelEncoder，对样本进行预测                 |
| `scripts/models/multiclass/predict_with_multiclass_cnn.py`                 | 加载多分类 CNN 模型、Scaler 和 LabelEncoder，对样本进行预测                 |

### Multiclass Result Files

主要输出目录：

```txt
results/multiclass/logistic_regression/
results/multiclass/random_forest/
results/multiclass/mlp_torch/
results/multiclass/cnn_torch/
results/multiclass/model_comparison/
```

核心对比文件：

```txt
results/multiclass/model_comparison/multiclass_model_comparison.csv
results/multiclass/model_comparison/multiclass_model_comparison.png
```

多分类阶段主要观察指标：

```txt
Accuracy
Macro Precision
Macro Recall
Macro F1
Weighted Precision
Weighted Recall
Weighted F1
```

### Multiclass Stage Conclusion

在多分类任务中，Random Forest 在 CICIDS2017 的 Flow 表格特征上表现非常稳定，整体指标优于大部分深度学习 baseline。MLP 和 CNN 能够完成多分类任务，但对少数类攻击存在漏报问题。

---

## 5. Class Imbalance Experiment Scripts

类别不平衡实验脚本用于研究 weighted loss 对少数类攻击检测能力的影响。

| Script                                                                  | Description                                |
| ----------------------------------------------------------------------- | ------------------------------------------ |
| `scripts/models/multiclass/train_multiclass_mlp_weighted.py`            | 训练使用 balanced class weight 的 Weighted MLP  |
| `scripts/models/multiclass/train_multiclass_mlp_weighted_clipped.py`    | 训练裁剪最大类别权重的 Clipped Weighted MLP           |
| `scripts/models/multiclass/compare_mlp_weight_experiments.py`           | 对比 MLP、Weighted MLP 和 Clipped Weighted MLP |
| `scripts/models/multiclass/train_multiclass_cnn_weighted.py`            | 训练使用 balanced class weight 的 Weighted CNN  |
| `scripts/models/multiclass/train_multiclass_cnn_weighted_clipped.py`    | 训练裁剪最大类别权重的 Clipped Weighted CNN           |
| `scripts/models/multiclass/compare_cnn_weight_experiments.py`           | 对比 CNN、Weighted CNN 和 Clipped Weighted CNN |
| `scripts/models/multiclass/compare_deep_learning_weight_experiments.py` | 汇总所有深度学习权重实验结果                             |

### Class Imbalance Result Files

主要输出目录：

```txt
results/multiclass/mlp_torch_weighted/
results/multiclass/mlp_torch_weighted_clipped/
results/multiclass/cnn_torch_weighted/
results/multiclass/cnn_torch_weighted_clipped/
results/multiclass/mlp_weight_experiments/
results/multiclass/cnn_weight_experiments/
results/multiclass/deep_learning_weight_experiments/
```

核心对比文件：

```txt
results/multiclass/mlp_weight_experiments/mlp_weight_experiments_comparison.csv
results/multiclass/cnn_weight_experiments/cnn_weight_experiments_comparison.csv
results/multiclass/deep_learning_weight_experiments/deep_learning_weight_experiments_comparison.csv
```

### Class Imbalance Stage Conclusion

类别权重能够显著提升少数类攻击的 Recall，但会引入更多 BENIGN -> Attack 误报。裁剪类别权重可以缓解直接 weighted loss 带来的误报问题，但仍然存在误报增加的副作用。

核心结论：

```txt
Reducing missed attacks usually increases false alarms.
```

---

## 6. Error Pattern Analysis Scripts

错误模式分析脚本用于进一步分析模型具体错在哪里，而不仅仅依赖 Accuracy、Macro F1 或 Weighted F1。

| Script                                                                       | Description                                            |
| ---------------------------------------------------------------------------- | ------------------------------------------------------ |
| `scripts/analysis/multiclass/analyze_cnn_error_patterns.py`                  | 分析原始 CNN 的错误模式，统计 Top 错误类型、攻击漏报和正常流量误报                 |
| `scripts/analysis/multiclass/analyze_random_forest_error_patterns.py`        | 分析 Random Forest 的错误模式                                 |
| `scripts/analysis/multiclass/analyze_clipped_weighted_cnn_error_patterns.py` | 分析 Clipped Weighted CNN 的错误模式                          |
| `scripts/analysis/multiclass/compare_error_patterns.py`                      | 对比 CNN、Random Forest 和 Clipped Weighted CNN 的总错误、漏报和误报 |
| `scripts/analysis/multiclass/compare_class_error_rates.py`                   | 按真实类别统计不同模型的错误率和 Attack -> BENIGN 比例                   |
| `scripts/analysis/multiclass/generate_error_analysis_summary.py`             | 自动生成 Day7 错误分析总结 Markdown 和关键发现 CSV                    |

### Error Types

| Error Type         | Meaning              |
| ------------------ | -------------------- |
| `Attack -> BENIGN` | 攻击流量被预测为正常流量，即攻击漏报   |
| `BENIGN -> Attack` | 正常流量被预测为攻击流量，即正常流量误报 |
| `Attack -> Attack` | 攻击流量被预测为错误的攻击类别      |

### Error Analysis Result Files

主要输出目录：

```txt
results/multiclass/cnn_error_patterns/
results/multiclass/random_forest_error_patterns/
results/multiclass/clipped_weighted_cnn_error_patterns/
results/multiclass/error_pattern_comparison/
results/multiclass/class_error_rate_comparison/
results/multiclass/error_analysis_summary/
```

核心结果文件：

```txt
results/multiclass/error_pattern_comparison/model_error_pattern_comparison.csv
results/multiclass/class_error_rate_comparison/class_error_rate_comparison.csv
results/multiclass/error_analysis_summary/day7_error_analysis_summary.md
results/multiclass/error_analysis_summary/day7_key_findings.csv
results/multiclass/error_analysis_summary/day7_highest_class_errors.csv
```

### Error Pattern Summary

| Model                | Total Errors | Attack -> BENIGN Errors | BENIGN -> Attack Errors | Attack -> Attack Errors |
| -------------------- | -----------: | ----------------------: | ----------------------: | ----------------------: |
| CNN                  |         1933 |                     800 |                    1097 |                      36 |
| Random Forest        |          636 |                     316 |                     305 |                      15 |
| Clipped Weighted CNN |        24757 |                      61 |                   24522 |                     174 |

### Error Analysis Conclusion

| Metric                         | Best Model           |
| ------------------------------ | -------------------- |
| Fewest total errors            | Random Forest        |
| Fewest Attack -> BENIGN errors | Clipped Weighted CNN |
| Fewest BENIGN -> Attack errors | Random Forest        |

结论：

```txt
Random Forest 整体错误最少，适合低误报场景。
Clipped Weighted CNN 攻击漏报最少，适合高敏感度场景。
CNN 对 WebAttack 和 Bot 等少数类攻击仍存在明显漏报。
```

---

## 7. Recommended Running Order

如果从零复现实验，推荐按以下顺序运行。

### 1. Explore Dataset

```powershell
python scripts/eda/dataset_overview.py
python scripts/eda/label_overview.py
python scripts/eda/binary_label_overview.py
```

### 2. Build Datasets

```powershell
python scripts/data/build_binary_dataset.py
python scripts/data/check_binary_dataset.py
python scripts/data/prepare_xy_check.py
python scripts/data/train_test_split_check.py

python scripts/data/build_multiclass_dataset.py
python scripts/data/check_multiclass_dataset.py
```

### 3. Train Binary Models

```powershell
python scripts/models/train_logistic_regression.py
python scripts/models/train_random_forest.py
python scripts/models/mlp_torch_binary.py
python scripts/models/cnn_torch_binary.py
python scripts/models/compare_binary_models.py
```

### 4. Run Binary Prediction Checks

```powershell
python scripts/models/predict_with_random_forest.py
python scripts/models/predict_with_mlp_torch.py
python scripts/models/predict_with_cnn_torch.py
```

### 5. Train Multiclass Models

```powershell
python scripts/models/multiclass/train_multiclass_logistic_regression.py
python scripts/models/multiclass/train_multiclass_random_forest.py
python scripts/models/multiclass/train_multiclass_mlp.py
python scripts/models/multiclass/train_multiclass_cnn.py
python scripts/models/multiclass/compare_multiclass_models.py
```

### 6. Run Multiclass Prediction Checks

```powershell
python scripts/models/multiclass/predict_with_multiclass_logistic_regression.py
python scripts/models/multiclass/predict_with_multiclass_random_forest.py
python scripts/models/multiclass/predict_with_multiclass_mlp.py
python scripts/models/multiclass/predict_with_multiclass_cnn.py
```

### 7. Run Class Imbalance Experiments

```powershell
python scripts/models/multiclass/train_multiclass_mlp_weighted.py
python scripts/models/multiclass/train_multiclass_mlp_weighted_clipped.py
python scripts/models/multiclass/compare_mlp_weight_experiments.py

python scripts/models/multiclass/train_multiclass_cnn_weighted.py
python scripts/models/multiclass/train_multiclass_cnn_weighted_clipped.py
python scripts/models/multiclass/compare_cnn_weight_experiments.py

python scripts/models/multiclass/compare_deep_learning_weight_experiments.py
```

### 8. Run Error Pattern Analysis

```powershell
python scripts/analysis/multiclass/analyze_cnn_error_patterns.py
python scripts/analysis/multiclass/analyze_random_forest_error_patterns.py
python scripts/analysis/multiclass/analyze_clipped_weighted_cnn_error_patterns.py
python scripts/analysis/multiclass/compare_error_patterns.py
python scripts/analysis/multiclass/compare_class_error_rates.py
python scripts/analysis/multiclass/generate_error_analysis_summary.py
```

---

## 8. Notes

Large files are intentionally excluded from GitHub:

```txt
data/
models/
.venv/
```

This repository keeps source code, documentation, and selected experiment results. Raw datasets and trained model artifacts should be stored locally.
