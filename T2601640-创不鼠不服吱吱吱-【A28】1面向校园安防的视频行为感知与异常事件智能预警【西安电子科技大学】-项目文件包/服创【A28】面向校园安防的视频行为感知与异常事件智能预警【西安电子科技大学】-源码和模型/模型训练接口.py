import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


class PoseSequenceDataset(Dataset):
    def __init__(self, sequences, labels):
        self.sequences = torch.tensor(sequences, dtype=torch.float32)  # [N, 10, 34]
        self.labels = torch.tensor(labels, dtype=torch.long)           # [N]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]


def train_one_epoch(model, dataloader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for x, y in dataloader:
        x = x.to(device)   # [B, 10, 34]
        y = y.to(device)   # [B]

        optimizer.zero_grad()
        logits = model(x)  # [B, 11]
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * x.size(0)
        preds = torch.argmax(logits, dim=1)
        total_correct += (preds == y).sum().item()
        total_samples += x.size(0)

    return total_loss / total_samples, total_correct / total_samples


@torch.no_grad()
def validate_one_epoch(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for x, y in dataloader:
        x = x.to(device)
        y = y.to(device)

        logits = model(x)
        loss = criterion(logits, y)

        total_loss += loss.item() * x.size(0)
        preds = torch.argmax(logits, dim=1)
        total_correct += (preds == y).sum().item()
        total_samples += x.size(0)

    return total_loss / total_samples, total_correct / total_samples


def train_model(
    train_sequences,
    train_labels,
    val_sequences,
    val_labels,
    save_path="best_model.pth",
    batch_size=32,
    epochs=50,
    lr=1e-3,
    weight_decay=1e-4,
    device=None
):
    """
    训练接口
    参数:
        train_sequences: 训练特征, shape [N, 10, 34]
        train_labels:    训练标签, shape [N]
        val_sequences:   验证特征, shape [M, 10, 34]
        val_labels:      验证标签, shape [M]
        save_path:       最优模型保存路径
        batch_size:      批大小
        epochs:          训练轮数
        lr:              学习率
        weight_decay:    权重衰减
        device:          cuda / cpu
    返回:
        model, best_val_acc
    """
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    train_dataset = PoseSequenceDataset(train_sequences, train_labels)
    val_dataset = PoseSequenceDataset(val_sequences, val_labels)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=False)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, drop_last=False)

    model = PoseLSTMWithAttentionClassifier(
        input_dim=34,
        hidden_dim=128,
        num_layers=2,
        num_heads=4,
        num_classes=11,
        dropout=0.2
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    best_val_acc = 0.0

    for epoch in range(epochs):
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc = validate_one_epoch(model, val_loader, criterion, device)

        print(
            f"Epoch [{epoch+1}/{epochs}] | "
            f"train_loss={train_loss:.4f}, train_acc={train_acc:.4f} | "
            f"val_loss={val_loss:.4f}, val_acc={val_acc:.4f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), save_path)
            print(f"save best model -> {save_path}")

    return model, best_val_acc