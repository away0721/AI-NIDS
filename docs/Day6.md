# Day6：多分类类别不平衡分析与深度学习加权优化实验

## 1. 今日目标

在 Day5 完成多分类模型训练与模型对比的基础上，Day6 重点分析多分类任务中的类别不平衡问题，并围绕 MLP 和 CNN 进行类别权重优化实验。实验主要关注少数类攻击的 Recall、Macro Recall、Macro F1 以及误报变化情况。

本日重点包括：

1. 分析 MLP 和 CNN 在少数类攻击上的漏报问题；
2. 在 MLP 和 CNN 中引入 class weight；
3. 对比原始模型、Weighted 模型和 Clipped Weighted 模型；
4. 分析类别权重对少数类 Recall 和整体误报的影响；
5. 总结不同优化策略下的模型取舍。

## 2. 问题背景

在 CICIDS2017 多分类任务中，类别分布极度不平衡。BENIGN、DoS、DDoS、PortScan 等类别样本数量较多，而 Bot、WebAttack、Infiltration、Heartbleed 等类别样本数量很少。原始 MLP 和 CNN 虽然整体 Accuracy 较高，但对少数类攻击存在明显漏报问题。

原始 MLP 的少数类 Recall 表现如下：

| Class        | Recall |
| ------------ | -----: |
| Bot          | 0.3376 |
| Infiltration | 0.2857 |
| WebAttack    | 0.0482 |

原始 CNN 的少数类 Recall 表现如下：

| Class        | Recall |
| ------------ | -----: |
| Bot          | 0.3734 |
| Infiltration | 0.1429 |
| WebAttack    | 0.1055 |

这说明，仅依靠 Accuracy 不能充分评价入侵检测模型的真实效果。对于 IDS 场景而言，少数类攻击虽然样本少，但安全风险高，因此需要重点关注少数类 Recall、Macro Recall 和 Macro F1。

## 3. MLP 类别权重实验

为了缓解少数类攻击漏报问题，本实验在原始 MLP 基础上分别进行了 Weighted MLP 和 Clipped Weighted MLP 实验。

Weighted MLP 使用 `compute_class_weight(class_weight="balanced")` 计算类别权重，并将其传入 `CrossEntropyLoss`。实验结果显示，Weighted MLP 显著提升了少数类攻击的 Recall，但也导致大量 BENIGN 正常流量被误判为攻击，整体 Accuracy 和 Macro F1 明显下降。

由于直接使用 balanced class weight 会导致 Heartbleed、Infiltration 等极少数类权重过大，因此进一步引入 Clipped Weighted MLP，将最大类别权重限制为 100。裁剪后，模型误报有所缓解，Accuracy、Macro F1 和 Weighted F1 均优于直接 Weighted MLP，但仍未超过原始 MLP。

MLP 权重实验对比如下：

| Experiment           | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 |
| -------------------- | -------: | --------------: | -----------: | -------: | ----------: |
| MLP                  |   0.9929 |          0.9869 |       0.7367 |   0.7747 |      0.9925 |
| Weighted MLP         |   0.9169 |          0.5034 |       0.9618 |   0.5770 |      0.9328 |
| Clipped Weighted MLP |   0.9413 |          0.5903 |       0.9482 |   0.6430 |      0.9517 |

实验结果表明，类别权重可以有效提升少数类攻击的召回能力，但过大的类别权重会导致模型过度偏向少数类，从而产生严重误报。权重裁剪能够在一定程度上缓解该问题。

## 4. CNN 类别权重实验

在 CNN 模型上，本实验同样进行了原始 CNN、Weighted CNN 和 Clipped Weighted CNN 的对比。

原始 CNN 在 Accuracy 和 Weighted F1 上表现最好，说明其整体分类能力较强。但原始 CNN 对 Bot、Infiltration 和 WebAttack 等少数类攻击的 Recall 较低，存在明显漏报问题。

Weighted CNN 引入 balanced class weight 后，少数类 Recall 明显提升，但由于类别权重过大，模型产生大量误报，导致 Accuracy、Macro Precision 和 Macro F1 明显下降。

Clipped Weighted CNN 将最大类别权重限制为 100 后，相比 Weighted CNN 明显缓解了误报问题，同时保持了较高的 Macro Recall，是更合理的加权版本。

CNN 权重实验对比如下：

| Experiment           | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 |
| -------------------- | -------: | --------------: | -----------: | -------: | ----------: |
| CNN                  |   0.9966 |          0.9402 |       0.7335 |   0.7697 |      0.9962 |
| Weighted CNN         |   0.8969 |          0.4223 |       0.9560 |   0.4800 |      0.9180 |
| Clipped Weighted CNN |   0.9562 |          0.5383 |       0.9719 |   0.5988 |      0.9655 |

实验结果表明，Clipped Weighted CNN 在 Macro Recall 上表现最好，说明其对少数类攻击最敏感，能够显著减少漏报。但由于少数类 Precision 仍然偏低，说明模型仍存在一定误报问题。

## 5. 深度学习权重实验总对比

综合 MLP 和 CNN 的权重实验结果如下：

| Experiment           | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 |
| -------------------- | -------: | --------------: | -----------: | -------: | ----------: |
| MLP                  |   0.9929 |          0.9869 |       0.7367 |   0.7747 |      0.9925 |
| Weighted MLP         |   0.9169 |          0.5034 |       0.9618 |   0.5770 |      0.9328 |
| Clipped Weighted MLP |   0.9413 |          0.5903 |       0.9482 |   0.6430 |      0.9517 |
| CNN                  |   0.9966 |          0.9402 |       0.7335 |   0.7697 |      0.9962 |
| Weighted CNN         |   0.8969 |          0.4223 |       0.9560 |   0.4800 |      0.9180 |
| Clipped Weighted CNN |   0.9562 |          0.5383 |       0.9719 |   0.5988 |      0.9655 |

最佳实验结果如下：

| Metric       | Best Experiment      |
| ------------ | -------------------- |
| Accuracy     | CNN                  |
| Macro Recall | Clipped Weighted CNN |
| Macro F1     | MLP                  |
| Weighted F1  | CNN                  |

从实验结果可以看出，不同指标下的最优模型并不相同。CNN 在整体 Accuracy 和 Weighted F1 上表现最好，说明其对大多数样本的分类能力最强；MLP 在 Macro F1 上表现最好，说明其在类别平均意义下的综合表现较优；Clipped Weighted CNN 在 Macro Recall 上表现最好，说明其最适合减少少数类攻击漏报。

## 6. 今日实验结论

Day6 的核心结论如下：

1. 原始 MLP 和 CNN 在整体指标上表现较好，但对少数类攻击存在漏报；
2. 直接使用 balanced class weight 可以显著提升少数类 Recall，但会引入大量误报；
3. 类别权重不是越大越好，过大的权重会导致模型过度偏向少数类；
4. Clipped class weight 能够缓解极端权重带来的误报问题；
5. 原始 CNN 适合作为追求整体准确率的主模型；
6. Clipped Weighted CNN 适合作为强调少数类攻击召回的参考模型；
7. 在 IDS 场景中，需要根据实际需求在漏报和误报之间进行权衡。

## 7. 今日产物

本日新增或更新的主要结果包括：

* Weighted MLP 训练结果；
* Clipped Weighted MLP 训练结果；
* MLP 权重实验对比结果；
* Weighted CNN 训练结果；
* Clipped Weighted CNN 训练结果；
* CNN 权重实验对比结果；
* 深度学习权重实验总对比结果。

相关结果保存在：

```txt
results/multiclass/mlp_torch_weighted/
results/multiclass/mlp_torch_weighted_clipped/
results/multiclass/mlp_weight_experiments/
results/multiclass/cnn_torch_weighted/
results/multiclass/cnn_torch_weighted_clipped/
results/multiclass/cnn_weight_experiments/
results/multiclass/deep_learning_weight_experiments/
```

## 8. 下一步计划

后续可以继续进行误报漏报样本分析，重点统计不同模型最常见的错误类型，例如：

* WebAttack -> BENIGN
* Bot -> BENIGN
* Infiltration -> BENIGN
* BENIGN -> Bot
* BENIGN -> WebAttack

通过错误模式分析，可以进一步理解不同模型的行为差异，并为后续可解释性分析、特征重要性分析和可视化 Dashboard 提供依据。
