from pathlib import Path

import joblib
import pandas as pd
import torch
import torch.nn as nn


DATA_PATH = Path(r"D:\Projects\ai-nids\data\processed\multiclass_dataset.csv")

MODEL_PATH = Path(r"D:\Projects\ai-nids\models\multiclass\mlp_torch_multiclass.pt")
SCALER_PATH = Path(r"D:\Projects\ai-nids\models\multiclass\mlp_torch_multiclass_scaler.pkl")
LABEL_ENCODER_PATH = Path(r"D:\Projects\ai-nids\models\multiclass\multiclass_label_encoder.pkl")

RESULT_DIR = Path(r"D:\Projects\ai-nids\results\multiclass\mlp_torch")
OUTPUT_PATH = RESULT_DIR / "sample_predictions.csv"

LABEL_COLUMN = "attack_category"
SAMPLES_PER_CLASS = 5
RANDOM_STATE = 42


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


def main() -> None:
    print("正在加载数据...")
    df = pd.read_csv(DATA_PATH)

    if LABEL_COLUMN not in df.columns:
        raise ValueError(
            f"数据集中没有找到标签列：{LABEL_COLUMN}\n"
            f"当前数据列名为：{df.columns.tolist()}"
        )

    print("正在加载 Scaler 和 LabelEncoder...")
    scaler = joblib.load(SCALER_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"当前预测设备：{device}")

    print("正在加载 MLP 模型...")
    checkpoint = torch.load(MODEL_PATH, map_location=device)

    input_dim = checkpoint["input_dim"]
    num_classes = checkpoint["num_classes"]

    model = MLPClassifier(input_dim=input_dim, num_classes=num_classes).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    feature_columns = [col for col in df.columns if col != LABEL_COLUMN]

    print("正在从每个类别中抽取样本...")

    sample_parts = []

    for class_name, group in df.groupby(LABEL_COLUMN):
        sampled_group = group.sample(
            n=min(SAMPLES_PER_CLASS, len(group)),
            random_state=RANDOM_STATE,
        )
        sample_parts.append(sampled_group)

    sample_df = pd.concat(sample_parts, axis=0).reset_index(drop=True)

    if LABEL_COLUMN not in sample_df.columns:
        raise ValueError(
            f"抽样后的数据中没有找到标签列：{LABEL_COLUMN}\n"
            f"抽样后数据列名为：{sample_df.columns.tolist()}"
        )

    X_sample = sample_df[feature_columns]
    y_true_text = sample_df[LABEL_COLUMN]

    print("正在使用训练阶段保存的 Scaler 标准化样本...")
    X_sample_scaled = scaler.transform(X_sample)

    X_sample_tensor = torch.tensor(
        X_sample_scaled,
        dtype=torch.float32,
    ).to(device)

    print("正在预测...")

    with torch.no_grad():
        logits = model(X_sample_tensor)
        probabilities = torch.softmax(logits, dim=1)
        confidence_tensor, y_pred_encoded_tensor = torch.max(probabilities, dim=1)

    y_pred_encoded = y_pred_encoded_tensor.cpu().numpy()
    confidence = confidence_tensor.cpu().numpy()

    y_pred_text = label_encoder.inverse_transform(y_pred_encoded)

    result_df = pd.DataFrame(
        {
            "true_label": y_true_text.values,
            "predicted_label": y_pred_text,
            "confidence": confidence,
            "is_correct": y_true_text.values == y_pred_text,
        }
    )

    print("\n预测结果：")
    print(result_df)

    print("\n预测正确数量：")
    print(result_df["is_correct"].value_counts())

    print("\n按类别统计预测结果：")
    class_summary = (
        result_df.groupby("true_label")["is_correct"]
        .agg(["count", "sum"])
        .rename(columns={"count": "total", "sum": "correct"})
    )
    class_summary["accuracy"] = class_summary["correct"] / class_summary["total"]
    print(class_summary)

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n样本预测结果已保存到：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()