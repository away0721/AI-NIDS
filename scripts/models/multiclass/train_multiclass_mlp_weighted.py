from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from torch.utils.data import DataLoader, TensorDataset


DATA_PATH = Path(r"D:\Projects\ai-nids\data\processed\multiclass_dataset.csv")

RESULT_DIR = Path(r"D:\Projects\ai-nids\results\multiclass\mlp_torch_weighted")
MODEL_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\mlp_torch_weighted_multiclass.pt"
)
SCALER_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\mlp_torch_weighted_multiclass_scaler.pkl"
)
LABEL_ENCODER_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\mlp_torch_weighted_label_encoder.pkl"
)

REPORT_PATH = RESULT_DIR / "mlp_torch_weighted_multiclass_report.txt"
METRICS_CSV_PATH = RESULT_DIR / "mlp_torch_weighted_multiclass_metrics.csv"
METRICS_FIG_PATH = RESULT_DIR / "mlp_torch_weighted_multiclass_metrics.png"
CONFUSION_MATRIX_FIG_PATH = RESULT_DIR / "mlp_torch_weighted_multiclass_confusion_matrix.png"
TRAINING_HISTORY_CSV_PATH = RESULT_DIR / "mlp_torch_weighted_multiclass_training_history.csv"
TRAINING_HISTORY_FIG_PATH = RESULT_DIR / "mlp_torch_weighted_multiclass_training_history.png"

LABEL_COLUMN = "attack_category"

RANDOM_STATE = 42
TEST_SIZE = 0.2
VAL_SIZE = 0.2

BATCH_SIZE = 1024
MAX_EPOCHS = 100
PATIENCE = 5
MIN_DELTA = 1e-4
LEARNING_RATE = 1e-3


class MLPClassifier(nn.Module):
    def __init__(self, input_dim: int, num_classes: int):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        return self.net(x)


def plot_metrics(metrics: dict) -> None:
    names = list(metrics.keys())
    values = list(metrics.values())

    plt.figure(figsize=(8, 5))
    plt.bar(names, values)
    plt.ylim(0, 1)
    plt.title("Weighted PyTorch MLP Multiclass Metrics")
    plt.ylabel("Score")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(METRICS_FIG_PATH)
    plt.close()


def plot_confusion_matrix(cm, class_names) -> None:
    plt.figure(figsize=(10, 8))
    plt.imshow(cm)
    plt.title("Weighted PyTorch MLP Multiclass Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.colorbar()

    tick_positions = range(len(class_names))
    plt.xticks(tick_positions, class_names, rotation=45, ha="right")
    plt.yticks(tick_positions, class_names)

    for i in range(len(class_names)):
        for j in range(len(class_names)):
            value = cm[i, j]
            if value > 0:
                plt.text(j, i, str(value), ha="center", va="center", fontsize=7)

    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_FIG_PATH)
    plt.close()


def plot_training_history(history_df: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 5))
    plt.plot(history_df["epoch"], history_df["train_loss"], label="Train Loss")
    plt.plot(history_df["epoch"], history_df["val_loss"], label="Validation Loss")
    plt.title("Weighted PyTorch MLP Multiclass Training History")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(TRAINING_HISTORY_FIG_PATH)
    plt.close()


def train_one_epoch(model, dataloader, criterion, optimizer, device) -> float:
    model.train()
    total_loss = 0.0
    total_samples = 0

    for batch_x, batch_y in dataloader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        optimizer.zero_grad()

        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)

        loss.backward()
        optimizer.step()

        batch_size = batch_x.size(0)
        total_loss += loss.item() * batch_size
        total_samples += batch_size

    return total_loss / total_samples


def evaluate_loss(model, dataloader, criterion, device) -> float:
    model.eval()
    total_loss = 0.0
    total_samples = 0

    with torch.no_grad():
        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)

            batch_size = batch_x.size(0)
            total_loss += loss.item() * batch_size
            total_samples += batch_size

    return total_loss / total_samples


def predict(model, dataloader, device):
    model.eval()

    all_preds = []
    all_targets = []

    with torch.no_grad():
        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)

            outputs = model(batch_x)
            preds = torch.argmax(outputs, dim=1)

            all_preds.append(preds.cpu())
            all_targets.append(batch_y)

    y_pred = torch.cat(all_preds).numpy()
    y_true = torch.cat(all_targets).numpy()

    return y_true, y_pred


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("正在加载多分类数据集...")
    df = pd.read_csv(DATA_PATH)

    if LABEL_COLUMN not in df.columns:
        raise ValueError(f"数据集中没有找到标签列：{LABEL_COLUMN}")

    print(f"数据规模：{df.shape}")

    X = df.drop(columns=[LABEL_COLUMN])
    y_text = df[LABEL_COLUMN]

    print("正在编码多分类标签...")
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_text)
    class_names = label_encoder.classes_
    num_classes = len(class_names)

    print("类别映射：")
    for index, class_name in enumerate(class_names):
        print(f"{index}: {class_name}")

    print("\n正在划分训练集、验证集和测试集...")
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=VAL_SIZE,
        random_state=RANDOM_STATE,
        stratify=y_train_val,
    )

    print(f"X_train: {X_train.shape}")
    print(f"X_val:   {X_val.shape}")
    print(f"X_test:  {X_test.shape}")

    print("\n正在标准化特征...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    print("正在构建 PyTorch Dataset 和 DataLoader...")
    X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.long)

    X_val_tensor = torch.tensor(X_val_scaled, dtype=torch.float32)
    y_val_tensor = torch.tensor(y_val, dtype=torch.long)

    X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test, dtype=torch.long)

    train_loader = DataLoader(
        TensorDataset(X_train_tensor, y_train_tensor),
        batch_size=BATCH_SIZE,
        shuffle=True,
    )

    val_loader = DataLoader(
        TensorDataset(X_val_tensor, y_val_tensor),
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    test_loader = DataLoader(
        TensorDataset(X_test_tensor, y_test_tensor),
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n当前训练设备：{device}")

    print("\n正在计算类别权重...")
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.arange(num_classes),
        y=y_train,
    )

    print("类别权重：")
    for class_name, weight in zip(class_names, class_weights):
        print(f"{class_name}: {weight:.4f}")

    class_weights_tensor = torch.tensor(
        class_weights,
        dtype=torch.float32,
    ).to(device)

    input_dim = X_train.shape[1]

    model = MLPClassifier(input_dim=input_dim, num_classes=num_classes).to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    print("\n开始训练 Weighted 多分类 MLP...")

    best_val_loss = float("inf")
    best_epoch = 0
    patience_counter = 0
    best_model_state = None

    history = []

    for epoch in range(1, MAX_EPOCHS + 1):
        train_loss = train_one_epoch(
            model=model,
            dataloader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
        )

        val_loss = evaluate_loss(
            model=model,
            dataloader=val_loader,
            criterion=criterion,
            device=device,
        )

        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
            }
        )

        print(
            f"Epoch {epoch:03d} | "
            f"Train Loss: {train_loss:.6f} | "
            f"Val Loss: {val_loss:.6f}"
        )

        if val_loss < best_val_loss - MIN_DELTA:
            best_val_loss = val_loss
            best_epoch = epoch
            patience_counter = 0
            best_model_state = {
                key: value.cpu().clone()
                for key, value in model.state_dict().items()
            }
        else:
            patience_counter += 1

        if patience_counter >= PATIENCE:
            print(f"\nEarly Stopping 触发，停止于 Epoch {epoch}")
            break

    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    print(f"\n最佳 Epoch：{best_epoch}")
    print(f"最佳 Validation Loss：{best_val_loss:.6f}")

    history_df = pd.DataFrame(history)
    history_df.to_csv(TRAINING_HISTORY_CSV_PATH, index=False, encoding="utf-8-sig")
    plot_training_history(history_df)

    print("\n正在测试集上预测...")
    y_true, y_pred = predict(
        model=model,
        dataloader=test_loader,
        device=device,
    )

    accuracy = accuracy_score(y_true, y_pred)

    macro_precision = precision_score(
        y_true, y_pred, average="macro", zero_division=0
    )
    macro_recall = recall_score(
        y_true, y_pred, average="macro", zero_division=0
    )
    macro_f1 = f1_score(
        y_true, y_pred, average="macro", zero_division=0
    )

    weighted_precision = precision_score(
        y_true, y_pred, average="weighted", zero_division=0
    )
    weighted_recall = recall_score(
        y_true, y_pred, average="weighted", zero_division=0
    )
    weighted_f1 = f1_score(
        y_true, y_pred, average="weighted", zero_division=0
    )

    metrics = {
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1_score": macro_f1,
        "weighted_precision": weighted_precision,
        "weighted_recall": weighted_recall,
        "weighted_f1_score": weighted_f1,
    }

    print("\nWeighted 多分类 MLP 评估结果：")
    print(f"Accuracy:           {accuracy:.4f}")
    print(f"Macro Precision:    {macro_precision:.4f}")
    print(f"Macro Recall:       {macro_recall:.4f}")
    print(f"Macro F1 Score:     {macro_f1:.4f}")
    print(f"Weighted Precision: {weighted_precision:.4f}")
    print(f"Weighted Recall:    {weighted_recall:.4f}")
    print(f"Weighted F1 Score:  {weighted_f1:.4f}")

    report = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        digits=4,
        zero_division=0,
    )

    cm = confusion_matrix(y_true, y_pred)

    print("\nClassification Report:")
    print(report)

    print("\nConfusion Matrix:")
    print(cm)

    print("\n正在保存模型和结果...")

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "input_dim": input_dim,
            "num_classes": num_classes,
            "class_names": class_names.tolist(),
            "class_weights": class_weights.tolist(),
        },
        MODEL_PATH,
    )

    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)

    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        file.write("Weighted PyTorch MLP Multiclass Classification Report\n")
        file.write("=" * 60 + "\n\n")
        file.write(f"Best Epoch: {best_epoch}\n")
        file.write(f"Best Validation Loss: {best_val_loss:.6f}\n\n")

        file.write("Class Weights:\n")
        for class_name, weight in zip(class_names, class_weights):
            file.write(f"{class_name}: {weight:.6f}\n")

        file.write("\nMetrics:\n")
        for key, value in metrics.items():
            file.write(f"{key}: {value:.6f}\n")

        file.write("\nClassification Report:\n")
        file.write(report)

        file.write("\nConfusion Matrix:\n")
        file.write(str(cm))

    pd.DataFrame([metrics]).to_csv(
        METRICS_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    plot_metrics(metrics)
    plot_confusion_matrix(cm, class_names)

    print(f"模型已保存到：{MODEL_PATH}")
    print(f"Scaler 已保存到：{SCALER_PATH}")
    print(f"LabelEncoder 已保存到：{LABEL_ENCODER_PATH}")
    print(f"文本报告已保存到：{REPORT_PATH}")
    print(f"指标 CSV 已保存到：{METRICS_CSV_PATH}")
    print(f"指标图已保存到：{METRICS_FIG_PATH}")
    print(f"训练历史 CSV 已保存到：{TRAINING_HISTORY_CSV_PATH}")
    print(f"训练历史图已保存到：{TRAINING_HISTORY_FIG_PATH}")
    print(f"混淆矩阵图已保存到：{CONFUSION_MATRIX_FIG_PATH}")


if __name__ == "__main__":
    main()