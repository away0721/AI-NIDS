# Day3

## 今日目标

今天进入 AI-NIDS 项目的第三天，主要目标是完成二分类任务下的多个模型实验，并形成完整的训练、评估、保存、预测和结果对比流程。

当前二分类任务为：

* `BENIGN`：正常流量
* `ATTACK`：攻击流量

标签映射规则：

* `BENIGN -> 0`
* `ATTACK -> 1`

---

## 今日完成内容

### 1. Train/Test Split

今天首先完成了二分类数据集的训练集和测试集划分。

数据集：

* 文件：`data/processed/binary_dataset.csv`
* 数据规模：2827761 行 × 79 列
* 特征数：78
* 标签列：`binary_label`

划分方式：

* 训练集：80%
* 测试集：20%
* `random_state=42`
* `stratify=y`

划分结果：

* `X_train`：2262208 行 × 78 列
* `X_test`：565553 行 × 78 列
* `y_train`：2262208 个标签
* `y_test`：565553 个标签

训练集和测试集中的类别比例基本保持一致，说明 `stratify=y` 生效。

---

### 2. Random Forest Baseline

完成了 Random Forest 二分类 Baseline 实验。

实验结果：

* Accuracy：0.9991
* Precision：0.9967
* Recall：0.9986
* F1 Score：0.9976

Confusion Matrix：

```txt
[[453872    370]
 [   156 111155]]
```

理解：

Random Forest 在当前二分类任务上表现最好，说明 CICIDS2017 的 Flow 统计特征对区分正常流量和攻击流量具有较强区分能力。

同时，Random Forest 对表格型数据非常友好，不需要额外归一化，也能取得很好的效果。

---

### 3. Logistic Regression Baseline

完成了 Logistic Regression 二分类实验。

实验结果：

* Accuracy：0.9162
* Precision：0.7129
* Recall：0.9614
* F1 Score：0.8187

Confusion Matrix：

```txt
[[411141  43101]
 [  4295 107016]]
```

理解：

Logistic Regression 是线性模型，整体效果明显弱于 Random Forest。

它的 Recall 较高，说明能够发现较多攻击流量；但 Precision 较低，说明误报正常流量较多。

这说明当前数据中的正常流量与攻击流量之间可能存在较复杂的非线性特征关系，简单线性模型难以充分表达。

---

### 4. PyTorch MLP Baseline

完成了 PyTorch 版 MLP 二分类神经网络实验。

实验设置：

* 使用完整二分类数据集
* Epochs：10
* Batch Size：1024
* Learning Rate：0.001
* 网络结构：78 -> 128 -> 64 -> 1
* 激活函数：ReLU
* Dropout：0.3
* 损失函数：BCEWithLogitsLoss
* 优化器：Adam

实验结果：

* Accuracy：0.9867
* Precision：0.9536
* Recall：0.9799
* F1 Score：0.9666

Confusion Matrix：

```txt
[[448940   5302]
 [  2235 109076]]
```

理解：

MLP 相比 Logistic Regression 有明显提升，说明神经网络能够学习到更复杂的非线性特征关系。

但 MLP 仍低于 Random Forest，说明在 CICIDS2017 这种表格型 Flow 特征数据上，传统树模型依然非常强。

---

### 5. PyTorch CNN Baseline

完成了 PyTorch 版 1D CNN 二分类实验。

实验设置：

* 使用完整二分类数据集
* 输入形状：`[N, 1, 78]`
* 卷积结构：Conv1d 1 -> 32 -> 64
* 池化方式：AdaptiveAvgPool1d
* 全连接层：64 -> 32 -> 1
* Epochs：10
* Batch Size：1024
* Learning Rate：0.001

实验结果：

* Accuracy：0.9776
* Precision：0.9039
* Recall：0.9917
* F1 Score：0.9458

Confusion Matrix：

```txt
[[442510  11732]
 [   924 110387]]
```

理解：

CNN 的 Recall 很高，说明它能识别大部分攻击流量，漏报较少。

但 CNN 的 Precision 相对较低，说明它误报正常流量较多。

因此，CNN 在当前任务中表现得更“激进”：宁可多报攻击，也尽量少漏报攻击。

---

## 模型对比总结

当前二分类阶段已经完成 4 个模型：

* Random Forest
* Logistic Regression
* PyTorch MLP
* PyTorch CNN

整体来看：

* Random Forest 综合表现最好
* PyTorch MLP 次之
* PyTorch CNN Recall 较高，但 Precision 较低
* Logistic Regression 整体最弱，尤其 Precision 明显偏低

重要结论：

深度学习模型不一定天然优于传统机器学习模型。

在 CICIDS2017 这种已经提取好的 Flow 表格特征数据上，Random Forest 这类树模型非常有竞争力。

---

## 今日关键理解

### 1. 归一化不应该无脑放在最早的数据预处理阶段

`binary_dataset.csv` 是一个通用的干净数据集，主要目标是：

* 清洗 NaN
* 清洗 Infinity
* 删除异常值
* 映射二分类标签
* 保留原始特征含义

是否归一化应该根据模型决定。

例如：

* Random Forest：通常不需要归一化
* Logistic Regression：需要标准化
* MLP / CNN：需要标准化

更规范的流程是：

```txt
先划分训练集和测试集
↓
只用训练集 fit scaler
↓
用同一个 scaler transform 训练集和测试集
```

这样可以避免测试集信息泄露到训练过程。

---

### 2. Loss 是模型训练过程中的错误程度

Loss 表示模型当前预测结果和真实标签之间的差距。

在 MLP 和 CNN 中使用的是：

```txt
BCEWithLogitsLoss
```

它适合二分类任务。

训练过程中：

```txt
模型预测
↓
计算 loss
↓
反向传播
↓
更新参数
↓
下一轮继续训练
```

如果 Loss 逐渐下降，说明模型正在学习。

---

### 3. `.pt` 和 `.pkl` 的区别

PyTorch 模型保存为：

```txt
.pt
```

例如：

```txt
models/mlp_torch_binary.pt
models/cnn_torch_binary.pt
```

`.pt` 保存的是神经网络模型参数，例如每一层的 weight 和 bias。

Scaler 保存为：

```txt
.pkl
```

例如：

```txt
models/mlp_torch_scaler.pkl
models/cnn_torch_scaler.pkl
```

`.pkl` 保存的是训练阶段的标准化规则，例如每个特征的均值和标准差。

预测时必须先加载 scaler 对输入数据进行标准化，再加载模型进行预测。

---

### 4. 训练脚本和预测脚本要分开

训练脚本负责：

```txt
读取数据
训练模型
评估模型
保存模型
保存实验结果
```

预测脚本负责：

```txt
加载模型
加载 scaler
读取样本
进行预测
保存预测结果
```

这样项目才具有真正的工程闭环。

---

## 今日生成的重要结果

### Random Forest

目录：

```txt
results/random_forest/
```

主要结果：

* `random_forest_binary_report.txt`
* `random_forest_binary_metrics.csv`
* `random_forest_binary_metrics.png`
* `random_forest_binary_confusion_matrix.png`
* `feature_importance_top20.csv`
* `feature_importance_top20.png`
* `sample_predictions.csv`

---

### Logistic Regression

目录：

```txt
results/logistic_regression/
```

主要结果：

* `logistic_regression_binary_report.txt`
* `logistic_regression_binary_metrics.csv`
* `logistic_regression_binary_metrics.png`
* `logistic_regression_binary_confusion_matrix.png`

---

### PyTorch MLP

目录：

```txt
results/mlp_torch/
```

主要结果：

* `mlp_torch_binary_report.txt`
* `mlp_torch_binary_metrics.csv`
* `mlp_torch_binary_metrics.png`
* `mlp_torch_binary_confusion_matrix.png`
* `mlp_torch_training_loss.png`
* `sample_predictions.csv`

---

### PyTorch CNN

目录：

```txt
results/cnn_torch/
```

主要结果：

* `cnn_torch_binary_report.txt`
* `cnn_torch_binary_metrics.csv`
* `cnn_torch_binary_metrics.png`
* `cnn_torch_binary_confusion_matrix.png`
* `cnn_torch_training_loss.png`
* `sample_predictions.csv`

---

### Model Comparison

目录：

```txt
results/model_comparison/
```

主要结果：

* `binary_model_comparison.csv`
* `binary_model_comparison.png`

---

## 当前阶段总结

到 Day3 为止，AI-NIDS 已经完成了二分类阶段的完整实验闭环：

```txt
数据处理
↓
训练集 / 测试集划分
↓
传统机器学习模型
↓
深度学习模型
↓
模型评估
↓
结果图表
↓
模型保存
↓
模型加载预测
↓
模型对比
↓
GitHub 版本管理
```

Phase 1 二分类任务已经基本完成。

后续可以继续做：

1. CNN-LSTM 二分类模型
2. 合并类别后的多分类任务
3. 原始完整类别多分类任务
4. 更规范的验证集与 Early Stopping
5. 模型对比分析和报告整理
