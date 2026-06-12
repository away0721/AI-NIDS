# Day4：深度学习训练策略优化

## 1. 今日目标

Day4 的主要目标不是继续增加新模型，而是对已经完成的 PyTorch 深度学习模型进行训练流程规范化改进。

在 Day3 中，MLP 和 CNN 都采用固定 `EPOCHS = 10` 的方式训练。虽然模型能够正常运行并得到测试集结果，但这种方式存在一个问题：训练轮数是人工指定的，无法判断模型是否训练不足，也无法判断继续训练是否会导致过拟合。

因此，Day4 将深度学习模型从固定 epoch 训练方式升级为：

```txt
train set + validation set + test set
max_epochs + early stopping
```

即不再简单地固定训练 10 轮，而是设置最大训练轮数，并通过验证集 loss 自动判断模型是否还需要继续训练。

---

## 2. Train / Validation / Test 三者关系

本次实验将数据集划分为三部分：

```txt
训练集 train set
验证集 validation set
测试集 test set
```

三者作用如下：

```txt
训练集：用于模型学习参数
验证集：用于每个 epoch 后评估模型是否还在提升
测试集：用于最终评估模型效果
```

训练集参与模型参数更新，会执行：

```txt
前向传播
计算 loss
反向传播
更新参数
```

验证集不参与参数更新，只用于观察模型在未参与训练的数据上的表现。验证阶段只进行前向传播和 loss 计算，不执行反向传播，也不会更新模型参数。

测试集只在最终阶段使用一次，用于衡量模型在未见数据上的最终表现。

---

## 3. StandardScaler 的正确使用

本次实验继续使用 `StandardScaler` 对特征进行标准化。

标准化的正确流程是：

```txt
先划分 train / validation / test
只用训练集 fit scaler
用同一个 scaler transform 训练集、验证集和测试集
```

对应逻辑为：

```python
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)
```

其中，`fit` 只能用于训练集。因为 `fit` 会计算特征均值和标准差，如果在验证集或测试集上执行 `fit`，就会把验证集或测试集的信息提前泄露给训练过程，造成 Data Leakage。

---

## 4. Train Loss、Validation Loss 与 Test Accuracy 的区别

`loss` 是模型训练过程中的优化目标，用于衡量模型预测结果与真实标签之间的差距。

训练集 loss 会参与反向传播和参数更新，因此它可以反映模型是否正在学习训练数据。

验证集 loss 不参与参数更新，它用于观察模型在未参与训练的数据上的表现。如果训练集 loss 持续下降，而验证集 loss 开始上升，通常说明模型可能开始过拟合。

测试集 accuracy、precision、recall 和 f1-score 是最终评估指标。它们不会参与训练，也不会用于 early stopping，只用于最终报告模型效果。

可以简单理解为：

```txt
train loss：模型学习训练数据的错误信号
validation loss：判断模型是否泛化、是否该停止训练
test metrics：最终测试集上的模型表现
```

---

## 5. Early Stopping 原理

Early Stopping 的作用是在训练过程中监控验证集 loss。如果验证集 loss 连续若干轮没有明显下降，就提前停止训练，并回滚到验证集 loss 最低时的模型参数。

本次实验设置为：

```python
MAX_EPOCHS = 100
PATIENCE = 5
MIN_DELTA = 1e-4
```

含义如下：

```txt
MAX_EPOCHS：最多训练 100 轮
PATIENCE：验证集 loss 连续 5 轮没有明显改善就停止
MIN_DELTA：验证集 loss 至少下降 0.0001 才认为是有效改善
```

这种方式比固定训练 10 轮更加合理。模型不会盲目训练满 100 轮，也不会因为某一轮验证集 loss 短暂变差就立刻停止，而是允许训练过程出现一定波动。

---

## 6. PyTorch MLP 实验结果

MLP 模型加入 Early Stopping 后，训练过程如下：

```txt
最大训练轮数：100
最佳 Epoch：9
最佳 Validation Loss：0.024161
Early Stopping 触发 Epoch：14
```

最终测试集结果为：

```txt
Accuracy:  0.9908
Precision: 0.9921
Recall:    0.9607
F1 Score:  0.9762
```

混淆矩阵为：

```txt
[[453390    852]
 [  4370 106941]]
```

相比固定 10 epoch 的 MLP，Early Stopping 后模型整体表现更稳定，Precision 和 F1 Score 有明显提升，误报数量明显下降。但 Recall 有所下降，说明模型变得更加谨慎，漏报数量有所增加。

这一结果说明，Early Stopping 并不一定让所有指标同时提升，但它可以根据验证集 loss 选择更合理的模型参数，避免盲目训练。

---

## 7. PyTorch CNN 实验结果

CNN 模型也加入了相同的训练策略，包括 validation set、Early Stopping 和最佳模型保存。

训练过程如下：

```txt
最大训练轮数：100
最佳 Epoch：16
最佳 Validation Loss：0.063374
Early Stopping 触发 Epoch：21
```

最终测试集结果为：

```txt
Accuracy:  0.9702
Precision: 0.9246
Recall:    0.9239
F1 Score:  0.9243
```

混淆矩阵为：

```txt
[[445853   8389]
 [  8468 102843]]
```

CNN 的训练过程中，Validation Loss 出现了多次波动，例如某些 epoch 的验证集 loss 明显升高，但后续又出现新的最优值。这说明训练过程并不是严格平滑下降的，会受到 batch 更新、shuffle、dropout、学习率和模型结构等因素影响。

因此，Early Stopping 使用 `PATIENCE = 5` 是合理的，因为它不会因为某一轮 loss 短暂变差就停止训练，而是观察连续多轮是否没有明显改善。

---

## 8. 二分类模型对比

重新生成模型对比后，四个模型结果如下：

| Model               | Accuracy | Precision | Recall | F1 Score |
| ------------------- | -------: | --------: | -----: | -------: |
| Random Forest       |   0.9991 |    0.9967 | 0.9986 |   0.9976 |
| Logistic Regression |   0.9162 |    0.7129 | 0.9614 |   0.8187 |
| PyTorch MLP         |   0.9908 |    0.9921 | 0.9607 |   0.9762 |
| PyTorch CNN         |   0.9702 |    0.9246 | 0.9239 |   0.9243 |

从结果看，Random Forest 仍然是当前二分类任务中表现最好的模型，四项指标都非常高。PyTorch MLP 在加入 Early Stopping 后表现明显提升，是当前深度学习模型中效果最好的。CNN 在本次 Early Stopping 版本中表现低于 MLP，说明在当前 78 维 Flow 统计特征上，简单的 1D CNN 并没有比 MLP 更有优势。

Logistic Regression 作为线性基线模型，Recall 较高，但 Precision 较低，说明它更容易将正常流量误判为攻击流量。

---

## 9. 今日理解总结

Day4 的核心收获是理解了训练集、验证集和测试集的区别，并将深度学习训练流程从固定 epoch 升级为更加规范的 Early Stopping 机制。

训练集用于学习参数，验证集用于训练过程中判断模型是否继续提升，测试集用于最终评估。验证集和测试集都不会参与反向传播，也不会更新模型参数。

同时，loss 和 accuracy 并不是同一种东西。loss 是训练过程中的优化目标，既关注预测是否正确，也关注预测的置信度；accuracy、precision、recall 和 f1-score 是最终评估指标，用于从不同角度评价模型效果。

本次改进让项目从“简单跑通模型”进一步升级为“具有规范训练流程的实验系统”。

---

## 10. 后续计划

后续可以继续从以下方向推进：

```txt
1. 将 Day4 的训练策略和实验结果同步到 README
2. 继续完善 docs/scripts.md 和 docs/glossary.md
3. 进入多分类任务，将攻击类型进一步细分
4. 分析类别不平衡问题
5. 尝试 CNN-LSTM 或更合理的序列建模方案
6. 进行误报和漏报样本分析
```

Day4 暂时不继续增加新模型，而是完成代码、实验结果和文档收口。
