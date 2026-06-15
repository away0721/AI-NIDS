# Glossary 术语表

本文档用于记录 AI-NIDS 项目学习过程中遇到的重要概念，方便后续复习、写报告和准备答辩。

---

## 1. 数据集与网络流量相关术语

### Dataset

英文：Dataset

中文：数据集

含义：

用于训练、验证和测试模型的数据集合。

在 AI-NIDS 项目中，当前主要使用 CICIDS2017 数据集。

---

### CICIDS2017

英文：Canadian Institute for Cybersecurity Intrusion Detection System 2017

中文：CICIDS2017 入侵检测数据集

含义：

一个常用的网络入侵检测公开数据集，包含正常流量和多种攻击流量。

在本项目中，当前使用的是其中的 `MachineLearningCSV` 版本。该版本已经将原始网络流量提取成了机器学习可用的表格特征。

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

在二分类阶段，Label 被转换为：

```txt
BENIGN -> 0
ATTACK -> 1
```

在多分类阶段，Label 被转换为更高层级的攻击类别，例如：

```txt
BENIGN
DoS
DDoS
PortScan
BruteForce
WebAttack
Bot
Infiltration
Heartbleed
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

不同类别的样本数量差距很大。

例如 CICIDS2017 中：

```txt
BENIGN: 2271205
Heartbleed: 11
Infiltration: 36
```

类别不平衡会导致模型更偏向样本数量多的类别。即使模型 Accuracy 很高，也可能对少数类攻击识别效果很差。

在 IDS 场景中，类别不平衡是一个重要问题，因为少数类攻击虽然样本少，但安全风险可能很高。

---

### Minority Class

英文：Minority Class

中文：少数类

含义：

样本数量较少的类别。

在本项目中，以下类别属于典型少数类：

```txt
Bot
Infiltration
Heartbleed
WebAttack
```

少数类通常更难学习，容易被模型忽略。

---

### Majority Class

英文：Majority Class

中文：多数类

含义：

样本数量较多的类别。

在本项目中，BENIGN 是最典型的多数类。DoS、DDoS、PortScan 也比 Bot、Infiltration、WebAttack 等类别多很多。

多数类样本多，模型更容易学习到它们的特征，但也可能因此忽略少数类。

---

## 2. 分类任务相关术语

### Binary Classification

英文：Binary Classification

中文：二分类

含义：

只判断样本属于两个类别中的哪一个。

在 AI-NIDS 二分类阶段：

```txt
BENIGN
ATTACK
```

模型只需要判断当前 Flow 是正常流量还是攻击流量。

---

### Multi-Class Classification

英文：Multi-Class Classification

中文：多分类

含义：

判断样本属于多个类别中的哪一个。

例如：

```txt
BENIGN
DoS
DDoS
PortScan
BruteForce
WebAttack
Bot
Infiltration
Heartbleed
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
单位时间内连接失败次数
某个源 IP 的连接频率
访问不同端口的数量
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
BENIGN -> 0
Bot -> 1
DDoS -> 3
```

---

### LabelEncoder

英文：LabelEncoder

中文：标签编码器

含义：

`LabelEncoder` 是 scikit-learn 中用于将文本类别标签转换为数字编号的工具。

在本项目中，多分类标签会被编码为：

```txt
0: BENIGN
1: Bot
2: BruteForce
3: DDoS
4: DoS
5: Heartbleed
6: Infiltration
7: PortScan
8: WebAttack
```

模型训练时使用数字标签，最终展示结果时再通过 `LabelEncoder` 还原成原始类别名称。

---

## 3. 数据划分与预处理相关术语

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

它应该只在最终评估时使用。

---

### Stratify

英文：Stratify

中文：分层抽样

含义：

在划分训练集、验证集和测试集时，保持各个类别的比例基本一致。

例如原始数据中：

```txt
BENIGN: 80%
ATTACK: 20%
```

使用 `stratify=y` 后，训练集和测试集也会尽量保持类似比例。

在类别不平衡任务中，分层抽样非常重要，否则少数类可能在某个集合中过少甚至缺失。

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

### Logistic Regression

英文：Logistic Regression

中文：逻辑回归

含义：

一种常用的线性分类模型。

特点：

```txt
模型简单
训练速度快
适合作为线性 Baseline
可解释性较强
难以学习复杂非线性关系
```

在本项目中，Logistic Regression 用于二分类和多分类实验。

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
对非线性关系建模能力较好
```

在当前多分类实验中，Random Forest 是综合表现最强的模型之一。

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

其中：

```txt
N：样本数量
78：Flow 特征数量
```

MLP 适合处理表格特征，但在类别不平衡场景中也可能出现少数类漏报。

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

它内部会把 logit 转换为概率，并计算二分类交叉熵损失。

在本项目的二分类 MLP 和 CNN 中使用过：

```python
nn.BCEWithLogitsLoss()
```

---

### CrossEntropyLoss

英文：Cross Entropy Loss

中文：交叉熵损失

含义：

多分类任务中常用的损失函数。

模型会为每个类别输出一个 logit，`CrossEntropyLoss` 会在内部结合 softmax 和真实标签计算损失。真实类别对应的概率越低，loss 越大；真实类别对应的概率越高，loss 越小。

普通写法：

```python
criterion = nn.CrossEntropyLoss()
```

带类别权重的写法：

```python
criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
```

在本项目中，多分类 MLP 和 CNN 使用 `CrossEntropyLoss`。

---

### Logit / Logits

英文：Logit / Logits

中文：未归一化预测值 / 原始分数

含义：

模型最后一层直接输出的原始数值。

Logit 不是概率，可能是任意实数。

在二分类中，模型通常输出一个 logit，需要通过 Sigmoid 转换为概率。

在多分类中，模型会输出多个 logits，每个类别对应一个分数，需要通过 Softmax 转换为概率。

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

### Softmax

英文：Softmax

中文：Softmax 函数

含义：

Softmax 用于将多个类别的 logits 转换为概率分布。转换后所有类别概率之和为 1。

例如：

```txt
logits:  [2.1, 0.3, -1.2]
softmax: [0.80, 0.14, 0.06]
```

预测时通常选择概率最大的类别作为最终分类结果。

---

### Argmax

英文：Argmax

中文：最大值索引

含义：

`argmax` 表示取最大值所在的位置。

在多分类预测中，模型会输出多个类别概率或 logits，`argmax` 用于选择分数最高的类别编号。

例如：

```txt
概率: [0.80, 0.14, 0.06]
argmax: 0
```

说明模型预测类别为第 0 类。

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

本项目常用设置：

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

### CUDA

英文：CUDA

中文：CUDA 并行计算平台

含义：

NVIDIA 提供的 GPU 并行计算平台。

在 PyTorch 中，如果 CUDA 可用，就可以把模型和数据放到 GPU 上训练，从而加速深度学习模型训练。

常见判断方式：

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

---

### GPU

英文：Graphics Processing Unit

中文：图形处理器

含义：

GPU 擅长进行大规模并行计算。

在本项目中，PyTorch MLP 和 CNN 可以使用 GPU 训练；而 scikit-learn 的 Logistic Regression 和 Random Forest 通常主要使用 CPU。

---

## 6. 类别权重与不平衡优化相关术语

### Class Weight

英文：Class Weight

中文：类别权重

含义：

类别权重是一种处理类别不平衡的方法。它会在训练过程中给不同类别设置不同的损失权重。

样本数量少的类别权重更大，样本数量多的类别权重更小。

这样做的目的是让模型在训练时更加重视少数类样本。

在 PyTorch 中，可以这样使用：

```python
criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
```

这并不是在预测阶段直接修改概率，而是在训练阶段修改 loss。少数类样本如果预测错误，会产生更大的损失，从而对模型参数更新产生更大影响。

---

### Balanced Class Weight

英文：Balanced Class Weight

中文：平衡类别权重

含义：

Balanced class weight 是根据类别样本数量自动计算类别权重的方法。

类别样本越少，权重越大；类别样本越多，权重越小。

在 scikit-learn 中，可以这样计算：

```python
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.arange(num_classes),
    y=y_train,
)
```

优点：

```txt
提升少数类 Recall
减少少数类漏报
```

缺点：

```txt
当某些类别样本极少时，权重可能非常大
模型可能过度偏向少数类
可能导致大量误报
```

---

### Clipped Class Weight

英文：Clipped Class Weight

中文：裁剪类别权重

含义：

Clipped class weight 是对 balanced class weight 的改进。它会限制类别权重的最大值，避免极少数类权重过大。

例如：

```python
MAX_CLASS_WEIGHT = 100.0
class_weights = np.clip(class_weights, a_min=None, a_max=MAX_CLASS_WEIGHT)
```

在本项目中，直接使用 balanced class weight 会让 Heartbleed、Infiltration 等极少数类获得非常大的权重，导致模型误报严重。使用 clipped class weight 后，可以在保持少数类 Recall 提升的同时，缓解部分误报问题。

---

### Weighted MLP

英文：Weighted MLP

中文：加权 MLP

含义：

在原始 MLP 的基础上，将类别权重传入 `CrossEntropyLoss`，使模型训练时更加重视少数类攻击。

在本项目中，Weighted MLP 显著提升了少数类攻击 Recall，但也带来了更多误报。

---

### Clipped Weighted MLP

英文：Clipped Weighted MLP

中文：裁剪加权 MLP

含义：

在 Weighted MLP 的基础上，对类别权重设置最大值限制，避免极少数类权重过大。

在本项目中，Clipped Weighted MLP 相比 Weighted MLP 更稳定，误报有所减少，但整体表现仍未超过原始 MLP。

---

### Weighted CNN

英文：Weighted CNN

中文：加权 CNN

含义：

在原始 CNN 的基础上，将类别权重传入 `CrossEntropyLoss`，使 CNN 更重视少数类攻击。

在本项目中，Weighted CNN 的少数类 Recall 明显提升，但误报严重，整体 Accuracy 和 Macro F1 下降。

---

### Clipped Weighted CNN

英文：Clipped Weighted CNN

中文：裁剪加权 CNN

含义：

在 Weighted CNN 的基础上，对类别权重设置最大值限制，避免极端类别权重影响训练。

在本项目中，Clipped Weighted CNN 在 Macro Recall 上表现最好，说明它最能减少少数类攻击漏报，但少数类 Precision 仍然偏低，说明仍存在一定误报。

---

### Conservative Model

英文：Conservative Model

中文：保守模型

含义：

保守模型指模型不太愿意预测少数类攻击，更倾向于预测大类或 BENIGN。

在本项目中，原始 MLP 和原始 CNN 相对保守。它们整体 Accuracy 很高，但 Bot、Infiltration、WebAttack 等少数类 Recall 较低，说明它们容易漏报少数类攻击。

---

### Over-sensitive Model

英文：Over-sensitive Model

中文：过度敏感模型

含义：

过度敏感模型指模型对攻击类别过于敏感，容易把正常流量误判成攻击。

在本项目中，直接使用 balanced class weight 的 Weighted MLP 和 Weighted CNN 就出现了这种情况。它们的少数类 Recall 很高，但 Precision 较低，说明模型报出了很多攻击，但其中不少是误报。

---

### Trade-off

英文：Trade-off

中文：取舍 / 权衡

含义：

Trade-off 表示在两个目标之间进行取舍。

在入侵检测中，常见的取舍是误报和漏报之间的平衡。

```txt
模型更敏感：可能减少漏报，但增加误报
模型更保守：可能减少误报，但增加漏报
```

本项目中的类别权重实验说明，class weight 可以提升少数类攻击 Recall，但也可能降低 Precision 和 Accuracy，因此需要根据实际安全场景选择合适的模型。

---

## 7. 评估指标相关术语

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

多分类混淆矩阵中，行通常表示真实类别，列通常表示预测类别。通过混淆矩阵可以观察模型最常见的误分类类型。

---

### Accuracy

英文：Accuracy

中文：准确率

含义：

预测正确样本占总样本的比例。

公式：

```txt
Accuracy = 预测正确的样本数 / 总样本数
```

注意：

在类别不平衡的数据集上，Accuracy 可能具有迷惑性。例如 BENIGN 样本很多时，模型只要大量预测 BENIGN，也可能得到很高的 Accuracy，但它可能漏掉很多少数类攻击。

---

### Precision

英文：Precision

中文：精确率

含义：

模型预测为某一类的样本中，有多少是真的属于这一类。

可以简单理解为：

```txt
Precision = 报得准不准
```

例如 Bot precision 低，说明模型预测出了很多 Bot，但其中很多其实不是真正的 Bot，也就是误报较多。

---

### Recall

英文：Recall

中文：召回率

含义：

某一类真实样本中，有多少被模型成功找出来。

可以简单理解为：

```txt
Recall = 找得全不全
```

例如 WebAttack recall 低，说明真实 WebAttack 中有很多没有被模型识别出来，也就是漏报较多。

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

### Macro Precision

英文：Macro Precision

中文：宏平均精确率

含义：

Macro Precision 是所有类别 Precision 的平均值，每个类别权重相同。

它不会因为 BENIGN 样本多就更偏向 BENIGN，因此适合观察模型在类别不平衡情况下的平均表现。

---

### Macro Recall

英文：Macro Recall

中文：宏平均召回率

含义：

Macro Recall 是所有类别 Recall 的平均值，每个类别权重相同。

在 IDS 多分类任务中，Macro Recall 很重要，因为它可以反映模型是否能够识别少数类攻击。Macro Recall 越高，通常说明模型对各类攻击都更敏感，少数类攻击的漏报更少。

注意：

Macro Recall 高不一定代表模型整体最好。比如 Weighted MLP 和 Weighted CNN 的 Macro Recall 很高，但 Precision 较低，说明它们虽然更容易发现少数类攻击，但也会把很多正常流量误报为攻击。

---

### Macro F1

英文：Macro F1

中文：宏平均 F1 分数

含义：

Macro F1 是所有类别 F1-score 的平均值，每个类别权重相同。

它适合衡量类别不平衡场景下模型的综合表现。如果模型只在 BENIGN、DoS、DDoS、PortScan 等大类上表现好，而在 Bot、Infiltration、WebAttack 等少数类上表现差，Macro F1 通常不会太高。

在本项目中，Macro F1 比 Accuracy 更适合观察模型对不同类别的整体平衡能力。

---

### Weighted Precision

英文：Weighted Precision

中文：加权精确率

含义：

Weighted Precision 是按照每个类别样本数量加权后的 Precision。样本越多的类别，对最终结果影响越大。

在 CICIDS2017 这类类别不平衡数据集中，Weighted Precision 容易受到 BENIGN、DoS、DDoS、PortScan 等大类影响。

因此，Weighted Precision 很高并不一定代表模型对少数类攻击识别得很好。

---

### Weighted Recall

英文：Weighted Recall

中文：加权召回率

含义：

Weighted Recall 是按照每个类别样本数量加权后的 Recall。样本多的类别对最终结果影响更大。

在多分类任务中，Weighted Recall 通常和 Accuracy 比较接近。

如果数据集中 BENIGN 样本占比很大，那么模型只要在 BENIGN 上表现很好，Weighted Recall 就可能很高。

---

### Weighted F1

英文：Weighted F1

中文：加权 F1 分数

含义：

Weighted F1 是按照每个类别样本数量加权后的 F1-score。

Weighted F1 可以反映模型在整体数据分布下的表现，但在类别不平衡场景中，它可能被大类主导。因此，即使 Weighted F1 很高，也不代表模型对少数类攻击识别得很好。

在本项目中，CNN 的 Weighted F1 很高，说明它整体分类能力很强；但它的少数类 Recall 较低，说明仍然存在少数类漏报问题。

---

### False Positive

英文：False Positive

中文：误报

含义：

真实是正常流量，但模型预测为攻击。

例如：

```txt
真实类别：BENIGN
预测类别：WebAttack
```

这就是一次误报。

在 IDS 中，误报会增加安全运维人员的告警负担。如果误报太多，系统会频繁产生告警，导致告警疲劳。

---

### False Negative

英文：False Negative

中文：漏报

含义：

真实是攻击流量，但模型预测为正常。

例如：

```txt
真实类别：WebAttack
预测类别：BENIGN
```

这就是一次漏报。

在 IDS 中，漏报通常更危险，因为真实攻击可能没有被系统发现。

---

### BENIGN Recall

英文：BENIGN Recall

中文：正常流量召回率

含义：

BENIGN Recall 表示真实正常流量中，有多少被模型正确识别为 BENIGN。

如果 BENIGN Recall 下降，说明有更多正常流量被误判为攻击，模型误报增加。

在本项目中，Weighted MLP 和 Weighted CNN 虽然提升了少数类攻击 Recall，但 BENIGN Recall 明显下降，说明误报增加。

---

## 8. 文件格式相关术语

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
LabelEncoder
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
Weighted MLP 模型参数
Weighted CNN 模型参数
```

---

## 9. 当前项目阶段理解

截至 Day6，AI-NIDS 已经完成二分类与多分类阶段的基础实验闭环，并进一步完成了深度学习模型的类别不平衡优化实验。

已完成内容包括：

```txt
数据探索
数据清洗
二分类数据集构建
多分类数据集构建
传统机器学习模型训练
PyTorch 深度学习模型训练
Validation Set 与 Early Stopping
模型保存与加载
样本预测
模型指标对比
类别不平衡分析
Weighted MLP 实验
Clipped Weighted MLP 实验
Weighted CNN 实验
Clipped Weighted CNN 实验
深度学习权重实验总对比
实验文档整理
```

当前阶段结论：

```txt
Random Forest 是当前多分类任务中综合表现最强的传统机器学习模型。
CNN 在深度学习模型中 Accuracy 和 Weighted F1 表现最好。
MLP 在 Macro F1 上表现较好。
Clipped Weighted CNN 在 Macro Recall 上表现最好，适合减少少数类攻击漏报。
直接使用 balanced class weight 会显著提升少数类 Recall，但也会增加误报。
裁剪类别权重可以缓解误报问题，在少数类召回和整体性能之间取得折中。
```

后续可以继续进入：

```txt
误报与漏报样本分析
错误模式统计
特征重要性分析
可解释性分析
CNN-LSTM 或序列建模
模型调参和消融实验
可视化 Dashboard
```
