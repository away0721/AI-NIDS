## CNN

Convolutional Neural Network

中文：卷积神经网络

作用：

自动提取特征。

---

## LSTM

Long Short-Term Memory

中文：长短期记忆网络

作用：

学习时间序列关系。

---

## Feature

中文：特征

用于描述网络流量的数据。

例如：

- Flow Duration
- Packets
- Bytes/s

---

## Feature Engineering

中文：特征工程

从原始数据中构造更有价值的特征。

例如：

10秒内访问的不同端口数。

---

## Encoding

中文：编码

将字符串转换为模型可处理的数字形式。

例如：

TCP → [1,0,0]

UDP → [0,1,0]

ICMP → [0,0,1]

---

## Normalization

中文：归一化

将不同量纲的数据缩放到相近范围。

避免大数值特征主导模型训练。

---

## Dataset

中文：数据集

用于训练和测试模型的数据集合。

---

## Label

中文：标签

模型最终需要预测的目标。

例如：

- Normal
- DDoS
- PortScan

## Accuracy

中文：准确率

表示预测正确样本占总样本的比例。

在类别不平衡的数据集上可能具有迷惑性。

---

## Recall

中文：召回率

表示真实存在的目标样本中，被模型成功发现的比例。

在 IDS 中通常代表：

发现攻击的能力。

---

## Precision

中文：精确率

表示模型判定为攻击的样本中，真正是攻击的比例。

反映误报情况。

---

## F1 Score

中文：F1分数

综合衡量 Precision 和 Recall 的指标。

通常用于评价分类模型整体性能。

## Overfitting

中文：过拟合

模型过度学习训练数据中的细节和噪声。

在训练集表现很好。

但在未见过的数据上表现较差。

本质：

模型记住了样本，而没有学会规律。

## Underfitting

中文：欠拟合

模型没有充分学习数据规律。

表现：

- Train Accuracy 低
- Test Accuracy 也低

本质：

模型能力不足或训练不足。

## Baseline

中文：基线模型

用于与目标模型进行对比的参考模型。

作用：

- 验证模型有效性
- 提供实验对照
- 衡量模型改进幅度

常见 Baseline：

- Random Forest
- XGBoost
- MLP

## Generalization

中文：泛化能力

模型在未见过的新数据上的表现能力。

泛化能力强：

说明模型学会了规律。

泛化能力弱：

说明模型可能只记住了训练数据。

## Epoch

中文：训练轮次

模型完整学习一次训练集称为一个 Epoch。

例如：

Epoch 1

表示完整遍历训练集一次。

Epoch 10

表示完整遍历训练集十次。

## Early Stopping

中文：提前停止

当模型开始过拟合时提前结束训练。

目的：

避免模型继续记忆训练数据。

## Train Set

中文：训练集

用于训练模型的数据。

## Test Set

中文：测试集

用于评估模型泛化能力的数据。

不参与训练。

## Flow

英文：Flow

中文：网络流

作用：

由多个 Packet 聚合形成的一次网络通信。

在 CICIDS2017 中：

一行数据 = 一个 Flow。

---

## Packet

英文：Packet

中文：数据包

作用：

网络传输的最小单位。

多个 Packet 可以组成一个 Flow。

---

## Five Tuple

英文：Five Tuple

中文：五元组

作用：

用于唯一标识一个 Flow。

包括：

- Source IP
- Destination IP
- Source Port
- Destination Port
- Protocol

---

## EDA

英文：Exploratory Data Analysis

中文：探索性数据分析

作用：

在训练模型之前理解数据集。

常见内容：

- 查看数据规模
- 查看 Label 分布
- 查看统计信息
- 查看缺失值
- 查看异常值

---

## Data Cleaning

英文：Data Cleaning

中文：数据清洗

作用：

处理脏数据。

例如：

- 缺失值（NaN）
- Infinity
- 异常值
- 重复数据

---

## Missing Value

英文：Missing Value

中文：缺失值

作用：

表示某个特征没有数据。

例如：

NaN。

训练前通常需要处理。

---

## Outlier

英文：Outlier

中文：异常值

作用：

不符合业务逻辑的数据。

例如：

Flow Duration = -13。

持续时间理论上不应该小于 0。

---

## Class Imbalance

英文：Class Imbalance

中文：类别不平衡

作用：

不同类别样本数量差异过大。

例如：

DoS Hulk：231073

Heartbleed：11

可能导致模型偏向样本数量较多的类别。

---

## Baseline

英文：Baseline

中文：基线模型

作用：

作为后续模型比较的参考标准。

例如：

- Random Forest
- Logistic Regression

通常先建立 Baseline，再尝试更复杂的模型。

---

## Binary Classification

英文：Binary Classification

中文：二分类

作用：

只判断是否属于攻击。

例如：

- BENIGN
- ATTACK

---

## Multi-Class Classification

英文：Multi-Class Classification

中文：多分类

作用：

判断具体攻击类型。

例如：

- BENIGN
- DDoS
- PortScan
- Bot
- Web Attack

等多个类别。

## Data Leakage

英文：Data Leakage

中文：数据泄露

作用：

指模型训练过程中使用了本不应该提前知道的信息，导致测试结果虚高。

典型例子：

先对整个数据集做归一化，再划分训练集和测试集。

问题：

这种做法会让测试集的均值、标准差等统计信息提前参与训练过程，使模型评估结果不够真实。

正确做法：

先划分训练集和测试集，再只使用训练集拟合归一化器，最后用同一个归一化器处理训练集和测试集。

在代码中可以使用 `Pipeline` 避免数据泄露。