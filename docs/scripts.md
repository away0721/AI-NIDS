# Scripts 说明文档

本文档用于记录 AI-NIDS 项目中 `scripts/` 目录下现有脚本的作用，避免后续忘记每个文件是干什么的。

---

## eda.py

作用：

用于对单个 CICIDS2017 CSV 文件进行探索性数据分析。

主要功能：

- 读取指定 CSV 文件
- 查看数据规模
- 查看 Label 分布
- 查看基础统计信息
- 查看缺失值
- 查看异常值

当前主要分析过的文件：

- `Monday-WorkingHours.pcap_ISCX.csv`
- `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`

重要发现：

- Monday 文件全部为 `BENIGN`
- PortScan 文件包含 `BENIGN` 和 `PortScan`
- `Flow Bytes/s` 存在少量缺失值
- `Flow Duration` 存在负数异常值

---

## dataset_overview.py

作用：

用于遍历 CICIDS2017 的全部 CSV 文件，查看每个文件的数据规模和 Label 分布。

主要功能：

- 遍历 `MachineLearningCVE` 目录下所有 CSV 文件
- 输出每个 CSV 的 shape
- 输出每个 CSV 的 Label 分布

重要发现：

- CICIDS2017 一共包含 8 个 CSV 文件
- 不同文件对应不同日期和攻击场景
- 有些文件只包含正常流量
- 有些文件包含正常流量和攻击流量
- 数据集中存在明显类别不平衡问题

---

## label_overview.py

作用：

用于统计整个 CICIDS2017 数据集的全局 Label 分布。

主要功能：

- 遍历全部 CSV 文件
- 累加每个 Label 的样本数量
- 输出整个数据集的 Label 总分布

当前统计结果：

- `BENIGN`: 2273097
- `DoS Hulk`: 231073
- `PortScan`: 158930
- `DDoS`: 128027
- `DoS GoldenEye`: 10293
- `FTP-Patator`: 7938
- `SSH-Patator`: 5897
- `DoS slowloris`: 5796
- `DoS Slowhttptest`: 5499
- `Bot`: 1966
- `Web Attack � Brute Force`: 1507
- `Web Attack � XSS`: 652
- `Infiltration`: 36
- `Web Attack � Sql Injection`: 21
- `Heartbleed`: 11

重要发现：

- `BENIGN` 样本数量最多
- 攻击类别之间样本数量差异很大
- `DoS Hulk`、`PortScan`、`DDoS` 样本较多
- `Heartbleed`、`Sql Injection`、`Infiltration` 样本极少
- 后续不适合直接从完整多分类开始
- 更适合先做 `BENIGN vs ATTACK` 二分类任务

---

## binary_label_overview.py

作用：

用于统计 CICIDS2017 转换为二分类任务后的 Label 分布。

二分类映射规则：

- `BENIGN` -> 0
- 其它所有攻击类型 -> 1

主要功能：

- 遍历全部 CSV 文件
- 统计正常流量数量
- 统计攻击流量数量
- 输出二分类样本总数和比例

当前统计结果：

- `BENIGN / 0`: 2273097
- `ATTACK / 1`: 557646
- `TOTAL`: 2830743

当前比例：

- `BENIGN`: 80.30%
- `ATTACK`: 19.70%

重要发现：

- 二分类任务存在一定类别不平衡
- 但不算极端失衡
- 可以先用该任务作为 AI-NIDS 的第一个建模目标

---

## build_binary_dataset.py

作用：

用于构建 AI-NIDS 项目的第一个二分类训练数据集。

主要功能：

- 读取 CICIDS2017 的全部 8 个 CSV 文件
- 去除列名前后的空格
- 将原始多分类 `Label` 映射为二分类标签 `binary_label`
- 合并全部 CSV 数据
- 清洗 `Infinity` 和 `NaN`
- 删除 `Flow Duration < 0` 的异常数据
- 删除原始多分类 `Label` 列
- 保存处理后的二分类数据集

二分类映射规则：

- `BENIGN` -> 0
- 其它所有攻击类型 -> 1

输出文件：

`data/processed/binary_dataset.csv`

运行结果：

- 清洗前行数：2830743
- 清洗后行数：2827761
- 删除行数：2982
- 最终数据规模：2827761 行 × 79 列

清洗后二分类分布：

- `binary_label = 0`: 2271205
- `binary_label = 1`: 556556

重要发现：

- 清洗删除的数据量很少，约占总数据的 0.1%
- 清洗后仍保持约 80% 正常流量、20% 攻击流量
- 该数据集可以作为后续 Random Forest Baseline 的输入数据

---

## check_binary_dataset.py

作用：

用于检查处理后的二分类数据集是否可以正常读取，以及数据结构是否正确。

主要功能：

- 读取 `data/processed/binary_dataset.csv`
- 查看数据规模
- 查看前 5 行数据
- 查看全部列名
- 查看二分类 Label 分布
- 检查是否存在缺失值

当前检查结果：

- 数据规模：2827761 行 × 79 列
- 包含 78 个特征列
- 包含 1 个标签列：`binary_label`
- `binary_label = 0`: 2271205
- `binary_label = 1`: 556556
- 缺失值数量：0

重要发现：

- 二分类数据集已经成功生成
- 原始多分类 `Label` 已删除
- 数据可以作为后续 Baseline 模型的输入
- 原始数据中存在重复列名问题，例如 `Fwd Header Length` 和 `Fwd Header Length.1`

---

## prepare_xy_check.py

作用：

用于检查二分类数据集是否可以正确拆分为模型训练所需的特征矩阵 `X` 和标签 `y`。

主要功能：

- 读取 `data/processed/binary_dataset.csv`
- 将 `binary_label` 之外的列作为特征矩阵 `X`
- 将 `binary_label` 作为标签 `y`
- 查看 `X` 和 `y` 的数据规模
- 查看部分特征列名
- 查看标签分布

当前检查结果：

- 原始数据规模：2827761 行 × 79 列
- 特征矩阵 `X`：2827761 行 × 78 列
- 标签 `y`：2827761 个值
- `binary_label = 0`: 2271205
- `binary_label = 1`: 556556

重要发现：

- 数据集已经可以被拆分为机器学习模型需要的输入和输出
- `X` 表示网络流量特征
- `y` 表示该 Flow 是否为攻击
- 后续模型训练将基于 `X` 和 `y` 进行

---

## train_test_split_check.py

作用：

用于检查二分类数据集是否可以正确划分为训练集和测试集。

主要功能：

- 读取 `data/processed/binary_dataset.csv`
- 拆分特征矩阵 `X` 和标签 `y`
- 使用 `train_test_split` 划分训练集和测试集
- 检查训练集和测试集的数据规模
- 检查训练集和测试集的标签比例

当前检查结果：

- 原始数据规模：2827761 行 × 79 列
- 特征矩阵 `X`：2827761 行 × 78 列
- 标签 `y`：2827761 个值
- 训练集 `X_train`：2262208 行 × 78 列
- 测试集 `X_test`：565553 行 × 78 列
- 训练集 `y_train`：2262208 个值
- 测试集 `y_test`：565553 个值

训练集 Label 比例：

- `0`: 80.3181%
- `1`: 19.6819%

测试集 Label 比例：

- `0`: 80.3182%
- `1`: 19.6818%

重要发现：

- 数据集已经可以正确划分为训练集和测试集
- `stratify=y` 保证了训练集和测试集的类别比例基本一致
- 后续可以基于该划分方式训练第一个 Baseline 模型

---

## train_random_forest.py

作用：

用于训练 AI-NIDS 项目的第一个二分类 Baseline 模型。

主要功能：

- 读取 `data/processed/binary_dataset.csv`
- 拆分特征矩阵 `X` 和标签 `y`
- 使用 `train_test_split` 划分训练集和测试集
- 训练 `RandomForestClassifier`
- 在测试集上进行预测
- 计算 Accuracy、Precision、Recall、F1 Score
- 生成 Confusion Matrix
- 保存文本实验报告
- 保存结构化 CSV 实验结果
- 保存混淆矩阵图
- 保存指标柱状图

输入文件：

`data/processed/binary_dataset.csv`

输出目录：

`results/random_forest/`

输出文件：

- `random_forest_binary_report.txt`
- `random_forest_binary_metrics.csv`
- `confusion_matrix.png`
- `metrics_bar.png`

重要说明：

该脚本是项目的第一个二分类 Baseline 实验，用于后续和 CNN、CNN-LSTM 等模型进行对比。

当前项目中，Random Forest 的相关实验结果统一保存在 `results/random_forest/` 目录下。