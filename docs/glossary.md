# Glossary 术语表

本文档用于记录 AI-NIDS 项目学习过程中遇到的重要概念，方便后续复习、写报告和准备答辩。

---

## 1. 数据集与网络流量相关术语

---

### Dataset

英文：Dataset

中文：数据集

含义：

用于训练、验证和测试模型的数据集合。

在 AI-NIDS 项目中，当前使用的是 CICIDS2017 数据集。

---

### CICIDS2017

英文：Canadian Institute for Cybersecurity Intrusion Detection System 2017

中文：CICIDS2017 入侵检测数据集

含义：

一个常用的网络入侵检测公开数据集，包含正常流量和多种攻击流量。

在本项目中，当前使用的是其中的 `MachineLearningCSV` 版本。

---

### Flow

英文：Flow

中文：网络流

含义：

由多个 Packet 聚合形成的一次网络通信记录。

在 CICIDS2017 的 MachineLearningCSV 数据中：

```txt
一行数据 = 一个 Flow
```

Flow 不是单个数据包，而是一段通信行为的统计结果。

---

### Packet

英文：Packet

中文：数据包

含义：

网络传输中的基本单位。

多个 Packet 可以组成一个 Flow。

---

### Five Tuple

英文：Five Tuple

中文：五元组

含义：

用于标识一条网络流的五个关键信息。

包括：

```txt
Source IP
Destination IP
Source Port
Destination Port
Protocol
```

---

### Feature

英文：Feature

中文：特征

含义：

用于描述样本的数据字段。

在 AI-NIDS 中，Feature 用于描述网络 Flow 的行为。

例如：

```txt
Flow Duration
Total Fwd Packets
Flow Bytes/s
Packet Length Mean
Destination Port
```

---

### Label

英文：Label

中文：标签

含义：

模型需要预测的目标结果。

在原始 CICIDS2017 中，Label 可能是：

```txt
BENIGN
DDoS
PortScan
DoS Hulk
Bot
Web Attack
```

在当前二分类阶段，Label 被转换为：

```txt
BENIGN -> 0
ATTACK -> 1
```

---

### EDA

英文：Exploratory Data Analysis

中文：探索性数据分析

含义：

在训练模型之前，对数据集进行初步理解和检查。

常见内容包括：

```txt
查看数据规模
查看 Label 分布
查看缺失值
查看异常值
查看数据统计信息
```

---

### Data Cleaning

英文：Data Cleaning

中文：数据清洗

含义：

处理数据中的脏数据或异常数据，使其更适合模型训练。

例如：

```txt
处理 NaN
处理 Infinity
删除异常值
删除无效样本
统一列名
```

---

### Missing Value

英文：Missing Value

中文：缺失值

含义：

数据中某些位置没有有效值。

常见形式：

```txt
NaN
None
空值
```

训练模型之前通常需要处理缺失值。

---

### Outlier

英文：Outlier

中文：异常值

含义：

不符合正常业务逻辑或统计规律的数据。

例如：

```txt
Flow Duration = -13
```

网络流持续时间理论上不应该小于 0，因此这类数据需要清洗。

---

### Class Imbalance

英文：Class Imbalance

中文：类别不平衡

含义：

不同类别的样本数量差异很大。

例如 CICIDS2017 中：

```txt
DoS Hulk: 231073
Heartbleed: 11
```

类别不平衡可能导致模型偏向样本数量较多的类别。

---

## 2. 分类任务相关术语

---

### Binary Classification

英文：Binary Classification

中文：二分类

含义：

只判断样本属于两个类别中的哪一个。

在 AI-NIDS 当前阶段：

```txt
BENIGN
ATTACK
```

---

### Multi-Class Classification

英文：Multi-Class Classification

中文：多分类

含义：

判断样本属于多个类别中的哪一个。

例如：

```txt
BENIGN
DDoS
PortScan
Bot
Web Attack
DoS Hulk
```

多分类比二分类更难，因为模型不仅要判断是否攻击，还要判断具体攻击类型。

---

### Baseline

英文：Baseline

中文：基线模型

含义：

用于作为对照和参考的基础模型。

作用：

```txt
验证任务是否可行
提供实验对照
衡量后续模型是否真的改进
```

本项目中的 Baseline 包括：

```txt
Logistic Regression
Random Forest
PyTorch MLP
PyTorch CNN
```

---

### Feature Engineering

英文：Feature Engineering

中文：特征工程

含义：

从原始数据中构造或选择更有价值的特征。

例如：

```txt
10 秒内访问的不同端口数
单位时间内连接失败次数
某个源 IP 的连接频率
```

在当前阶段，项目主要使用 CICIDS2017 已经提取好的 Flow 特征。

---

### Encoding

英文：Encoding

中文：编码

含义：

将字符串或类别型数据转换为模型可以处理的数字形式。

例如：

```txt
TCP  -> [1, 0, 0]
UDP  -> [0, 1, 0]
ICMP -> [0, 0, 1]
```

---

## 3. 数据划分与预处理相关术语

---

### Train Set

英文：Train Set

中文：训练集

含义：

用于模型学习参数的数据。

训练集会参与模型训练过程。

在深度学习中，训练集会执行：

```txt
前向传播
计算 loss
反向传播
更新参数
```

---

### Validation Set

英文：Validation Set

中文：验证集

含义：

训练过程中用于观察模型表现的数据。

验证集不会参与反向传播，也不会更新模型参数。

它主要用于：

```txt
观察 validation loss
判断模型是否过拟合
进行 Early Stopping
辅助调参
```

---

### Test Set

英文：Test Set

中文：测试集

含义：

用于最终评估模型泛化能力的数据。

测试集不参与训练，也不参与 Early Stopping。

它应该只在最终评估时使用一次。

---

### Stratify

英文：Stratify

中文：分层抽样

含义：

在划分训练集和测试集时，保持各个类别的比例基本一致。

例如原始数据中：

```txt
BENIGN: 80%
ATTACK: 20%
```

使用 `stratify=y` 后，训练集和测试集也会尽量保持类似比例。

---

### Normalization

英文：Normalization

中文：归一化

含义：

将数据缩放到某个固定范围。

例如：

```txt
0 到 1
-1 到 1
```

作用是避免数值范围过大的特征主导模型训练。

---

### Standardization

英文：Standardization

中文：标准化

含义：

将数据转换为均值接近 0、标准差接近 1 的分布。

常见公式：

```txt
标准化后的值 = (原始值 - 均值) / 标准差
```

---

### StandardScaler

英文：StandardScaler

中文：标准化器

含义：

`sklearn` 中用于标准化数据的工具。

它会根据训练集计算每个特征的均值和标准差。

正确使用方式：

```python
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)
```

注意：

```txt
只能在训练集上 fit
验证集和测试集只能 transform
```

---

### Data Leakage

英文：Data Leakage

中文：数据泄露

含义：

模型训练过程中使用了本不应该提前知道的信息，导致测试结果虚高。

典型错误：

```txt
先对整个数据集做标准化
再划分训练集和测试集
```

这样会让测试集的均值和标准差信息提前参与训练过程。

正确做法：

```txt
先划分训练集、验证集、测试集
只用训练集 fit scaler
再用同一个 scaler transform 验证集和测试集
```

---

### Pipeline

英文：Pipeline

中文：流水线

含义：

`sklearn` 中用于把多个处理步骤串联起来的工具。

例如：

```txt
StandardScaler -> LogisticRegression
```

使用 Pipeline 可以减少数据泄露风险，让预处理和模型训练流程更加规范。

---

## 4. 模型相关术语

---

### Logistic Regression

英文：Logistic Regression

中文：逻辑回归

含义：

一种常用的线性分类模型。

在本项目中，它用于二分类任务：

```txt
BENIGN
ATTACK
```

特点：

```txt
模型简单
训练速度快
可作为线性 Baseline
但难以学习复杂非线性关系
```

---

### Random Forest

英文：Random Forest

中文：随机森林

含义：

由多棵决策树组成的集成学习模型。

特点：

```txt
适合表格数据
抗过拟合能力较强
能输出特征重要性
在当前二分类任务中表现最好
```

---

### MLP

英文：Multi-Layer Perceptron

中文：多层感知机 / 全连接神经网络

含义：

由多个全连接层组成的神经网络。

在本项目中，MLP 的输入是：

```txt
[N, 78]
```

其中 `N` 是样本数量，`78` 是 Flow 特征数量。

---

### CNN

英文：Convolutional Neural Network

中文：卷积神经网络

含义：

一种通过卷积操作提取局部特征的神经网络。

在图像任务中使用非常广泛。

在本项目中，CNN 被用于 1D Flow 特征建模，输入格式为：

```txt
[N, 1, 78]
```

其中：

```txt
N：样本数量
1：通道数
78：Flow 特征长度
```

---

### 1D CNN

英文：One-Dimensional Convolutional Neural Network

中文：一维卷积神经网络

含义：

在一维序列或一维特征排列上进行卷积操作的 CNN。

在 AI-NIDS 中，1D CNN 将 78 个 Flow 特征视为一个一维特征序列进行建模。

注意：

当前这种做法是一种实验性建模方式，并不等价于真正的时间序列流量建模。

---

### LSTM

英文：Long Short-Term Memory

中文：长短期记忆网络

含义：

一种循环神经网络结构，用于学习序列数据中的长期依赖关系。

适合处理：

```txt
时间序列
文本序列
行为序列
流量序列
```

如果后续要做 CNN-LSTM，更严谨的方式是构造 Flow 序列或时间窗口，而不是简单把 78 个特征当成时间步。

---

## 5. 深度学习训练相关术语

---

### Tensor

英文：Tensor

中文：张量

含义：

深度学习框架中用于存储数据的多维数组。

例如：

```txt
[N, 78]
[N, 1, 78]
```

PyTorch 模型输入通常需要转换为 Tensor。

---

### Epoch

英文：Epoch

中文：训练轮次

含义：

模型完整遍历一次训练集，称为一个 Epoch。

例如：

```txt
Epoch 1：完整学习训练集一次
Epoch 10：完整学习训练集十次
```

---

### Batch

英文：Batch

中文：批次

含义：

一次送入模型训练的一小部分数据。

因为数据集通常很大，模型不会一次性处理全部数据，而是分成多个 Batch。

---

### Batch Size

英文：Batch Size

中文：批大小

含义：

每次训练送入模型的样本数量。

例如：

```txt
Batch Size = 1024
```

表示每次训练使用 1024 条样本。

---

### Forward Propagation

英文：Forward Propagation

中文：前向传播

含义：

数据从输入层经过模型，最终得到预测结果的过程。

训练集、验证集和测试集都会执行前向传播。

---

### Backward Propagation

英文：Backward Propagation

中文：反向传播

含义：

根据 loss 计算梯度，并将误差信息反向传回模型参数的过程。

只有训练集阶段会执行反向传播。

验证集和测试集不会执行反向传播。

---

### Loss

英文：Loss

中文：损失值

含义：

衡量模型预测结果与真实标签之间差距的数值。

Loss 不只是看预测是否正确，还会考虑预测的置信度。

例如真实标签是攻击：

```txt
预测概率 0.99：loss 较小
预测概率 0.51：虽然分类正确，但 loss 较大
预测概率 0.01：loss 很大
```

---

### Train Loss

英文：Train Loss

中文：训练集损失

含义：

模型在训练集上的损失值。

作用：

```txt
指导模型更新参数
观察模型是否正在学习训练数据
```

Train Loss 会参与反向传播和参数更新。

---

### Validation Loss

英文：Validation Loss

中文：验证集损失

含义：

模型在验证集上的损失值。

作用：

```txt
观察模型在未参与训练的数据上的表现
判断是否过拟合
用于 Early Stopping
```

Validation Loss 不参与参数更新。

---

### BCEWithLogitsLoss

英文：Binary Cross Entropy With Logits Loss

中文：带 Logits 的二元交叉熵损失

含义：

PyTorch 中常用于二分类任务的损失函数。

它内部会把 Logit 转换为概率，并计算二分类交叉熵损失。

在本项目中，MLP 和 CNN 都使用：

```python
nn.BCEWithLogitsLoss()
```

---

### Logit

英文：Logit

中文：未归一化预测值

含义：

模型最后一层直接输出的原始数值。

Logit 不是概率，可能是任意实数。

在二分类中，需要通过 Sigmoid 将 Logit 转换为概率。

---

### Sigmoid

英文：Sigmoid

中文：Sigmoid 函数

含义：

将任意实数转换到 0 到 1 之间。

在二分类中，Sigmoid 输出可以理解为攻击概率。

例如：

```txt
Sigmoid(logit) = 0.92
```

可以理解为模型认为该样本是攻击的概率为 92%。

---

### Optimizer

英文：Optimizer

中文：优化器

含义：

用于根据梯度更新模型参数的算法。

常见优化器：

```txt
SGD
Adam
AdamW
```

本项目中 PyTorch MLP 和 CNN 使用 Adam 优化器。

---

### Adam

英文：Adam Optimizer

中文：Adam 优化器

含义：

一种常用的深度学习优化器。

特点：

```txt
收敛速度较快
使用方便
适合作为初始实验选择
```

---

### Learning Rate

英文：Learning Rate

中文：学习率

含义：

控制模型每次参数更新步子大小的超参数。

学习率过大，loss 可能震荡。

学习率过小，训练速度可能很慢。

---

### Dropout

英文：Dropout

中文：随机失活

含义：

训练过程中随机让一部分神经元暂时不工作。

作用：

```txt
减少神经元之间的依赖
降低过拟合风险
增强泛化能力
```

---

### BatchNorm

英文：Batch Normalization

中文：批归一化

含义：

对神经网络中间层输出进行规范化的技术。

作用：

```txt
稳定训练过程
加快收敛
缓解数值分布变化
```

本项目 CNN 中使用了 `BatchNorm1d`。

---

### Early Stopping

英文：Early Stopping

中文：提前停止

含义：

当验证集 loss 连续若干轮没有明显改善时，提前结束训练。

目的：

```txt
避免无意义训练
降低过拟合风险
自动选择较优训练轮次
```

本项目设置：

```txt
MAX_EPOCHS = 100
PATIENCE = 5
MIN_DELTA = 1e-4
```

---

### Patience

英文：Patience

中文：容忍轮数

含义：

Early Stopping 中允许验证集 loss 连续多少轮不提升。

例如：

```txt
PATIENCE = 5
```

表示验证集 loss 连续 5 轮没有明显下降时，停止训练。

---

### Min Delta

英文：Minimum Delta

中文：最小改善幅度

含义：

用于判断验证集 loss 是否真的改善。

例如：

```txt
MIN_DELTA = 1e-4
```

表示验证集 loss 至少下降 0.0001，才算有效改善。

---

### Overfitting

英文：Overfitting

中文：过拟合

含义：

模型过度学习训练集中的细节和噪声。

表现：

```txt
Train Loss 继续下降
Validation Loss 开始上升
训练集表现很好
未见数据表现变差
```

本质：

模型记住了训练样本，而没有学会通用规律。

---

### Underfitting

英文：Underfitting

中文：欠拟合

含义：

模型没有充分学习数据规律。

表现：

```txt
Train Loss 高
Validation Loss 高
Train Accuracy 低
Test Accuracy 低
```

原因可能是：

```txt
模型太简单
训练轮数太少
特征不足
学习率不合适
```

---

### Generalization

英文：Generalization

中文：泛化能力

含义：

模型在未见过的新数据上的表现能力。

泛化能力强说明模型学到了较通用的规律。

泛化能力弱说明模型可能只记住了训练数据。

---

## 6. 评估指标相关术语

---

### Confusion Matrix

英文：Confusion Matrix

中文：混淆矩阵

含义：

用于展示分类模型预测结果的表格。

二分类混淆矩阵通常包含：

```txt
TN：真实为正常，预测为正常
FP：真实为正常，预测为攻击
FN：真实为攻击，预测为正常
TP：真实为攻击，预测为攻击
```

---

### Accuracy

英文：Accuracy

中文：准确率

含义：

预测正确样本占总样本的比例。

公式：

```txt
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

注意：

在类别不平衡的数据集上，Accuracy 可能具有迷惑性。

---

### Precision

英文：Precision

中文：精确率

含义：

模型预测为攻击的样本中，真正是攻击的比例。

公式：

```txt
Precision = TP / (TP + FP)
```

在 IDS 中，Precision 反映误报情况。

Precision 越高，误报越少。

---

### Recall

英文：Recall

中文：召回率

含义：

真实攻击样本中，被模型成功发现的比例。

公式：

```txt
Recall = TP / (TP + FN)
```

在 IDS 中，Recall 通常代表发现攻击的能力。

Recall 越高，漏报越少。

---

### F1 Score

英文：F1 Score

中文：F1 分数

含义：

综合衡量 Precision 和 Recall 的指标。

公式：

```txt
F1 = 2 × Precision × Recall / (Precision + Recall)
```

当需要同时关注误报和漏报时，F1 Score 比单独看 Accuracy 更有意义。

---

### False Positive

英文：False Positive

中文：误报

含义：

真实是正常流量，但模型预测为攻击。

在 IDS 中，误报会增加安全运维人员的告警负担。

---

### False Negative

英文：False Negative

中文：漏报

含义：

真实是攻击流量，但模型预测为正常。

在 IDS 中，漏报通常更危险，因为攻击可能未被发现。

---

## 7. 文件格式相关术语

---

### CSV

英文：Comma-Separated Values

中文：逗号分隔值文件

含义：

一种常见的表格数据文件格式。

本项目原始数据和处理后的数据主要使用 CSV 文件。

---

### `.pkl`

英文：Pickle File

中文：Python 序列化文件

含义：

用于保存 Python 对象的文件格式。

在本项目中，`.pkl` 用于保存：

```txt
Random Forest 模型
Logistic Regression 模型
StandardScaler
```

---

### `.pt`

英文：PyTorch Model File

中文：PyTorch 模型文件

含义：

PyTorch 常用的模型参数保存格式。

在本项目中，`.pt` 用于保存：

```txt
MLP 模型参数
CNN 模型参数
```

---

## 8. 当前项目阶段理解

截至 Day5，AI-NIDS 已经完成二分类阶段的完整实验闭环：

```txt
数据探索
数据清洗
二分类数据集构建
传统机器学习模型训练
PyTorch 深度学习模型训练
Validation Set 与 Early Stopping
模型保存与加载
样本预测
模型指标对比
实验文档整理
```

当前最佳模型是 Random Forest，当前最佳深度学习模型是 PyTorch MLP。

后续可以继续进入：

```txt
多分类任务
类别不平衡处理
误报与漏报分析
CNN-LSTM 或序列建模
模型调参和消融实验
```
