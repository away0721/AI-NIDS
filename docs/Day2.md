# Day2

## 数据集分析

使用 CICIDS2017 数据集。

包含 8 个 CSV 文件。

每个 CSV 对应不同日期和攻击场景。

---

## 重要理解

1. 一行数据代表一个 Flow，而不是一个 Packet。

2. 一个 Flow 由多个 Packet 聚合而成。

3. 每个 Flow 被提取为 79 个特征。

4. 最后一列 Label 为攻击类型。

---

## Label 分布

Monday:
BENIGN

Tuesday:
BENIGN
FTP-Patator
SSH-Patator

Wednesday:
BENIGN
DoS Hulk
DoS GoldenEye
DoS Slowloris
DoS SlowHTTPTest
Heartbleed

Thursday:
Web Attack
Infiltration

Friday:
Bot
PortScan
DDoS

---

## 数据问题

发现：

Flow Bytes/s 存在少量缺失值。

Flow Duration 存在负数异常值。

训练前需要进行数据清洗。

---

## 后续路线

Phase 1:
BENIGN vs ATTACK

Phase 2:
合并类别后的多分类

Phase 3:
全部类别分类