# Day7：多分类误报漏报分析与错误模式可视化

## 1. 今日目标

在 Day6 完成多分类类别不平衡优化实验的基础上，Day7 重点分析不同模型的误报、漏报和错误模式。

Day7 不再继续训练新模型，而是围绕已有模型回答以下问题：

1. 哪些模型整体错误数量最少；
2. 哪些模型攻击漏报最少；
3. 哪些模型正常流量误报最少；
4. 哪些攻击类别最容易被预测为 BENIGN；
5. 原始 CNN、Random Forest 和 Clipped Weighted CNN 的错误模式有什么区别；
6. 类别权重优化带来的误报和漏报变化是否符合预期。

本日重点分析三个模型：

| Model                | 选择原因                                |
| -------------------- | ----------------------------------- |
| CNN                  | 深度学习模型中 Accuracy 和 Weighted F1 表现最好 |
| Random Forest        | 当前多分类任务中综合表现最强                      |
| Clipped Weighted CNN | Macro Recall 表现最好，适合观察少数类漏报变化       |

---

## 2. 背景

在入侵检测任务中，仅看 Accuracy、Weighted F1 等整体指标是不够的。一个模型可能整体准确率很高，但仍然会漏报少数类攻击。

因此，除了模型整体指标外，还需要进一步分析：

* False Positive：正常流量被误报为攻击；
* False Negative：攻击流量被漏报为 BENIGN；
* Attack Misclassification：攻击被识别为另一种攻击；
* Top Error Pattern：最常见的错误预测类型。

Day7 的核心目标是从错误样本和混淆矩阵中提取更细粒度的错误模式，为后续可解释性分析和可视化 Dashboard 提供依据。

---

## 3. CNN 错误模式分析

原始 CNN 的错误分析结果如下：

| Metric        |  Value |
| ------------- | -----: |
| Test Samples  | 565553 |
| Error Samples |   1933 |
| Error Rate    | 0.0034 |

CNN 的 Top 错误模式主要包括：

| Error Pattern       | Count |
| ------------------- | ----: |
| BENIGN -> DoS       |   866 |
| WebAttack -> BENIGN |   373 |
| Bot -> BENIGN       |   245 |
| BENIGN -> PortScan  |   204 |
| DoS -> BENIGN       |   112 |

从结果可以看出，CNN 的主要问题有两个：

1. 部分 BENIGN 正常流量被误报为 DoS；
2. WebAttack 和 Bot 等少数类攻击容易被预测为 BENIGN。

其中，`WebAttack -> BENIGN` 和 `Bot -> BENIGN` 是比较严重的漏报模式，说明原始 CNN 虽然整体指标较高，但对少数类攻击仍然存在明显漏报问题。

CNN 的 Attack -> BENIGN 漏报主要包括：

| Error Pattern          | Count |
| ---------------------- | ----: |
| WebAttack -> BENIGN    |   373 |
| Bot -> BENIGN          |   245 |
| DoS -> BENIGN          |   112 |
| BruteForce -> BENIGN   |    36 |
| DDoS -> BENIGN         |    17 |
| PortScan -> BENIGN     |    11 |
| Infiltration -> BENIGN |     6 |

CNN 的 BENIGN -> Attack 误报主要包括：

| Error Pattern          | Count |
| ---------------------- | ----: |
| BENIGN -> DoS          |   866 |
| BENIGN -> PortScan     |   204 |
| BENIGN -> BruteForce   |    20 |
| BENIGN -> DDoS         |     6 |
| BENIGN -> Infiltration |     1 |

---

## 4. Random Forest 错误模式分析

Random Forest 的错误分析结果如下：

| Metric        |  Value |
| ------------- | -----: |
| Test Samples  | 565553 |
| Error Samples |    636 |
| Error Rate    | 0.0011 |

Random Forest 的 Top 错误模式主要包括：

| Error Pattern      | Count |
| ------------------ | ----: |
| BENIGN -> PortScan |   196 |
| PortScan -> BENIGN |   135 |
| Bot -> BENIGN      |    91 |
| BENIGN -> DoS      |    67 |
| DoS -> BENIGN      |    59 |

从结果可以看出，Random Forest 的错误数量明显少于 CNN。它的主要错误集中在：

1. BENIGN 与 PortScan 之间的混淆；
2. BENIGN 与 DoS 之间的混淆；
3. Bot 仍然存在一定漏报。

Random Forest 的 Attack -> BENIGN 漏报主要包括：

| Error Pattern          | Count |
| ---------------------- | ----: |
| PortScan -> BENIGN     |   135 |
| Bot -> BENIGN          |    91 |
| DoS -> BENIGN          |    59 |
| DDoS -> BENIGN         |    14 |
| WebAttack -> BENIGN    |    11 |
| BruteForce -> BENIGN   |     3 |
| Infiltration -> BENIGN |     3 |

Random Forest 的 BENIGN -> Attack 误报主要包括：

| Error Pattern       | Count |
| ------------------- | ----: |
| BENIGN -> PortScan  |   196 |
| BENIGN -> DoS       |    67 |
| BENIGN -> Bot       |    39 |
| BENIGN -> WebAttack |     2 |
| BENIGN -> DDoS      |     1 |

整体来看，Random Forest 在 CICIDS2017 的 Flow 表格特征上表现更稳定，不仅整体指标较高，实际错误样本数量也明显更少。

---

## 5. Clipped Weighted CNN 错误模式分析

Clipped Weighted CNN 的错误分析结果如下：

| Metric        |  Value |
| ------------- | -----: |
| Test Samples  | 565553 |
| Error Samples |  24757 |
| Error Rate    | 0.0438 |

Clipped Weighted CNN 的 Top 错误模式主要包括：

| Error Pattern          | Count |
| ---------------------- | ----: |
| BENIGN -> Bot          |  9296 |
| BENIGN -> PortScan     |  6570 |
| BENIGN -> DoS          |  4135 |
| BENIGN -> WebAttack    |  1930 |
| BENIGN -> DDoS         |  1280 |
| BENIGN -> BruteForce   |  1058 |
| BENIGN -> Infiltration |   245 |

从结果可以看出，Clipped Weighted CNN 的攻击漏报明显减少，但正常流量误报明显增加。这与 Day6 的实验结论一致：类别权重会让模型更加敏感，能够减少少数类攻击漏报，但也会导致更多 BENIGN 被预测为攻击。

Clipped Weighted CNN 的 Attack -> BENIGN 漏报主要包括：

| Error Pattern        | Count |
| -------------------- | ----: |
| DoS -> BENIGN        |    36 |
| DDoS -> BENIGN       |    10 |
| PortScan -> BENIGN   |     6 |
| WebAttack -> BENIGN  |     4 |
| Bot -> BENIGN        |     3 |
| BruteForce -> BENIGN |     2 |

Clipped Weighted CNN 的 BENIGN -> Attack 误报主要包括：

| Error Pattern          | Count |
| ---------------------- | ----: |
| BENIGN -> Bot          |  9296 |
| BENIGN -> PortScan     |  6570 |
| BENIGN -> DoS          |  4135 |
| BENIGN -> WebAttack    |  1930 |
| BENIGN -> DDoS         |  1280 |
| BENIGN -> BruteForce   |  1058 |
| BENIGN -> Infiltration |   245 |
| BENIGN -> Heartbleed   |     8 |

该模型适合强调“尽量减少攻击漏报”的场景，但不适合作为低误报场景下的默认模型。

---

## 6. 三个模型错误模式总对比

三个模型的错误总览如下：

| Model                | Total Errors | Attack -> BENIGN Errors | BENIGN -> Attack Errors | Attack -> Attack Errors |
| -------------------- | -----------: | ----------------------: | ----------------------: | ----------------------: |
| CNN                  |         1933 |                     800 |                    1097 |                      36 |
| Random Forest        |          636 |                     316 |                     305 |                      15 |
| Clipped Weighted CNN |        24757 |                      61 |                   24522 |                     174 |

最佳错误表现如下：

| Metric                         | Best Model           |
| ------------------------------ | -------------------- |
| Total Errors Fewest            | Random Forest        |
| Attack -> BENIGN Errors Fewest | Clipped Weighted CNN |
| BENIGN -> Attack Errors Fewest | Random Forest        |

从总对比可以看出：

1. Random Forest 总错误数最少，整体最稳定；
2. Random Forest 正常流量误报最少，更适合作为低误报告警系统的主模型；
3. Clipped Weighted CNN 攻击漏报最少，更适合强调安全敏感、宁可误报也不漏报的场景；
4. Clipped Weighted CNN 总错误数最多，主要原因是大量 BENIGN 被预测为攻击；
5. CNN 介于两者之间，但对 WebAttack 和 Bot 的漏报较明显。

---

## 7. 按类别错误率分析

按真实类别统计后，每个模型错误率最高的类别如下：

| Model                | Highest Error Class | Error Rate | Errors | Support |
| -------------------- | ------------------- | ---------: | -----: | ------: |
| CNN                  | WebAttack           |     0.8945 |    390 |     436 |
| Random Forest        | Infiltration        |     0.4286 |      3 |       7 |
| Clipped Weighted CNN | Infiltration        |     0.1429 |      1 |       7 |

每个模型攻击被判成 BENIGN 比例最高的类别如下：

| Model                | Highest Attack -> BENIGN Class |   Rate | Errors | Support |
| -------------------- | ------------------------------ | -----: | -----: | ------: |
| CNN                  | Infiltration                   | 0.8571 |      6 |       7 |
| Random Forest        | Infiltration                   | 0.4286 |      3 |       7 |
| Clipped Weighted CNN | WebAttack                      | 0.0092 |      4 |     436 |

该结果说明：

1. CNN 对 WebAttack 的整体错误率很高，说明其少数类识别能力不足；
2. CNN 和 Random Forest 对 Infiltration 都存在明显挑战，但 Infiltration 的测试样本只有 7 条，因此结果需要谨慎解释；
3. Clipped Weighted CNN 显著降低了 Attack -> BENIGN 漏报比例，尤其对 WebAttack 和 Bot 的漏报明显减少；
4. 但 Clipped Weighted CNN 的代价是大量 BENIGN 被误报为攻击。

---

## 8. 今日实验产物

Day7 新增分析脚本：

```txt
scripts/analysis/multiclass/analyze_cnn_error_patterns.py
scripts/analysis/multiclass/analyze_random_forest_error_patterns.py
scripts/analysis/multiclass/analyze_clipped_weighted_cnn_error_patterns.py
scripts/analysis/multiclass/compare_error_patterns.py
scripts/analysis/multiclass/compare_class_error_rates.py
scripts/analysis/multiclass/generate_error_analysis_summary.py
```

Day7 新增结果目录：

```txt
results/multiclass/cnn_error_patterns/
results/multiclass/random_forest_error_patterns/
results/multiclass/clipped_weighted_cnn_error_patterns/
results/multiclass/error_pattern_comparison/
results/multiclass/class_error_rate_comparison/
results/multiclass/error_analysis_summary/
```

主要输出文件包括：

```txt
cnn_error_pattern_summary.csv
random_forest_error_pattern_summary.csv
clipped_weighted_cnn_error_pattern_summary.csv
model_error_pattern_comparison.csv
class_error_rate_comparison.csv
day7_error_analysis_summary.md
day7_key_findings.csv
day7_highest_class_errors.csv
```

---

## 9. 今日结论

Day7 的核心结论如下：

1. Random Forest 是当前错误数量最少、整体最稳定的模型；
2. Random Forest 在总错误数和 BENIGN 误报控制方面明显优于 CNN；
3. CNN 主要问题是 WebAttack 和 Bot 等少数类攻击被预测为 BENIGN；
4. Clipped Weighted CNN 显著减少 Attack -> BENIGN 漏报；
5. Clipped Weighted CNN 的代价是大量正常流量被误报为攻击；
6. 类别权重优化验证了“减少漏报会增加误报”的安全检测权衡；
7. 对 IDS 系统而言，模型选择不能只看 Accuracy，需要结合误报、漏报和具体部署场景；
8. 如果追求整体稳定性，Random Forest 更适合作为主模型；
9. 如果追求减少攻击漏报，Clipped Weighted CNN 可作为高敏感度参考模型；
10. 后续可以进一步做特征重要性分析和错误样本可解释性分析。

---

## 10. 下一步计划

后续可以继续进入：

1. Random Forest 特征重要性分析；
2. 错误样本特征分布分析；
3. SHAP / Permutation Importance 可解释性分析；
4. 将错误模式结果接入可视化 Dashboard；
5. 设计模型选择策略，例如“低误报模式”和“高召回模式”。
