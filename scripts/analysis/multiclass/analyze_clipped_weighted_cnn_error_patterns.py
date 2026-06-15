from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from torch.utils.data import DataLoader, TensorDataset


DATA_PATH = Path(r"D:\Projects\ai-nids\data\processed\multiclass_dataset.csv")

MODEL_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\cnn_torch_weighted_clipped_multiclass.pt"
)
SCALER_PATH = Path(
    r"D:\Projects\ai-nids\models\multiclass\cnn_torch_weighted_clipped_multiclass_scaler.pkl"
)

RESULT_DIR = Path(
    r"D:\Projects\ai-nids\results\multiclass\clipped_weighted_cnn_error_patterns"
)

ERROR_DETAIL_CSV_PATH = RESULT_DIR / "clipped_weighted_cnn_error_details.csv"
ERROR_PATTERN_CSV_PATH = RESULT_DIR / "clipped_weighted_cnn_error_pattern_summary.csv"
ERROR_PATTERN_FIG_PATH = RESULT_DIR / "clipped_weighted_cnn_top_error_patterns.png"
ATTACK_TO_BENIGN_CSV_PATH = (
    RESULT_DIR / "clipped_weighted_cnn_attack_to_benign_errors.csv"
)
BENIGN_TO_ATTACK_CSV_PATH = (
    RESULT_DIR / "clipped_weighted_cnn_benign_to_attack_errors.csv"
)

LABEL_COLUMN = "attack_category"

RANDOM_STATE = 42
TEST_SIZE = 0.2
VAL_SIZE = 0.2
BATCH_SIZE = 1024


class CNNClassifier(nn.Module):
    def __init__(self, input_dim: int, num_classes: int):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
        )

        conv_output_dim = 64 * (input_dim // 4)

        self.classifier = nn.Sequential(
            nn.Linear(conv_output_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, start_dim=1)
        return self.classifier(x)


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


def plot_top_error_patterns(error_pattern_df: pd.DataFrame) -> None:
    top_df = error_pattern_df.head(15).copy()

    labels = (
        top_df["true_label"].astype(str)
        + " -> "
        + top_df["predicted_label"].astype(str)
    )

    plt.figure(figsize=(12, 7))
    plt.barh(labels[::-1], top_df["count"][::-1])
    plt.title("Top Clipped Weighted CNN Error Patterns")
    plt.xlabel("Error Count")
    plt.ylabel("True Label -> Predicted Label")
    plt.tight_layout()
    plt.savefig(ERROR_PATTERN_FIG_PATH)
    plt.close()


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    print("正在加载多分类数据集...")
    df = pd.read_csv(DATA_PATH)

    if LABEL_COLUMN not in df.columns:
        raise ValueError(f"数据集中没有找到标签列：{LABEL_COLUMN}")

    print(f"数据规模：{df.shape}")

    X = df.drop(columns=[LABEL_COLUMN])
    y_text = df[LABEL_COLUMN]

    print("正在编码标签...")
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

    # 保持和训练脚本一致：先划分 train_val/test，再从 train_val 中划分 val。
    # 本脚本只使用 test set。
    _, _, _, _ = train_test_split(
        X_train_val,
        y_train_val,
        test_size=VAL_SIZE,
        random_state=RANDOM_STATE,
        stratify=y_train_val,
    )

    print(f"X_test: {X_test.shape}")

    print("\n正在加载 scaler 和 Clipped Weighted CNN 模型...")
    scaler: StandardScaler = joblib.load(SCALER_PATH)

    checkpoint = torch.load(MODEL_PATH, map_location="cpu")

    input_dim = checkpoint.get("input_dim", X_test.shape[1])
    checkpoint_num_classes = checkpoint.get("num_classes", num_classes)

    model = CNNClassifier(
        input_dim=input_dim,
        num_classes=checkpoint_num_classes,
    )

    model.load_state_dict(checkpoint["model_state_dict"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    print(f"当前预测设备：{device}")

    print("\n正在标准化测试集特征...")
    X_test_scaled = scaler.transform(X_test)

    X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32).unsqueeze(1)
    y_test_tensor = torch.tensor(y_test, dtype=torch.long)

    test_loader = DataLoader(
        TensorDataset(X_test_tensor, y_test_tensor),
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    print("\n正在预测测试集...")
    y_true, y_pred = predict(
        model=model,
        dataloader=test_loader,
        device=device,
    )

    print("\n正在统计错误样本...")
    result_df = pd.DataFrame(
        {
            "true_label_id": y_true,
            "predicted_label_id": y_pred,
        }
    )

    result_df["true_label"] = result_df["true_label_id"].apply(
        lambda index: class_names[index]
    )

    result_df["predicted_label"] = result_df["predicted_label_id"].apply(
        lambda index: class_names[index]
    )

    result_df["is_correct"] = (
        result_df["true_label_id"] == result_df["predicted_label_id"]
    )

    error_df = result_df[result_df["is_correct"] == False].copy()

    error_df["error_type"] = (
        error_df["true_label"].astype(str)
        + " -> "
        + error_df["predicted_label"].astype(str)
    )

    error_pattern_df = (
        error_df.groupby(["true_label", "predicted_label", "error_type"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    total_samples = len(result_df)
    total_errors = len(error_df)
    error_rate = total_errors / total_samples

    print(f"测试集样本数：{total_samples}")
    print(f"错误样本数：{total_errors}")
    print(f"错误率：{error_rate:.4f}")

    print("\nTop 15 错误模式：")
    print(error_pattern_df.head(15))

    print("\n正在统计 Attack -> BENIGN 漏报...")
    attack_to_benign_df = error_pattern_df[
        (error_pattern_df["true_label"] != "BENIGN")
        & (error_pattern_df["predicted_label"] == "BENIGN")
    ].copy()

    print(attack_to_benign_df)

    print("\n正在统计 BENIGN -> Attack 误报...")
    benign_to_attack_df = error_pattern_df[
        (error_pattern_df["true_label"] == "BENIGN")
        & (error_pattern_df["predicted_label"] != "BENIGN")
    ].copy()

    print(benign_to_attack_df)

    print("\n正在保存结果...")

    error_df.to_csv(
        ERROR_DETAIL_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    error_pattern_df.to_csv(
        ERROR_PATTERN_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    attack_to_benign_df.to_csv(
        ATTACK_TO_BENIGN_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    benign_to_attack_df.to_csv(
        BENIGN_TO_ATTACK_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    plot_top_error_patterns(error_pattern_df)

    print(f"\n错误样本明细已保存到：{ERROR_DETAIL_CSV_PATH}")
    print(f"错误模式汇总已保存到：{ERROR_PATTERN_CSV_PATH}")
    print(f"Top 错误模式图已保存到：{ERROR_PATTERN_FIG_PATH}")
    print(f"Attack -> BENIGN 漏报统计已保存到：{ATTACK_TO_BENIGN_CSV_PATH}")
    print(f"BENIGN -> Attack 误报统计已保存到：{BENIGN_TO_ATTACK_CSV_PATH}")


if __name__ == "__main__":
    main()