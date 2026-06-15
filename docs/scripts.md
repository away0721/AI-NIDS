# Scripts 说明文档

本文档用于记录 AI-NIDS 项目中 `scripts/` 目录下现有脚本的作用、输入输出文件以及推荐运行顺序，避免后续忘记每个文件的用途。

---

## 1. EDA 脚本

EDA 脚本主要用于探索 CICIDS2017 原始数据集，包括单文件分析、全局 Label 分布统计和二分类标签分布统计。

---

### scripts/eda/eda.py

作用：

用于对单个 CICIDS2017 CSV 文件进行探索性数据分析。

主要功能：

* 读取指定 CSV 文件
* 查看数据规模
* 查看 Label 分布
* 查看基础统计信息
* 查看缺失值
* 查看异常值

当前主要分析过的文件：

* `Monday-WorkingHours.pcap_ISCX.csv`
* `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`

重要发现：

* Monday 文件全部为 `BENIGN`
* PortScan 文件包含 `BENIGN` 和 `PortScan`
* `Flow Bytes/s` 存在少量缺失值
* `Flow Duration` 存在负数异常值

---

### scripts/eda/dataset_overview.py

作用：

用于遍历 CICIDS2017 的全部 CSV 文件，查看每个文件的数据规模和 Label 分布。

主要功能：

* 遍历 `MachineLearningCVE` 目录下所有 CSV 文件
* 输出每个 CSV 的 shape
* 输出每个 CSV 的 Label 分布

重要发现：

* CICIDS2017 一共包含 8 个 CSV 文件
* 不同文件对应不同日期和攻击场景
* 有些文件只包含正常流量
* 有些文件包含正常流量和攻击流量
* 数据集中存在明显类别不平衡问题

---

### scripts/eda/label_overview.py

作用：

用于统计整个 CICIDS2017 数据集的全局 Label 分布。

主要功能：

* 遍历全部 CSV 文件
* 累加每个 Label 的样本数量
* 输出整个数据集的 Label 总分布

当前统计结果：

```txt
BENIGN: 2273097
DoS Hulk: 231073
PortScan: 158930
DDoS: 128027
DoS GoldenEye: 10293
FTP-Patator: 7938
SSH-Patator: 5897
DoS slowloris: 5796
DoS Slowhttptest: 5499
Bot: 1966
Web Attack � Brute Force: 1507
Web Attack � XSS: 652
Infiltration: 36
Web Attack � Sql Injection: 21
Heartbleed: 11
```

重要发现：

* `BENIGN` 样本数量最多
* 攻击类别之间样本数量差异很大
* `DoS Hulk`、`PortScan`、`DDoS` 样本较多
* `Heartbleed`、`Sql Injection`、`Infiltration` 样本极少
* 后续不适合直接从完整多分类开始
* 更适合先做 `BENIGN vs ATTACK` 二分类任务

---

### scripts/eda/binary_label_overview.py

作用：

用于统计 CICIDS2017 转换为二分类任务后的 Label 分布。

二分类映射规则：

```txt
BENIGN -> 0
其它所有攻击类型 -> 1
```

主要功能：

* 遍历全部 CSV 文件
* 统计正常流量数量
* 统计攻击流量数量
* 输出二分类样本总数和比例

当前统计结果：

```txt
BENIGN / 0: 2273097
ATTACK / 1: 557646
TOTAL: 2830743
```

当前比例：

```txt
BENIGN: 80.30%
ATTACK: 19.70%
```

重要发现：

* 二分类任务存在一定类别不平衡
* 但不算极端失衡
* 可以先用该任务作为 AI-NIDS 的第一个建模目标

---

## 2. 数据处理脚本

数据处理脚本主要用于构建二分类数据集、检查数据质量，并验证数据能否正确拆分为模型输入 `X` 和标签 `y`。

---

### scripts/data/build_binary_dataset.py

作用：

用于构建 AI-NIDS 项目的二分类训练数据集。

主要功能：

* 读取 CICIDS2017 的全部 8 个 CSV 文件
* 去除列名前后的空格
* 将原始多分类 `Label` 映射为二分类标签 `binary_label`
* 合并全部 CSV 数据
* 清洗 `Infinity` 和 `NaN`
* 删除 `Flow Duration < 0` 的异常数据
* 删除原始多分类 `Label` 列
* 保存处理后的二分类数据集

二分类映射规则：

```txt
BENIGN -> 0
其它所有攻击类型 -> 1
```

输入文件：

```txt
data/raw/MachineLearningCSV/MachineLearningCVE/*.csv
```

输出文件：

```txt
data/processed/binary_dataset.csv
```

运行结果：

```txt
清洗前行数：2830743
清洗后行数：2827761
删除行数：2982
最终数据规模：2827761 行 × 79 列
```

清洗后二分类分布：

```txt
binary_label = 0: 2271205
binary_label = 1: 556556
```

重要发现：

* 清洗删除的数据量很少，约占总数据的 0.1%
* 清洗后仍保持约 80% 正常流量、20% 攻击流量
* 该数据集可以作为后续二分类模型的输入数据

---

### scripts/data/check_binary_dataset.py

作用：

用于检查处理后的二分类数据集是否可以正常读取，以及数据结构是否正确。

主要功能：

* 读取 `data/processed/binary_dataset.csv`
* 查看数据规模
* 查看前 5 行数据
* 查看全部列名
* 查看二分类 Label 分布
* 检查是否存在缺失值

当前检查结果：

```txt
数据规模：2827761 行 × 79 列
特征列：78 个
标签列：binary_label
binary_label = 0: 2271205
binary_label = 1: 556556
缺失值数量：0
```

重要发现：

* 二分类数据集已经成功生成
* 原始多分类 `Label` 已删除
* 数据可以作为后续模型训练的输入
* 原始数据中存在重复列名问题，例如 `Fwd Header Length` 和 `Fwd Header Length.1`

---

### scripts/data/prepare_xy_check.py

作用：

用于检查二分类数据集是否可以正确拆分为模型训练所需的特征矩阵 `X` 和标签 `y`。

主要功能：

* 读取 `data/processed/binary_dataset.csv`
* 将 `binary_label` 之外的列作为特征矩阵 `X`
* 将 `binary_label` 作为标签 `y`
* 查看 `X` 和 `y` 的数据规模
* 查看部分特征列名
* 查看标签分布

当前检查结果：

```txt
原始数据规模：2827761 行 × 79 列
特征矩阵 X：2827761 行 × 78 列
标签 y：2827761 个值
binary_label = 0: 2271205
binary_label = 1: 556556
```

重要发现：

* 数据集已经可以被拆分为机器学习模型需要的输入和输出
* `X` 表示网络流量特征
* `y` 表示该 Flow 是否为攻击

---

### scripts/data/train_test_split_check.py

作用：

用于检查二分类数据集是否可以正确划分为训练集和测试集。

主要功能：

* 读取 `data/processed/binary_dataset.csv`
* 拆分特征矩阵 `X` 和标签 `y`
* 使用 `train_test_split` 划分训练集和测试集
* 检查训练集和测试集的数据规模
* 检查训练集和测试集的标签比例

当前检查结果：

```txt
原始数据规模：2827761 行 × 79 列
特征矩阵 X：2827761 行 × 78 列
标签 y：2827761 个值
训练集 X_train：2262208 行 × 78 列
测试集 X_test：565553 行 × 78 列
训练集 y_train：2262208 个值
测试集 y_test：565553 个值
```

训练集 Label 比例：

```txt
0: 80.3181%
1: 19.6819%
```

测试集 Label 比例：

```txt
0: 80.3182%
1: 19.6818%
```

重要发现：

* 数据集已经可以正确划分为训练集和测试集
* `stratify=y` 保证了训练集和测试集的类别比例基本一致

---

## 3. 模型训练脚本

模型训练脚本用于训练传统机器学习模型和 PyTorch 深度学习模型，并保存模型、指标、图表和实验报告。

---

### scripts/models/train_random_forest.py

作用：

用于训练 Random Forest 二分类模型。

主要功能：

* 读取 `data/processed/binary_dataset.csv`
* 拆分特征矩阵 `X` 和标签 `y`
* 使用 `train_test_split` 划分训练集和测试集
* 训练 `RandomForestClassifier`
* 在测试集上进行预测
* 计算 Accuracy、Precision、Recall、F1 Score
* 生成 Confusion Matrix
* 保存模型文件
* 保存文本实验报告
* 保存结构化 CSV 实验结果
* 保存混淆矩阵图
* 保存指标柱状图
* 保存特征重要性 CSV 和图片

输入文件：

```txt
data/processed/binary_dataset.csv
```

输出文件：

```txt
models/random_forest_binary.pkl
results/random_forest/random_forest_binary_report.txt
results/random_forest/random_forest_binary_metrics.csv
results/random_forest/random_forest_binary_metrics.png
results/random_forest/random_forest_binary_confusion_matrix.png
results/random_forest/feature_importance_top20.csv
results/random_forest/feature_importance_top20.png
```

当前实验结果：

```txt
Accuracy:  0.9991
Precision: 0.9967
Recall:    0.9986
F1 Score:  0.9976
```

重要说明：

Random Forest 是当前二分类任务中表现最好的模型，适合作为强传统机器学习 Baseline。

---

### scripts/models/train_logistic_regression.py

作用：

用于训练 Logistic Regression 二分类 Baseline 模型。

主要功能：

* 读取 `data/processed/binary_dataset.csv`
* 拆分特征矩阵 `X` 和标签 `y`
* 使用 `train_test_split` 划分训练集和测试集
* 使用 `StandardScaler` 对特征进行标准化
* 训练 `LogisticRegression`
* 计算 Accuracy、Precision、Recall、F1 Score
* 生成 Confusion Matrix
* 保存模型文件
* 保存文本实验报告
* 保存结构化指标 CSV
* 保存指标柱状图
* 保存混淆矩阵图

输入文件：

```txt
data/processed/binary_dataset.csv
```

输出文件：

```txt
models/logistic_regression_binary.pkl
results/logistic_regression/logistic_regression_binary_report.txt
results/logistic_regression/logistic_regression_binary_metrics.csv
results/logistic_regression/logistic_regression_binary_metrics.png
results/logistic_regression/logistic_regression_binary_confusion_matrix.png
```

当前实验结果：

```txt
Accuracy:  0.9162
Precision: 0.7129
Recall:    0.9614
F1 Score:  0.8187
```

重要说明：

Logistic Regression 是简单线性基线模型。它的 Recall 较高，但 Precision 较低，说明模型能发现较多攻击流量，但也会产生较多误报。

---

### scripts/models/mlp_torch_binary.py

作用：

用于训练 PyTorch 版 MLP 二分类神经网络模型。

主要功能：

* 读取 `data/processed/binary_dataset.csv`
* 拆分特征矩阵 `X` 和标签 `y`
* 划分训练集、验证集和测试集
* 使用 `StandardScaler` 对特征进行标准化
* 将数据转换为 PyTorch Tensor
* 构建 MLP 神经网络
* 使用 `BCEWithLogitsLoss` 进行二分类训练
* 使用 Adam 优化器更新模型参数
* 使用验证集 Loss 进行 Early Stopping
* 保存验证集表现最好的模型参数
* 在测试集上评估最佳模型
* 保存 PyTorch 模型文件
* 保存 Scaler
* 保存文本实验报告
* 保存结构化指标 CSV
* 保存指标柱状图
* 保存混淆矩阵图
* 保存训练 Loss 和验证 Loss 曲线图

输入文件：

```txt
data/processed/binary_dataset.csv
```

输出文件：

```txt
models/mlp_torch_binary.pt
models/mlp_torch_scaler.pkl
results/mlp_torch/mlp_torch_binary_report.txt
results/mlp_torch/mlp_torch_binary_metrics.csv
results/mlp_torch/mlp_torch_binary_metrics.png
results/mlp_torch/mlp_torch_binary_confusion_matrix.png
results/mlp_torch/mlp_torch_training_loss.png
```

当前实验设置：

```txt
训练数据：完整二分类数据集
采样数量：None，即使用全量数据
MAX_EPOCHS：100
PATIENCE：5
MIN_DELTA：1e-4
Batch Size：1024
Learning Rate：0.001
隐藏层结构：128 -> 64
激活函数：ReLU
Dropout：0.3
损失函数：BCEWithLogitsLoss
优化器：Adam
```

当前实验结果：

```txt
Best Epoch: 9
Best Validation Loss: 0.024161
Accuracy:  0.9908
Precision: 0.9921
Recall:    0.9607
F1 Score:  0.9762
```

Confusion Matrix：

```txt
[[453390    852]
 [  4370 106941]]
```

重要说明：

MLP 是当前深度学习模型中表现最好的模型。相比固定 10 epoch 的旧版本，加入 Validation Set 和 Early Stopping 后，Precision 和 F1 Score 明显提升，但 Recall 略有下降。

---

### scripts/models/cnn_torch_binary.py

作用：

用于训练 PyTorch 版 1D CNN 二分类模型。

主要功能：

* 读取 `data/processed/binary_dataset.csv`
* 拆分特征矩阵 `X` 和标签 `y`
* 划分训练集、验证集和测试集
* 使用 `StandardScaler` 对特征进行标准化
* 将数据转换为 PyTorch Tensor
* 将 78 个 Flow 特征 reshape 为 `[N, 1, 78]`
* 构建 1D CNN 神经网络
* 使用 `BCEWithLogitsLoss` 进行二分类训练
* 使用 Adam 优化器更新模型参数
* 使用验证集 Loss 进行 Early Stopping
* 保存验证集表现最好的模型参数
* 在测试集上评估最佳模型
* 保存 PyTorch 模型文件
* 保存 Scaler
* 保存文本实验报告
* 保存结构化指标 CSV
* 保存指标柱状图
* 保存混淆矩阵图
* 保存训练 Loss 和验证 Loss 曲线图

输入文件：

```txt
data/processed/binary_dataset.csv
```

输出文件：

```txt
models/cnn_torch_binary.pt
models/cnn_torch_scaler.pkl
results/cnn_torch/cnn_torch_binary_report.txt
results/cnn_torch/cnn_torch_binary_metrics.csv
results/cnn_torch/cnn_torch_binary_metrics.png
results/cnn_torch/cnn_torch_binary_confusion_matrix.png
results/cnn_torch/cnn_torch_training_loss.png
```

当前实验设置：

```txt
训练数据：完整二分类数据集
采样数量：None，即使用全量数据
MAX_EPOCHS：100
PATIENCE：5
MIN_DELTA：1e-4
Batch Size：1024
Learning Rate：0.001
卷积结构：Conv1d 1 -> 32 -> 64
池化方式：AdaptiveAvgPool1d
全连接层：64 -> 32 -> 1
激活函数：ReLU
Dropout：0.3
损失函数：BCEWithLogitsLoss
优化器：Adam
```

当前实验结果：

```txt
Best Epoch: 16
Best Validation Loss: 0.063374
Accuracy:  0.9702
Precision: 0.9246
Recall:    0.9239
F1 Score:  0.9243
```

Confusion Matrix：

```txt
[[445853   8389]
 [  8468 102843]]
```

重要说明：

CNN 使用 `[N, 1, 78]` 的输入格式，将 78 个 Flow 特征视为一维特征序列进行卷积建模。在当前二分类任务中，CNN 的效果低于 MLP 和 Random Forest，说明简单 1D CNN 在当前表格型 Flow 特征上并不一定比 MLP 更有优势。

---

## 4. 模型预测脚本

模型预测脚本用于验证模型保存、加载和独立预测流程是否正常。

---

### scripts/models/predict_with_random_forest.py

作用：

用于加载已经训练好的 Random Forest 模型，并对样本 Flow 进行预测。

主要功能：

* 加载 `models/random_forest_binary.pkl`
* 读取 `data/processed/binary_dataset.csv`
* 随机抽取部分正常流量和攻击流量
* 使用模型进行预测
* 输出真实标签、预测标签和预测是否正确
* 保存样本预测结果 CSV

输出文件：

```txt
results/random_forest/sample_predictions.csv
```

重要说明：

该脚本用于验证 Random Forest 模型从训练、保存到加载预测的完整闭环。

---

### scripts/models/predict_with_mlp_torch.py

作用：

用于加载已经训练好的 PyTorch MLP 二分类模型，并对样本 Flow 进行预测。

主要功能：

* 加载 `models/mlp_torch_binary.pt`
* 加载 `models/mlp_torch_scaler.pkl`
* 读取 `data/processed/binary_dataset.csv`
* 随机抽取 5 条正常流量和 5 条攻击流量
* 使用训练阶段保存的 Scaler 对样本特征进行标准化
* 将样本转换为 PyTorch Tensor
* 使用 MLP 模型输出攻击概率
* 根据攻击概率生成二分类预测结果
* 输出真实标签、预测标签、攻击概率和预测是否正确
* 保存样本预测结果 CSV

输出文件：

```txt
results/mlp_torch/sample_predictions.csv
```

重要说明：

预测时必须同时加载模型文件 `.pt` 和标准化器 `.pkl`。其中 `.pt` 保存神经网络模型参数，`.pkl` 保存训练阶段的特征标准化规则。

---

### scripts/models/predict_with_cnn_torch.py

作用：

用于加载已经训练好的 PyTorch CNN 二分类模型，并对样本 Flow 进行预测。

主要功能：

* 加载 `models/cnn_torch_binary.pt`
* 加载 `models/cnn_torch_scaler.pkl`
* 读取 `data/processed/binary_dataset.csv`
* 随机抽取 5 条正常流量和 5 条攻击流量
* 使用训练阶段保存的 Scaler 对样本特征进行标准化
* 将样本转换为 PyTorch Tensor
* 将输入 reshape 为 `[N, 1, 78]`
* 使用 CNN 模型输出攻击概率
* 根据攻击概率生成二分类预测结果
* 输出真实标签、预测标签、攻击概率和预测是否正确
* 保存样本预测结果 CSV

输出文件：

```txt
results/cnn_torch/sample_predictions.csv
```

重要说明：

CNN 的输入格式为 `[batch_size, channels, feature_length]`，因此预测前需要使用 `unsqueeze(1)` 将样本从 `[N, 78]` 转换为 `[N, 1, 78]`。

---

## 5. 模型对比脚本

### scripts/models/compare_binary_models.py

作用：

用于汇总 Random Forest、Logistic Regression、PyTorch MLP 和 PyTorch CNN 的二分类实验结果，并生成统一对比表和对比图。

主要功能：

* 读取各模型的 metrics CSV 文件
* 兼容不同 metrics CSV 格式
* 汇总 Accuracy、Precision、Recall、F1 Score
* 保存统一模型对比 CSV
* 保存模型指标对比图

输入文件：

```txt
results/random_forest/random_forest_binary_metrics.csv
results/logistic_regression/logistic_regression_binary_metrics.csv
results/mlp_torch/mlp_torch_binary_metrics.csv
results/cnn_torch/cnn_torch_binary_metrics.csv
```

输出文件：

```txt
results/model_comparison/binary_model_comparison.csv
results/model_comparison/binary_model_comparison.png
```

当前模型对比结果：

```txt
Random Forest:
Accuracy  = 0.9991
Precision = 0.9967
Recall    = 0.9986
F1 Score  = 0.9976

Logistic Regression:
Accuracy  = 0.9162
Precision = 0.7129
Recall    = 0.9614
F1 Score  = 0.8187

PyTorch MLP:
Accuracy  = 0.9908
Precision = 0.9921
Recall    = 0.9607
F1 Score  = 0.9762

PyTorch CNN:
Accuracy  = 0.9702
Precision = 0.9246
Recall    = 0.9239
F1 Score  = 0.9243
```

重要说明：

该脚本用于生成当前二分类阶段的最终模型对比结果。从当前结果看，Random Forest 表现最好，PyTorch MLP 是深度学习模型中表现最好的模型。

---

## 6. 推荐运行顺序

如果从零开始复现实验，推荐按以下顺序运行：

### 1. 数据探索

```powershell
python scripts\eda\dataset_overview.py
python scripts\eda\label_overview.py
python scripts\eda\binary_label_overview.py
```

### 2. 构建二分类数据集

```powershell
python scripts\data\build_binary_dataset.py
```

### 3. 检查二分类数据集

```powershell
python scripts\data\check_binary_dataset.py
python scripts\data\prepare_xy_check.py
python scripts\data\train_test_split_check.py
```

### 4. 训练传统机器学习模型

```powershell
python scripts\models\train_random_forest.py
python scripts\models\train_logistic_regression.py
```

### 5. 训练深度学习模型

```powershell
python scripts\models\mlp_torch_binary.py
python scripts\models\cnn_torch_binary.py
```

### 6. 进行样本预测验证

```powershell
python scripts\models\predict_with_random_forest.py
python scripts\models\predict_with_mlp_torch.py
python scripts\models\predict_with_cnn_torch.py
```

### 7. 生成模型对比结果

```powershell
python scripts\models\compare_binary_models.py
```

---

## 7. 当前阶段总结

截至 Day5，AI-NIDS 项目已经完成二分类阶段的完整实验闭环：

```txt
数据探索
数据清洗
二分类标签构建
传统机器学习模型训练
PyTorch 深度学习模型训练
Early Stopping 训练策略优化
模型保存与加载
样本预测验证
多模型指标对比
实验结果可视化
```

后续可以进入多分类任务、类别不平衡分析、误报漏报分析和更复杂的序列建模实验。

### `scripts/models/multiclass/train_multiclass_logistic_regression.py`

训练多分类 Logistic Regression 模型。该脚本读取 `data/processed/multiclass_dataset.csv`，使用 `StandardScaler` 对 78 个 Flow 特征进行标准化，并使用 `LabelEncoder` 将 `attack_category` 转换为数字类别。模型使用 `class_weight="balanced"` 缓解类别不平衡问题，最终输出分类报告、混淆矩阵、指标 CSV 和模型文件。

输出文件包括：

- `models/multiclass/logistic_regression_multiclass.pkl`
- `models/multiclass/logistic_regression_multiclass_scaler.pkl`
- `models/multiclass/multiclass_label_encoder.pkl`
- `results/multiclass/logistic_regression/logistic_regression_multiclass_report.txt`
- `results/multiclass/logistic_regression/logistic_regression_multiclass_metrics.csv`
- `results/multiclass/logistic_regression/logistic_regression_multiclass_confusion_matrix.png`

### `scripts/models/multiclass/predict_with_multiclass_logistic_regression.py`

加载已经训练好的 Logistic Regression 多分类模型、Scaler 和 LabelEncoder，从每个类别中抽取若干样本进行预测，输出真实类别、预测类别、置信度和是否预测正确。用于直观观察模型在不同类别上的预测效果。

输出文件：

- `results/multiclass/logistic_regression/sample_predictions.csv`

### `scripts/models/multiclass/train_multiclass_mlp.py`

训练 PyTorch MLP 多分类模型。模型输入为 78 个 Flow 特征，输出为 9 个类别 logits。训练时使用 `CrossEntropyLoss`，并采用训练集、验证集和测试集划分。验证集用于 Early Stopping，测试集用于最终评估。该脚本支持 GPU 训练。

输出文件包括：

- `models/multiclass/mlp_torch_multiclass.pt`
- `models/multiclass/mlp_torch_multiclass_scaler.pkl`
- `results/multiclass/mlp_torch/mlp_torch_multiclass_report.txt`
- `results/multiclass/mlp_torch/mlp_torch_multiclass_metrics.csv`
- `results/multiclass/mlp_torch/mlp_torch_multiclass_training_history.csv`
- `results/multiclass/mlp_torch/mlp_torch_multiclass_confusion_matrix.png`

### `scripts/models/multiclass/predict_with_multiclass_mlp.py`

加载 PyTorch MLP 多分类模型、Scaler 和 LabelEncoder，从每个类别抽样进行预测。该脚本使用 softmax 将模型输出 logits 转换为类别概率，并取最大概率对应类别作为预测结果。

输出文件：

- `results/multiclass/mlp_torch/sample_predictions.csv`

### `scripts/models/multiclass/train_multiclass_cnn.py`

训练 PyTorch 1D CNN 多分类模型。该脚本将每条 Flow 的 78 个特征转换为 `[N, 1, 78]` 的输入形式，通过一维卷积提取局部特征。模型输出 9 个类别 logits，使用 `CrossEntropyLoss` 进行训练，并加入 Early Stopping。

输出文件包括：

- `models/multiclass/cnn_torch_multiclass.pt`
- `models/multiclass/cnn_torch_multiclass_scaler.pkl`
- `results/multiclass/cnn_torch/cnn_torch_multiclass_report.txt`
- `results/multiclass/cnn_torch/cnn_torch_multiclass_metrics.csv`
- `results/multiclass/cnn_torch/cnn_torch_multiclass_training_history.csv`
- `results/multiclass/cnn_torch/cnn_torch_multiclass_confusion_matrix.png`

### `scripts/models/multiclass/predict_with_multiclass_cnn.py`

加载 PyTorch CNN 多分类模型、Scaler 和 LabelEncoder，从每个类别抽取样本进行预测。该脚本用于观察 CNN 在单条 Flow 样本上的预测类别、置信度和错误类型。

输出文件：

- `results/multiclass/cnn_torch/sample_predictions.csv`

### `scripts/models/multiclass/compare_multiclass_models.py`

读取 Random Forest、Logistic Regression、PyTorch MLP 和 PyTorch CNN 四个多分类模型的指标 CSV，生成统一的模型对比表和对比图。对比指标包括 Accuracy、Macro Precision、Macro Recall、Macro F1、Weighted Precision、Weighted Recall 和 Weighted F1。

输出文件：

- `results/multiclass/model_comparison/multiclass_model_comparison.csv`
- `results/multiclass/model_comparison/multiclass_model_comparison.png`

## Day6：类别不平衡优化实验脚本

| Script | Description |
|---|---|
| `scripts/models/multiclass/train_multiclass_mlp_weighted.py` | 训练使用 balanced class weight 的 Weighted MLP |
| `scripts/models/multiclass/train_multiclass_mlp_weighted_clipped.py` | 训练裁剪最大类别权重的 Clipped Weighted MLP |
| `scripts/models/multiclass/compare_mlp_weight_experiments.py` | 对比 MLP、Weighted MLP、Clipped Weighted MLP |
| `scripts/models/multiclass/train_multiclass_cnn_weighted.py` | 训练使用 balanced class weight 的 Weighted CNN |
| `scripts/models/multiclass/train_multiclass_cnn_weighted_clipped.py` | 训练裁剪最大类别权重的 Clipped Weighted CNN |
| `scripts/models/multiclass/compare_cnn_weight_experiments.py` | 对比 CNN、Weighted CNN、Clipped Weighted CNN |
| `scripts/models/multiclass/compare_deep_learning_weight_experiments.py` | 对比所有深度学习权重实验 |

## Day7：错误模式分析脚本

| Script | Description |
|---|---|
| `scripts/analysis/multiclass/analyze_cnn_error_patterns.py` | 分析原始 CNN 的错误模式，统计 Top 错误类型、攻击漏报和正常流量误报 |
| `scripts/analysis/multiclass/analyze_random_forest_error_patterns.py` | 分析 Random Forest 的错误模式 |
| `scripts/analysis/multiclass/analyze_clipped_weighted_cnn_error_patterns.py` | 分析 Clipped Weighted CNN 的错误模式 |
| `scripts/analysis/multiclass/compare_error_patterns.py` | 对比 CNN、Random Forest 和 Clipped Weighted CNN 的总错误、漏报和误报 |
| `scripts/analysis/multiclass/compare_class_error_rates.py` | 按真实类别统计不同模型的错误率和 Attack -> BENIGN 比例 |
| `scripts/analysis/multiclass/generate_error_analysis_summary.py` | 自动生成 Day7 错误分析总结 Markdown 和关键发现 CSV |