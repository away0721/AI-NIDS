# AI-NIDS

AI-NIDS is a network intrusion detection experiment project based on the CICIDS2017 dataset.

The current stage focuses on **flow-based binary intrusion detection**, where each network flow is classified as either normal traffic or attack traffic.

```txt
BENIGN -> 0
ATTACK -> 1
```

This project is built as a step-by-step machine learning and deep learning practice project. It covers data exploration, dataset cleaning, feature preprocessing, model training, model evaluation, prediction, result visualization, and experiment documentation.

---

## Current Progress

The project has completed the full binary classification baseline workflow:

* CICIDS2017 dataset exploration
* Binary label construction
* Data cleaning and preprocessing
* Train / validation / test split
* Traditional machine learning baselines
* PyTorch deep learning baselines
* Early Stopping for deep learning models
* Model evaluation and comparison
* Result visualization
* Project documentation

Implemented models:

| Model               | Type           | Description                    |
| ------------------- | -------------- | ------------------------------ |
| Logistic Regression | Traditional ML | Linear baseline model          |
| Random Forest       | Traditional ML | Strong tree-based baseline     |
| PyTorch MLP         | Deep Learning  | Fully connected neural network |
| PyTorch CNN         | Deep Learning  | 1D CNN over flow features      |

---

## Dataset

This project uses the **CICIDS2017 MachineLearningCSV** dataset.

Each row represents a network flow instead of a single packet. The raw dataset contains multiple traffic categories, including normal traffic and different attack types.

In the current binary classification stage:

```txt
BENIGN traffic -> BENIGN
All attack traffic -> ATTACK
```

After cleaning, the processed binary dataset contains:

```txt
Total samples: 2,827,761
Features: 78
Label column: binary_label
```

Binary label distribution:

```txt
BENIGN: 2,271,205
ATTACK:   556,556
```

The processed dataset is saved as:

```txt
data/processed/binary_dataset.csv
```

Large data files are ignored by Git and are not uploaded to the repository.

---

## Model Results

Current binary classification results:

| Model               | Accuracy | Precision | Recall | F1 Score |
| ------------------- | -------: | --------: | -----: | -------: |
| Random Forest       |   0.9991 |    0.9967 | 0.9986 |   0.9976 |
| Logistic Regression |   0.9162 |    0.7129 | 0.9614 |   0.8187 |
| PyTorch MLP         |   0.9908 |    0.9921 | 0.9607 |   0.9762 |
| PyTorch CNN         |   0.9702 |    0.9246 | 0.9239 |   0.9243 |

At the current stage, Random Forest performs best on the binary classification task. PyTorch MLP is the strongest deep learning baseline. Logistic Regression is used as a simple linear baseline, while CNN is used as an experimental 1D convolutional model over flow features.

---

## Training Strategy

For traditional machine learning models:

* Logistic Regression uses `StandardScaler`.
* Random Forest directly uses the original numerical features.
* Models are evaluated on the test set after training.

For PyTorch deep learning models:

* The dataset is split into train / validation / test sets.
* `StandardScaler` is fitted only on the training set.
* Validation loss is monitored after every epoch.
* Early Stopping is used to avoid unnecessary training and reduce overfitting risk.

Early Stopping settings:

```python
MAX_EPOCHS = 100
PATIENCE = 5
MIN_DELTA = 1e-4
```

The deep learning workflow is:

```txt
Train set:
  Used for parameter learning.

Validation set:
  Used for monitoring validation loss and early stopping.

Test set:
  Used only once for final evaluation.
```

---

## Project Structure

```txt
AI-NIDS/
├── .venv/                          # Python virtual environment, ignored by Git
│
├── data/
│   ├── raw/
│   │   └── MachineLearningCSV/
│   │       └── MachineLearningCVE/  # Original CICIDS2017 CSV files, ignored by Git
│   └── processed/
│       └── binary_dataset.csv       # Cleaned binary classification dataset, ignored by Git
│
├── docs/
│   ├── Day1.md
│   ├── Day2.md
│   ├── Day3.md
│   ├── Day4.md
│   ├── glossary.md
│   └── scripts.md
│
├── models/                         # Saved model files, ignored by Git
│   ├── random_forest_binary.pkl
│   ├── logistic_regression_binary.pkl
│   ├── mlp_torch_binary.pt
│   ├── mlp_torch_scaler.pkl
│   ├── cnn_torch_binary.pt
│   └── cnn_torch_scaler.pkl
│
├── results/
│   ├── random_forest/
│   ├── logistic_regression/
│   ├── mlp_torch/
│   ├── cnn_torch/
│   └── model_comparison/
│
├── scripts/
│   ├── eda/
│   │   ├── eda.py
│   │   ├── dataset_overview.py
│   │   ├── label_overview.py
│   │   └── binary_label_overview.py
│   │
│   ├── data/
│   │   ├── build_binary_dataset.py
│   │   ├── check_binary_dataset.py
│   │   ├── prepare_xy_check.py
│   │   └── train_test_split_check.py
│   │
│   └── models/
│       ├── train_random_forest.py
│       ├── predict_with_random_forest.py
│       ├── train_logistic_regression.py
│       ├── mlp_torch_binary.py
│       ├── predict_with_mlp_torch.py
│       ├── cnn_torch_binary.py
│       ├── predict_with_cnn_torch.py
│       └── compare_binary_models.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## How to Run

### 1. Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Build binary dataset

```powershell
python scripts\data\build_binary_dataset.py
```

### 4. Train traditional machine learning models

```powershell
python scripts\models\train_random_forest.py
python scripts\models\train_logistic_regression.py
```

### 5. Train PyTorch deep learning models

```powershell
python scripts\models\mlp_torch_binary.py
python scripts\models\cnn_torch_binary.py
```

### 6. Compare all binary models

```powershell
python scripts\models\compare_binary_models.py
```

The comparison results will be saved to:

```txt
results/model_comparison/
```

---

## Output Results

The project generates:

```txt
classification reports
metrics CSV files
metrics bar charts
confusion matrix images
training / validation loss curves
feature importance reports
sample prediction results
model comparison charts
```

Example result directories:

```txt
results/random_forest/
results/logistic_regression/
results/mlp_torch/
results/cnn_torch/
results/model_comparison/
```

---

## Notes

Large files are ignored by Git, including:

```txt
.venv/
data/raw/
data/processed/
models/
```

This keeps the repository lightweight and suitable for GitHub.

---

## Next Steps

Planned next steps:

* Improve README and experiment documentation
* Add multiclass intrusion detection
* Analyze class imbalance
* Add more detailed false positive and false negative analysis
* Explore CNN-LSTM or sequence-based modeling
* Improve model tuning and validation strategy
* Prepare the project for resume and research presentation
