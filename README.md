# AI-NIDS

AI-NIDS is a machine learning based Network Intrusion Detection System project built on the CICIDS2017 dataset.
The project focuses on binary classification, multiclass attack classification, class imbalance optimization, and error pattern analysis for intrusion detection.

Unlike a simple model training demo, this project aims to build a reproducible experimental pipeline for understanding how different machine learning and deep learning models behave in network intrusion detection scenarios.

## Overview

Network Intrusion Detection Systems need to identify malicious traffic from large-scale network flow data. In real-world IDS scenarios, the major challenge is not only achieving high accuracy, but also reducing missed attacks and controlling false alarms.

This project explores several key questions:

* How well do traditional machine learning models perform on IDS flow features?
* How do deep learning models such as MLP and CNN compare with Random Forest?
* How does class imbalance affect minority attack detection?
* Can weighted loss improve attack recall?
* What kinds of errors do different models make?
* Which models are better for low false alarms, and which are better for reducing missed attacks?

## Key Features

* Binary intrusion detection: BENIGN vs Attack
* Multiclass intrusion detection across 9 traffic categories
* Traditional machine learning models:

  * Logistic Regression
  * Random Forest
* Deep learning models:

  * MLP
  * CNN
* Class imbalance experiments:

  * Weighted MLP
  * Clipped Weighted MLP
  * Weighted CNN
  * Clipped Weighted CNN
* Error pattern analysis:

  * Attack -> BENIGN false negatives
  * BENIGN -> Attack false positives
  * Attack -> Attack misclassification
* Model comparison reports and visualizations
* Experiment documentation from Day1 to Day7
* Reproducible script-based workflow

## Dataset

This project uses the CICIDS2017 dataset.

The dataset is organized locally as:

```txt
data/
├── raw/
│   └── MachineLearningCSV/
└── processed/
    ├── binary_dataset.csv
    └── multiclass_dataset.csv
```

The raw and processed datasets are not committed to GitHub because of file size limitations.

The multiclass task uses the following categories:

| Label ID | Class        |
| -------: | ------------ |
|        0 | BENIGN       |
|        1 | Bot          |
|        2 | BruteForce   |
|        3 | DDoS         |
|        4 | DoS          |
|        5 | Heartbleed   |
|        6 | Infiltration |
|        7 | PortScan     |
|        8 | WebAttack    |

## Project Structure

```txt
AI-NIDS/
├── data/                 # Local dataset files, ignored by Git
│   ├── raw/              # Raw CICIDS2017 CSV files
│   └── processed/        # Processed binary and multiclass datasets
├── docs/                 # Experiment notes, script index, and glossary
├── models/               # Trained model artifacts, ignored by Git
├── notebooks/            # Reserved for exploratory analysis
├── results/              # Metrics, reports, confusion matrices, and visualizations
├── scripts/              # Data processing, EDA, model training, and analysis scripts
│   ├── data/             # Dataset construction and validation
│   ├── eda/              # Exploratory data analysis
│   ├── models/           # Binary and multiclass model training / prediction
│   └── analysis/         # Error pattern and false-positive / false-negative analysis
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
└── .gitignore            # Ignore data, models, virtual environment, and cache files
```

## Experiment Roadmap

| Stage | Description                                                                          |
| ----- | ------------------------------------------------------------------------------------ |
| Day1  | Dataset preparation and basic data understanding                                     |
| Day2  | Binary classification dataset construction                                           |
| Day3  | Binary model training and comparison                                                 |
| Day4  | Multiclass dataset construction and baseline modeling                                |
| Day5  | Multiclass model comparison with Logistic Regression, Random Forest, MLP, and CNN    |
| Day6  | Class imbalance optimization with weighted and clipped weighted deep learning models |
| Day7  | Error pattern analysis, false positive analysis, and false negative analysis         |

## Models

### Binary Classification

The binary task classifies traffic into:

```txt
BENIGN
Attack
```

Implemented models:

* Logistic Regression
* Random Forest
* MLP
* CNN

### Multiclass Classification

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

Implemented models:

* Logistic Regression
* Random Forest
* MLP
* CNN
* Weighted MLP
* Clipped Weighted MLP
* Weighted CNN
* Clipped Weighted CNN

## Key Results

### Binary Classification

The binary classification experiments compare traditional machine learning and deep learning models on the BENIGN vs Attack task.

Main result files:

```txt
results/model_comparison/binary_model_comparison.csv
results/model_comparison/binary_model_comparison.png
```

Model-specific outputs include:

```txt
results/logistic_regression/
results/random_forest/
results/mlp_torch/
results/cnn_torch/
```

These folders contain metrics, classification reports, confusion matrices, training curves, and sample predictions.

### Multiclass Classification

The multiclass experiments compare Logistic Regression, Random Forest, MLP, and CNN.

Main result files:

```txt
results/multiclass/model_comparison/multiclass_model_comparison.csv
results/multiclass/model_comparison/multiclass_model_comparison.png
```

Model-specific outputs include:

```txt
results/multiclass/logistic_regression/
results/multiclass/random_forest/
results/multiclass/mlp_torch/
results/multiclass/cnn_torch/
```

The current experiments show that Random Forest performs very strongly on CICIDS2017 flow-based tabular features.

## Class Imbalance Experiments

IDS datasets often suffer from severe class imbalance. Minority attacks such as Bot, WebAttack, Infiltration, and Heartbleed have far fewer samples than BENIGN, DoS, DDoS, or PortScan.

To study this problem, this project implements:

* Weighted MLP
* Clipped Weighted MLP
* Weighted CNN
* Clipped Weighted CNN

Main comparison files:

```txt
results/multiclass/mlp_weight_experiments/mlp_weight_experiments_comparison.csv
results/multiclass/mlp_weight_experiments/mlp_weight_experiments_comparison.png

results/multiclass/cnn_weight_experiments/cnn_weight_experiments_comparison.csv
results/multiclass/cnn_weight_experiments/cnn_weight_experiments_comparison.png

results/multiclass/deep_learning_weight_experiments/deep_learning_weight_experiments_comparison.csv
results/multiclass/deep_learning_weight_experiments/deep_learning_weight_experiments_comparison.png
```

Main findings:

| Finding                    | Explanation                                                               |
| -------------------------- | ------------------------------------------------------------------------- |
| Original MLP / CNN         | High overall accuracy, but weaker minority-class recall                   |
| Weighted MLP / CNN         | Much higher minority-class recall, but many more false positives          |
| Clipped Weighted MLP / CNN | More balanced than direct weighted loss, but still increases false alarms |
| Random Forest              | Strong overall stability on tabular flow features                         |

The results show a clear IDS trade-off:

```txt
Reducing missed attacks usually increases false alarms.
```

## Error Pattern Analysis

Day7 focuses on understanding model errors beyond standard metrics.

The project compares three representative models:

| Model                | Reason                        |
| -------------------- | ----------------------------- |
| CNN                  | Strong deep learning baseline |
| Random Forest        | Best overall stable model     |
| Clipped Weighted CNN | Strongest attack recall model |

Error types analyzed:

| Error Type       | Meaning                                               |
| ---------------- | ----------------------------------------------------- |
| Attack -> BENIGN | Attack traffic is missed as normal traffic            |
| BENIGN -> Attack | Normal traffic is falsely reported as attack          |
| Attack -> Attack | Attack traffic is classified as the wrong attack type |

Main result folders:

```txt
results/multiclass/cnn_error_patterns/
results/multiclass/random_forest_error_patterns/
results/multiclass/clipped_weighted_cnn_error_patterns/
results/multiclass/error_pattern_comparison/
results/multiclass/class_error_rate_comparison/
results/multiclass/error_analysis_summary/
```

### Error Pattern Summary

| Model                | Total Errors | Attack -> BENIGN Errors | BENIGN -> Attack Errors | Attack -> Attack Errors |
| -------------------- | -----------: | ----------------------: | ----------------------: | ----------------------: |
| CNN                  |         1933 |                     800 |                    1097 |                      36 |
| Random Forest        |          636 |                     316 |                     305 |                      15 |
| Clipped Weighted CNN |        24757 |                      61 |                   24522 |                     174 |

### Best Models by Error Type

| Metric                         | Best Model           |
| ------------------------------ | -------------------- |
| Fewest total errors            | Random Forest        |
| Fewest Attack -> BENIGN errors | Clipped Weighted CNN |
| Fewest BENIGN -> Attack errors | Random Forest        |

Main observations:

* Random Forest has the fewest total errors and the best overall stability.
* Random Forest also has the fewest BENIGN -> Attack false positives.
* Clipped Weighted CNN has the fewest Attack -> BENIGN false negatives.
* CNN shows clear missed detection for minority attacks such as WebAttack and Bot.
* Clipped Weighted CNN significantly reduces missed attacks, but introduces many false alarms.

This confirms that model selection in IDS should not only depend on accuracy. Different deployment scenarios may require different models:

| Scenario               | Recommended Model    |
| ---------------------- | -------------------- |
| Low false alarm IDS    | Random Forest        |
| High sensitivity IDS   | Clipped Weighted CNN |
| Deep learning baseline | CNN                  |

## Important Result Files

| File                                                                                                  | Description                                |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| `results/model_comparison/binary_model_comparison.csv`                                                | Binary model comparison                    |
| `results/multiclass/model_comparison/multiclass_model_comparison.csv`                                 | Multiclass model comparison                |
| `results/multiclass/deep_learning_weight_experiments/deep_learning_weight_experiments_comparison.csv` | Weighted deep learning comparison          |
| `results/multiclass/error_pattern_comparison/model_error_pattern_comparison.csv`                      | Error pattern comparison                   |
| `results/multiclass/class_error_rate_comparison/class_error_rate_comparison.csv`                      | Per-class error rate comparison            |
| `results/multiclass/error_analysis_summary/day7_error_analysis_summary.md`                            | Auto-generated Day7 error analysis summary |

## How to Run

### 1. Create Virtual Environment

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Prepare Dataset

Place the CICIDS2017 CSV files under:

```txt
data/raw/MachineLearningCSV/MachineLearningCVE/
```

Then build the processed datasets:

```powershell
python scripts/data/build_binary_dataset.py
python scripts/data/build_multiclass_dataset.py
```

### 4. Run Binary Models

```powershell
python scripts/models/train_logistic_regression.py
python scripts/models/train_random_forest.py
python scripts/models/mlp_torch_binary.py
python scripts/models/cnn_torch_binary.py
python scripts/models/compare_binary_models.py
```

### 5. Run Multiclass Models

```powershell
python scripts/models/multiclass/train_multiclass_logistic_regression.py
python scripts/models/multiclass/train_multiclass_random_forest.py
python scripts/models/multiclass/train_multiclass_mlp.py
python scripts/models/multiclass/train_multiclass_cnn.py
python scripts/models/multiclass/compare_multiclass_models.py
```

### 6. Run Class Imbalance Experiments

```powershell
python scripts/models/multiclass/train_multiclass_mlp_weighted.py
python scripts/models/multiclass/train_multiclass_mlp_weighted_clipped.py
python scripts/models/multiclass/compare_mlp_weight_experiments.py

python scripts/models/multiclass/train_multiclass_cnn_weighted.py
python scripts/models/multiclass/train_multiclass_cnn_weighted_clipped.py
python scripts/models/multiclass/compare_cnn_weight_experiments.py

python scripts/models/multiclass/compare_deep_learning_weight_experiments.py
```

### 7. Run Error Pattern Analysis

```powershell
python scripts/analysis/multiclass/analyze_cnn_error_patterns.py
python scripts/analysis/multiclass/analyze_random_forest_error_patterns.py
python scripts/analysis/multiclass/analyze_clipped_weighted_cnn_error_patterns.py
python scripts/analysis/multiclass/compare_error_patterns.py
python scripts/analysis/multiclass/compare_class_error_rates.py
python scripts/analysis/multiclass/generate_error_analysis_summary.py
```

## Documentation

| Document           | Description                                   |
| ------------------ | --------------------------------------------- |
| `docs/Day1.md`     | Dataset preparation and initial understanding |
| `docs/Day2.md`     | Binary dataset construction                   |
| `docs/Day3.md`     | Binary model training                         |
| `docs/Day4.md`     | Multiclass dataset preparation                |
| `docs/Day5.md`     | Multiclass model comparison                   |
| `docs/Day6.md`     | Class imbalance experiments                   |
| `docs/Day7.md`     | Error pattern analysis                        |
| `docs/scripts.md`  | Script index                                  |
| `docs/glossary.md` | Project glossary                              |

## Tech Stack

* Python
* pandas
* NumPy
* scikit-learn
* PyTorch
* matplotlib
* seaborn
* CICIDS2017 dataset

## Current Status

Completed:

* Binary IDS classification
* Multiclass IDS classification
* Traditional ML and deep learning comparison
* Class imbalance optimization
* Error pattern analysis
* False positive / false negative analysis
* Result visualization
* Experiment documentation

In progress / planned:

* README and project structure refinement
* Research paper review
* GitHub project comparison
* Feature importance analysis
* SHAP or permutation importance
* FastAPI inference service
* Dashboard visualization

## Future Work

Planned improvements:

1. Add research paper review notes for IDS class imbalance and explainability.
2. Compare this project with existing open-source IDS projects.
3. Improve Random Forest feature importance analysis.
4. Add SHAP or permutation importance for model interpretability.
5. Build a lightweight FastAPI inference API.
6. Build a dashboard for visualizing metrics, confusion matrices, and error patterns.
7. Add Docker support for easier deployment.
8. Improve README and result presentation for GitHub portfolio use.

## Notes

Large files are intentionally excluded from GitHub:

```txt
data/
models/
.venv/
```

This repository focuses on source code, documentation, experiment results, and reproducible analysis scripts.
