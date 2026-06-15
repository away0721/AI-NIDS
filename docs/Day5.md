# Day5：多分类模型训练、预测与模型对比

## 1. 今日目标

今日主要完成 CICIDS2017 多分类任务中的模型训练、单样本预测验证以及模型对比实验。此前已经完成多分类数据集构建、多分类 Random Forest 训练与预测，因此今天继续完成 Logistic Regression、PyTorch MLP、PyTorch CNN 三个模型，并最终通过统一对比脚本汇总四个模型的多分类性能。

本阶段的目标不是单纯追求 Accuracy，而是重点观察不同模型在类别不平衡场景下的表现，尤其关注少数类攻击如 Bot、Infiltration、WebAttack、Heartbleed 的 Precision、Recall 和 F1-score。

---

## 2. 多分类 Logistic Regression

### 2.1 模型设置

多分类 Logistic Regression 使用 `StandardScaler` 对特征进行标准化，并使用 `LabelEncoder` 将文本类别标签编码为数字类别。模型使用 `solver="saga"`，并设置 `class_weight="balanced"` 以缓解类别不平衡问题。

训练过程中，模型在达到 `max_iter=1000` 后仍未完全收敛，出现 `ConvergenceWarning`。这说明在 CICIDS2017 这种大规模、多类别且类别极度不平衡的数据集上，Logistic Regression 训练成本较高，且线性模型表达能力有限。

### 2.2 训练结果

多分类 Logistic Regression 的测试集结果如下：

```txt
Accuracy:           0.7841
Macro Precision:    0.3777
Macro Recall:       0.8978
Macro F1 Score:     0.4223
Weighted Precision: 0.9396
Weighted Recall:    0.7841
Weighted F1 Score:  0.8406
```

该模型的 Macro Recall 较高，说明它倾向于尽可能识别少数类攻击；但 Macro Precision 和 Macro F1 较低，说明它产生了大量误报。尤其是 Bot、Infiltration、WebAttack 等类别，虽然召回率较高，但精确率极低，表示模型经常将正常流量或其他类别误判为少数类攻击。

### 2.3 单样本预测结果分析

Logistic Regression 的 practice 结果中，45 条抽样样本预测正确 37 条，错误 8 条。按类别统计如下：

```txt
BENIGN:       2 / 5
Bot:          3 / 5
BruteForce:   5 / 5
DDoS:         5 / 5
DoS:          4 / 5
Heartbleed:   5 / 5
Infiltration: 4 / 5
PortScan:     5 / 5
WebAttack:    4 / 5
```

从样本预测可以看出，Logistic Regression 会将部分 BENIGN 高置信度误判为 Bot 或 BruteForce。这与整体评估结果一致，说明 `class_weight="balanced"` 虽然增强了少数类识别能力，但也导致正常流量误报增加。因此 Logistic Regression 更适合作为线性基线模型，而不适合作为当前任务的主模型。

---

## 3. 多分类 PyTorch MLP

### 3.1 模型设置

多分类 MLP 使用 78 个 Flow 特征作为输入，输出层为 9 个神经元，对应 9 个攻击类别。训练时使用 `CrossEntropyLoss`，预测时通过 `argmax` 选取概率最高的类别。

与二分类 MLP 不同：

```txt
二分类：输出 1 个 logit，使用 BCEWithLogitsLoss，经过 sigmoid 后判断是否攻击。
多分类：输出 9 个 logits，使用 CrossEntropyLoss，通过 argmax 得到预测类别。
```

MLP 使用训练集、验证集和测试集三部分数据，并加入 Early Stopping。训练集用于更新参数，验证集用于选择最佳 epoch，测试集只用于最终评估。

### 3.2 GPU 环境配置

今天将 PyTorch 环境从 CPU 版切换为 GPU 版，当前环境信息如下：

```txt
torch version: 2.5.1+cu121
cuda version: 12.1
cuda available: True
gpu: NVIDIA GeForce RTX 4060 Laptop GPU
```

训练和预测时均显示：

```txt
当前训练设备：cuda
当前预测设备：cuda
```

说明 MLP 和后续 CNN 已经能够使用 GPU 运行。

### 3.3 训练结果

MLP 在第 20 个 epoch 触发 Early Stopping，最佳 epoch 为 15：

```txt
Early Stopping 触发，停止于 Epoch 20
最佳 Epoch：15
最佳 Validation Loss：0.020377
```

测试集结果如下：

```txt
Accuracy:           0.9929
Macro Precision:    0.9869
Macro Recall:       0.7367
Macro F1 Score:     0.7747
Weighted Precision: 0.9929
Weighted Recall:    0.9929
Weighted F1 Score:  0.9925
```

MLP 整体效果明显优于 Logistic Regression，说明非线性神经网络能够学习更复杂的 Flow 特征关系。但从分类报告看，MLP 对少数类攻击仍然存在明显漏报。

典型少数类表现：

```txt
Bot recall:          0.3376
Infiltration recall: 0.2857
WebAttack recall:    0.0482
```

尤其是 WebAttack，测试集中有 436 条真实样本，但只有 21 条被正确识别，大量 WebAttack 被误判为 BENIGN。

### 3.4 单样本预测结果分析

MLP practice 中，45 条抽样样本预测正确 31 条，错误 14 条。按类别统计如下：

```txt
BENIGN:       5 / 5
Bot:          1 / 5
BruteForce:   5 / 5
DDoS:         5 / 5
DoS:          4 / 5
Heartbleed:   4 / 5
Infiltration: 0 / 5
PortScan:     5 / 5
WebAttack:    2 / 5
```

MLP 对 BENIGN、BruteForce、DDoS、PortScan 等大类或特征明显的类别识别较好，但对 Bot、Infiltration、WebAttack 等少数类攻击识别较差。多个少数类样本被高置信度误判为 BENIGN，说明 MLP 相比 Logistic Regression 更保守，误报少但漏报多。

---

## 4. 多分类 PyTorch CNN

### 4.1 模型设置

多分类 CNN 将每条 Flow 的 78 个特征视作一维特征序列，输入形状从 `[N, 78]` 转换为 `[N, 1, 78]`。模型使用 `Conv1d` 提取局部特征，再通过全连接层输出 9 个类别 logits。

CNN 同样使用：

```txt
CrossEntropyLoss
Adam Optimizer
Validation Set
Early Stopping
GPU Training
```

### 4.2 训练结果

CNN 在第 30 个 epoch 触发 Early Stopping，最佳 epoch 为 25：

```txt
Early Stopping 触发，停止于 Epoch 30
最佳 Epoch：25
最佳 Validation Loss：0.010991
```

测试集结果如下：

```txt
Accuracy:           0.9966
Macro Precision:    0.9402
Macro Recall:       0.7335
Macro F1 Score:     0.7697
Weighted Precision: 0.9966
Weighted Recall:    0.9966
Weighted F1 Score:  0.9962
```

CNN 的 Accuracy 和 Weighted F1 高于 MLP，说明它在整体样本上的分类能力更强。但 CNN 的 Macro F1 略低于 MLP，说明它对少数类整体改善不明显。

典型少数类表现如下：

```txt
Bot recall:          0.3734
Infiltration recall: 0.1429
WebAttack recall:    0.1055
```

CNN 对 WebAttack 的召回率略高于 MLP，但仍然很低。真实 WebAttack 中有大量样本被误判为 BENIGN，说明 CNN 仍然没有解决少数类攻击漏报问题。

### 4.3 单样本预测结果分析

CNN practice 中，45 条抽样样本预测正确 36 条，错误 9 条。按类别统计如下：

```txt
BENIGN:       5 / 5
Bot:          1 / 5
BruteForce:   5 / 5
DDoS:         5 / 5
DoS:          5 / 5
Heartbleed:   5 / 5
Infiltration: 3 / 5
PortScan:     5 / 5
WebAttack:    2 / 5
```

与 MLP 相比，CNN 在 practice 抽样中整体更稳定，尤其 Infiltration 的抽样表现更好。但从完整测试集指标来看，Infiltration 的 recall 仍然较低，因此不能仅凭抽样结果判断模型已经解决该类别问题。

CNN 的典型错误仍然是：

```txt
Bot -> BENIGN
Infiltration -> BENIGN
WebAttack -> BENIGN
```

这说明 CNN 的主要风险仍是少数类攻击漏报。

---

## 5. 多分类模型对比

今日最后实现了 `compare_multiclass_models.py`，用于读取四个模型的 metrics CSV，并生成统一的多分类模型对比表和对比图。

输出文件：

```txt
results/multiclass/model_comparison/multiclass_model_comparison.csv
results/multiclass/model_comparison/multiclass_model_comparison.png
```

最终对比结果如下：

```txt
Random Forest:
Accuracy           0.9989
Macro F1 Score     0.9463
Weighted F1 Score  0.9989

Logistic Regression:
Accuracy           0.7841
Macro F1 Score     0.4223
Weighted F1 Score  0.8406

PyTorch MLP:
Accuracy           0.9929
Macro F1 Score     0.7747
Weighted F1 Score  0.9925

PyTorch CNN:
Accuracy           0.9966
Macro F1 Score     0.7697
Weighted F1 Score  0.9962
```

最佳模型结果：

```txt
Accuracy 最佳：Random Forest
Macro F1 最佳：Random Forest
Weighted F1 最佳：Random Forest
```

---

## 6. 阶段性结论

本阶段完成了 CICIDS2017 多分类任务中四类模型的完整实验闭环。实验表明：

第一，Random Forest 在当前 Flow 特征数据上表现最强，不仅整体 Accuracy 最高，Macro F1 和 Weighted F1 也最高，说明它在大类和小类之间取得了更好的平衡。

第二，Logistic Regression 作为线性基线模型表现最弱。由于使用 `class_weight="balanced"`，它对少数类攻击召回较高，但误报严重，经常将 BENIGN 误判为少数类攻击。

第三，MLP 明显优于 Logistic Regression，说明神经网络能够学习非线性特征关系。但 MLP 对少数类攻击仍然偏保守，存在 Bot、Infiltration、WebAttack 漏报问题。

第四，CNN 的 Accuracy 和 Weighted F1 高于 MLP，但 Macro F1 略低于 MLP。CNN 在整体样本上更强，但没有从根本上解决少数类攻击识别困难的问题。

第五，类别不平衡仍然是多分类 IDS 的核心问题。尤其是 Bot、Infiltration、WebAttack 等类别，由于样本数量少，模型容易出现漏报或误报。后续需要考虑 class weight、SMOTE、过采样、欠采样、focal loss、特征选择和小类别优化等方向。

---

## 7. 下一步计划

后续工作可以围绕以下方向继续推进：

```txt
1. 完善 README 和实验文档
2. 补充 docs/scripts.md 中新增脚本说明
3. 补充 docs/glossary.md 中新增概念
4. 做类别不平衡优化实验
5. 做特征重要性与 Top-K 特征轻量化实验
6. 调研近几年 IDS 论文和 GitHub 项目
7. 设计 AI-NIDS 可视化 Dashboard
```

从毕设角度看，后续可以将项目定位为：

```txt
基于 CICIDS2017 的轻量级、可解释、可视化网络入侵检测系统设计与实现
```

重点研究问题是：

```txt
在类别不平衡的多分类入侵检测任务中，如何提升少数类攻击识别能力，并通过特征解释和可视化系统增强模型可用性。
```
