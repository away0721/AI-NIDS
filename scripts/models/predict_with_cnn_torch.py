from pathlib import Path

import joblib
import pandas as pd
import torch
from torch import nn


MODEL_PATH = Path(
    r"D:\Projects\ai-nids\models\cnn_torch_binary.pt"
)

SCALER_PATH = Path(
    r"D:\Projects\ai-nids\models\cnn_torch_scaler.pkl"
)

DATA_PATH = Path(
    r"D:\Projects\ai-nids\data\processed\binary_dataset.csv"
)

RESULT_PATH = Path(
    r"D:\Projects\ai-nids\results\cnn_torch\sample_predictions.csv"
)


class CNNBinaryClassifier(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv1d(
                in_channels=1,
                out_channels=32,
                kernel_size=3,
                padding=1,
            ),
            nn.ReLU(),
            nn.BatchNorm1d(32),

            nn.Conv1d(
                in_channels=32,
                out_channels=64,
                kernel_size=3,
                padding=1,
            ),
            nn.ReLU(),
            nn.BatchNorm1d(64),

            nn.AdaptiveAvgPool1d(1),
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        x = self.conv(x)
        x = self.classifier(x)
        return x


def main():
    print("正在加载 PyTorch CNN 模型...")

    checkpoint = torch.load(
        MODEL_PATH,
        map_location="cpu",
    )

    input_dim = checkpoint["input_dim"]

    model = CNNBinaryClassifier(input_dim=input_dim)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    print("正在加载 Scaler...")
    scaler = joblib.load(SCALER_PATH)

    print("正在读取二分类数据集...")
    df = pd.read_csv(DATA_PATH)

    benign_samples = df[df["binary_label"] == 0].sample(
        n=5,
        random_state=42,
    )

    attack_samples = df[df["binary_label"] == 1].sample(
        n=5,
        random_state=42,
    )

    sample_df = pd.concat(
        [benign_samples, attack_samples],
        ignore_index=True,
    )

    sample_X = sample_df.drop(columns=["binary_label"])
    sample_y = sample_df["binary_label"]

    print("\n正在标准化样本特征...")
    sample_X_scaled = scaler.transform(sample_X)

    # CNN 输入需要是 [样本数, 通道数, 特征长度]
    # 这里是 [10, 1, 78]
    sample_X_tensor = torch.tensor(
        sample_X_scaled,
        dtype=torch.float32,
    ).unsqueeze(1)

    print("正在预测 10 条 Flow...")

    with torch.no_grad():
        logits = model(sample_X_tensor)
        probs = torch.sigmoid(logits)
        predictions = (probs >= 0.5).int().numpy().flatten()
        probabilities = probs.numpy().flatten()

    result_df = pd.DataFrame({
        "true_label": sample_y.values,
        "predicted_label": predictions,
        "attack_probability": probabilities,
    })

    result_df["true_name"] = result_df["true_label"].map({
        0: "BENIGN",
        1: "ATTACK",
    })

    result_df["predicted_name"] = result_df["predicted_label"].map({
        0: "BENIGN",
        1: "ATTACK",
    })

    result_df["is_correct"] = (
        result_df["true_label"] == result_df["predicted_label"]
    )

    print("\n预测结果：")
    print(result_df)

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(
        RESULT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\n预测结果已保存到：{RESULT_PATH}")


if __name__ == "__main__":
    main()