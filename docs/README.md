# AI-NIDS Documentation

This directory contains the experiment notes, script index, and glossary for the AI-NIDS project.

The documentation is organized by development stages. Each `Day*.md` file records the goal, implementation process, experiment results, and conclusions of a specific stage.

## Documentation Roadmap

| Document      | Topic                           | Description                                                                                   |
| ------------- | ------------------------------- | --------------------------------------------------------------------------------------------- |
| `Day1.md`     | Dataset Understanding           | Initial understanding of CICIDS2017, file structure, labels, and data overview                |
| `Day2.md`     | Binary Dataset Construction     | Build the BENIGN vs Attack binary classification dataset                                      |
| `Day3.md`     | Binary Model Training           | Train and compare binary classifiers such as Logistic Regression, Random Forest, MLP, and CNN |
| `Day4.md`     | Multiclass Dataset Construction | Build the multiclass dataset and define attack categories                                     |
| `Day5.md`     | Multiclass Model Comparison     | Compare Logistic Regression, Random Forest, MLP, and CNN on multiclass classification         |
| `Day6.md`     | Class Imbalance Optimization    | Study weighted and clipped weighted loss for MLP and CNN                                      |
| `Day7.md`     | Error Pattern Analysis          | Analyze false positives, false negatives, Attack -> BENIGN errors, and model error patterns   |
| `scripts.md`  | Script Index                    | Explain the purpose of each major script in the project                                       |
| `glossary.md` | Glossary                        | Define important IDS, machine learning, and evaluation terms used in the project              |

## Recommended Reading Order

If you are new to this project, read the documents in this order:

```txt
Day1.md
Day2.md
Day3.md
Day4.md
Day5.md
Day6.md
Day7.md
scripts.md
glossary.md
```

This order follows the actual development process of the project, from dataset preparation to model training, class imbalance optimization, and error pattern analysis.

## Experiment Flow

The project follows this experimental flow:

```txt
Dataset Preparation
        ↓
Binary Classification
        ↓
Multiclass Classification
        ↓
Model Comparison
        ↓
Class Imbalance Optimization
        ↓
Error Pattern Analysis
        ↓
Future Explainability and Dashboard
```

## Key Experiment Stages

### 1. Dataset Preparation

The raw CICIDS2017 CSV files are cleaned and transformed into processed datasets for binary and multiclass classification.

Related scripts:

```txt
scripts/data/
scripts/eda/
```

### 2. Binary Classification

The binary task classifies network traffic into:

```txt
BENIGN
Attack
```

Implemented models include Logistic Regression, Random Forest, MLP, and CNN.

Related results:

```txt
results/model_comparison/
results/logistic_regression/
results/random_forest/
results/mlp_torch/
results/cnn_torch/
```

### 3. Multiclass Classification

The multiclass task classifies traffic into 9 categories:

```txt
BENIGN
Bot
BruteForce
DDoS
DoS
Heartbleed
Infiltration
PortScan
WebAttack
```

Related results:

```txt
results/multiclass/model_comparison/
results/multiclass/logistic_regression/
results/multiclass/random_forest/
results/multiclass/mlp_torch/
results/multiclass/cnn_torch/
```

### 4. Class Imbalance Optimization

The project studies how class imbalance affects minority attack detection.

Implemented experiments include:

```txt
Weighted MLP
Clipped Weighted MLP
Weighted CNN
Clipped Weighted CNN
```

Related results:

```txt
results/multiclass/mlp_weight_experiments/
results/multiclass/cnn_weight_experiments/
results/multiclass/deep_learning_weight_experiments/
```

### 5. Error Pattern Analysis

The project analyzes model errors from three perspectives:

```txt
Attack -> BENIGN
BENIGN -> Attack
Attack -> Attack
```

This helps explain the trade-off between missed attacks and false alarms.

Related results:

```txt
results/multiclass/error_pattern_comparison/
results/multiclass/class_error_rate_comparison/
results/multiclass/error_analysis_summary/
```

## Main Conclusions

The current project results show that:

1. Random Forest performs strongly on CICIDS2017 flow-based tabular features.
2. CNN has high overall performance but still misses minority attacks such as WebAttack and Bot.
3. Weighted deep learning models improve minority-class recall but increase false positives.
4. Clipped Weighted CNN significantly reduces Attack -> BENIGN missed detections.
5. Random Forest has the fewest total errors and the fewest BENIGN -> Attack false positives.
6. IDS model selection should consider not only Accuracy, but also false positives, false negatives, and deployment goals.

## Future Documentation Plan

Future documents may include:

| Document                | Description                                                            |
| ----------------------- | ---------------------------------------------------------------------- |
| `research_papers.md`    | Notes from IDS, CICIDS2017, class imbalance, and explainability papers |
| `github_research.md`    | Comparison with existing open-source IDS projects                      |
| `feature_importance.md` | Random Forest feature importance and model explainability              |
| `dashboard.md`          | Dashboard design and visualization notes                               |
| `api.md`                | FastAPI inference service design                                       |
