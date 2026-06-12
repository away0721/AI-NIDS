from pathlib import Path
import copy

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\binary_dataset.csv"
)

RESULT_DIR = Path(
    r"D:\Projects\ai-nids\results\mlp_torch"
)

MODEL_PATH = Path(
    r"D:\Projects\ai-nids\models\mlp_torch_binary.pt"
)

SCALER_PATH = Path(
    r"D:\Projects\ai-nids\models\mlp_torch_scaler.pkl"
)

SAMPLE_SIZE = None

BATCH_SIZE = 1024
MAX_EPOCHS = 100
PATIENCE = 5
MIN_DELTA = 1e-4
LEARNING_RATE = 0.001
RANDOM_STATE = 42


class MLPBinaryClassifier(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(64, 1),
        )

    def forward(self, x):
        return self.network(x)


def evaluate_loss(model, data_loader, criterion):
    model.eval()
    total_loss = 0.0

    with torch.no_grad():
        for batch_X, batch_y in data_loader:
            logits = model(batch_X)
            loss = criterion(logits, batch_y)
            total_loss += loss.item()

    return total_loss / len(data_loader)


def main():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("正在读取二分类数据集...")
    df = pd.read_csv(DATA_PATH)

    if SAMPLE_SIZE is not None and SAMPLE_SIZE < len(df):
        print(f"正在采样 {SAMPLE_SIZE} 条数据用于 PyTorch MLP 训练...")

        df_0 = df[df["binary_label"] == 0]
        df_1 = df[df["binary_label"] == 1]

        ratio_0 = len(df_0) / len(df)
        sample_0_size = int(SAMPLE_SIZE * ratio_0)
        sample_1_size = SAMPLE_SIZE - sample_0_size

        sample_0 = df_0.sample(
            n=sample_0_size,
            random_state=RANDOM_STATE,
        )

        sample_1 = df_1.sample(
            n=sample_1_size,
            random_state=RANDOM_STATE,
        )

        df = pd.concat(
            [sample_0, sample_1],
            ignore_index=True,
        )

        print("采样后二分类 Label 分布：")
        print(df["binary_label"].value_counts())
        print(df["binary_label"].value_counts(normalize=True))

    X = df.drop(columns=["binary_label"])
    y = df["binary_label"]

    print("正在划分训练集、验证集和测试集...")

    # 第一次划分：先切出 20% 测试集
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # 第二次划分：从剩下的 80% 中切出 20% 作为验证集
    # 最终比例：
    # train      = 64%
    # validation = 16%
    # test       = 20%
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y_train_val,
    )

    print("数据划分结果：")
    print(f"X_train: {X_train.shape}")
    print(f"X_val:   {X_val.shape}")
    print(f"X_test:  {X_test.shape}")

    print("正在标准化特征...")

    scaler = StandardScaler()

    # 只能用训练集 fit scaler
    X_train_scaled = scaler.fit_transform(X_train)

    # 验证集和测试集只能 transform，不能 fit
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    joblib.dump(scaler, SCALER_PATH)

    print("正在转换为 PyTorch Tensor...")

    X_train_tensor = torch.tensor(
        X_train_scaled,
        dtype=torch.float32,
    )

    X_val_tensor = torch.tensor(
        X_val_scaled,
        dtype=torch.float32,
    )

    X_test_tensor = torch.tensor(
        X_test_scaled,
        dtype=torch.float32,
    )

    y_train_tensor = torch.tensor(
        y_train.values,
        dtype=torch.float32,
    ).view(-1, 1)

    y_val_tensor = torch.tensor(
        y_val.values,
        dtype=torch.float32,
    ).view(-1, 1)

    y_test_tensor = torch.tensor(
        y_test.values,
        dtype=torch.float32,
    ).view(-1, 1)

    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    val_dataset = TensorDataset(X_val_tensor, y_val_tensor)

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    input_dim = X_train.shape[1]
    model = MLPBinaryClassifier(input_dim=input_dim)

    criterion = nn.BCEWithLogitsLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    print("开始训练 PyTorch MLP with Early Stopping...")

    train_losses = []
    val_losses = []

    best_val_loss = float("inf")
    best_epoch = 0
    best_model_state = None
    no_improve_count = 0

    for epoch in range(MAX_EPOCHS):
        model.train()
        total_train_loss = 0.0

        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()

            logits = model(batch_X)
            loss = criterion(logits, batch_y)

            loss.backward()
            optimizer.step()

            total_train_loss += loss.item()

        avg_train_loss = total_train_loss / len(train_loader)
        avg_val_loss = evaluate_loss(model, val_loader, criterion)

        train_losses.append(avg_train_loss)
        val_losses.append(avg_val_loss)

        print(
            f"Epoch {epoch + 1}/{MAX_EPOCHS} "
            f"- Train Loss: {avg_train_loss:.6f} "
            f"- Val Loss: {avg_val_loss:.6f}"
        )

        if avg_val_loss < best_val_loss - MIN_DELTA:
            best_val_loss = avg_val_loss
            best_epoch = epoch + 1
            best_model_state = copy.deepcopy(model.state_dict())
            no_improve_count = 0

            print(
                f"验证集 Loss 改善，保存当前最佳模型。"
                f"Best Val Loss: {best_val_loss:.6f}"
            )
        else:
            no_improve_count += 1

            print(
                f"验证集 Loss 未明显改善。"
                f"Early Stopping 计数：{no_improve_count}/{PATIENCE}"
            )

        if no_improve_count >= PATIENCE:
            print(
                f"\n触发 Early Stopping："
                f"验证集 Loss 连续 {PATIENCE} 轮未明显改善。"
            )
            break

    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    print(f"\n最佳 Epoch：{best_epoch}")
    print(f"最佳 Val Loss：{best_val_loss:.6f}")

    print("正在测试集上评估最佳模型...")

    model.eval()

    with torch.no_grad():
        test_logits = model(X_test_tensor)
        test_probs = torch.sigmoid(test_logits)
        y_pred = (test_probs >= 0.5).int().numpy().flatten()

    y_true = y_test.values

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)

    report = classification_report(
        y_true,
        y_pred,
        target_names=["BENIGN", "ATTACK"],
        digits=4,
    )

    print("\n评估结果：")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    print("\nConfusion Matrix:")
    print(cm)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "input_dim": input_dim,
            "sample_size": SAMPLE_SIZE,
            "max_epochs": MAX_EPOCHS,
            "best_epoch": best_epoch,
            "patience": PATIENCE,
            "min_delta": MIN_DELTA,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
        },
        MODEL_PATH,
    )

    result_text = f"""PyTorch MLP Binary Classification Baseline with Early Stopping

Dataset:
- Data path: {DATA_PATH}
- Used samples: {len(df)}
- Feature count: {input_dim}
- Task: Binary Classification
- Label mapping:
  - BENIGN -> 0
  - ATTACK -> 1

Data Split:
- Train set: {X_train.shape}
- Validation set: {X_val.shape}
- Test set: {X_test.shape}
- random_state: {RANDOM_STATE}
- stratify: y

Preprocessing:
- StandardScaler
- Scaler is fitted only on training set
- Validation set and test set are transformed using the same scaler

Model:
- PyTorch MLP
- Input dimension: {input_dim}
- Hidden layers: 128 -> 64
- Activation: ReLU
- Dropout: 0.3
- Output: 1 logit
- Loss: BCEWithLogitsLoss
- Optimizer: Adam
- Max epochs: {MAX_EPOCHS}
- Best epoch: {best_epoch}
- Patience: {PATIENCE}
- Min delta: {MIN_DELTA}
- Batch size: {BATCH_SIZE}
- Learning rate: {LEARNING_RATE}

Metrics:
- Accuracy:  {accuracy:.4f}
- Precision: {precision:.4f}
- Recall:    {recall:.4f}
- F1 Score:  {f1:.4f}

Confusion Matrix:
{cm}

Classification Report:
{report}
"""

    report_path = RESULT_DIR / "mlp_torch_binary_report.txt"
    metrics_csv_path = RESULT_DIR / "mlp_torch_binary_metrics.csv"
    metrics_png_path = RESULT_DIR / "mlp_torch_binary_metrics.png"
    cm_png_path = RESULT_DIR / "mlp_torch_binary_confusion_matrix.png"
    loss_png_path = RESULT_DIR / "mlp_torch_training_loss.png"

    report_path.write_text(result_text, encoding="utf-8")

    metrics_df = pd.DataFrame(
        [
            {
                "model": "PyTorch MLP",
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "sample_size": len(df),
                "max_epochs": MAX_EPOCHS,
                "best_epoch": best_epoch,
            }
        ]
    )

    metrics_df.to_csv(
        metrics_csv_path,
        index=False,
        encoding="utf-8-sig",
    )

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["BENIGN", "ATTACK"],
    )

    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, colorbar=False)
    plt.title("PyTorch MLP Confusion Matrix")
    plt.tight_layout()
    plt.savefig(cm_png_path, dpi=300)
    plt.close()

    metric_names = ["Accuracy", "Precision", "Recall", "F1 Score"]
    metric_values = [accuracy, precision, recall, f1]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(metric_names, metric_values)
    plt.ylim(0.0, 1.05)
    plt.title("PyTorch MLP Binary Classification Metrics")
    plt.ylabel("Score")

    for bar, value in zip(bars, metric_values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.01,
            f"{value:.4f}",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    plt.savefig(metrics_png_path, dpi=300)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(
        range(1, len(train_losses) + 1),
        train_losses,
        marker="o",
        label="Train Loss",
    )
    plt.plot(
        range(1, len(val_losses) + 1),
        val_losses,
        marker="o",
        label="Validation Loss",
    )
    plt.axvline(
        x=best_epoch,
        linestyle="--",
        label=f"Best Epoch: {best_epoch}",
    )
    plt.title("PyTorch MLP Training and Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(loss_png_path, dpi=300)
    plt.close()

    print(f"\n模型已保存到：{MODEL_PATH}")
    print(f"Scaler 已保存到：{SCALER_PATH}")
    print(f"文本报告已保存到：{report_path}")
    print(f"指标 CSV 已保存到：{metrics_csv_path}")
    print(f"指标图已保存到：{metrics_png_path}")
    print(f"混淆矩阵图已保存到：{cm_png_path}")
    print(f"训练/验证 Loss 图已保存到：{loss_png_path}")


if __name__ == "__main__":
    main()