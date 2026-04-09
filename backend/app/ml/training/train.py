import argparse
import logging
import math
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from app.ml.fusion import FusionMLP
from app.ml.training.dataset import DeepfakeFeatureDataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def train(data_dir: str, epochs: int, batch_size: int, lr: float, model_out: str):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    # 1. Load Dataset
    logger.info(f"Loading features from {data_dir}...")
    try:
        full_dataset = DeepfakeFeatureDataset(data_dir)
    except FileNotFoundError as e:
        logger.error(e)
        return
        
    total_size = len(full_dataset)
    train_size = int(0.8 * total_size)
    val_size = total_size - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, pin_memory=True)
    
    logger.info(f"Dataset split: {train_size} train, {val_size} validation")
    
    # 2. Initialize Model, Loss, Optimizer
    model = FusionMLP().to(device)
    criterion = nn.BCELoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    
    best_val_loss = float('inf')
    
    # 3. Training Loop
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        train_correct = 0
        
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch}/{epochs} [Train]")
        for features, labels in progress_bar:
            features, labels = features.to(device), labels.to(device).float()
            
            optimizer.zero_grad()
            
            # The original forward method expects visual_feat and audio_feat separately 
            # OR we can modify fusion layer or dataset. Wait, dataset returns a fused 2816 tensor.
            # FusionMLP forward normally takes (visual, audio), 
            # Let's adjust inputs by splitting the 2816 tensor or modifying the training loop.
            visual_feat = features[:, :2048]
            audio_feat = features[:, 2048:]
            
            # Fusion MLP forward takes 1D, wait we should use vectorized operations
            # Standard FusionMLP in TrustChain expects 1D per API request.
            # Let's vectorize it for training.
            preds = []
            for i in range(features.size(0)):
                pred = model(visual_feat[i], audio_feat[i])
                preds.append(pred)
            preds = torch.stack(preds)
            
            loss = criterion(preds, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * features.size(0)
            predictions = (preds >= 0.5).float()
            train_correct += (predictions == labels).sum().item()
            
            progress_bar.set_postfix({'loss': f"{loss.item():.4f}"})
            
        train_loss /= train_size
        train_acc = train_correct / train_size
        
        # 4. Validation Loop
        model.eval()
        val_loss = 0.0
        val_correct = 0
        with torch.no_grad():
            for features, labels in val_loader:
                features, labels = features.to(device), labels.to(device).float()
                
                visual_feat = features[:, :2048]
                audio_feat = features[:, 2048:]
                
                preds = []
                for i in range(features.size(0)):
                    pred = model(visual_feat[i], audio_feat[i])
                    preds.append(pred)
                preds = torch.stack(preds)
                
                loss = criterion(preds, labels)
                val_loss += loss.item() * features.size(0)
                predictions = (preds >= 0.5).float()
                val_correct += (predictions == labels).sum().item()
                
        val_loss /= val_size
        val_acc = val_correct / val_size
        
        logger.info(f"Epoch {epoch}: Train Loss={train_loss:.4f}, Acc={train_acc:.4f} | Val Loss={val_loss:.4f}, Acc={val_acc:.4f}")
        
        # 5. Checkpoint
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            logger.info(f"Validation loss improved. Saving model to {model_out}...")
            torch.save(model.state_dict(), model_out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train FusionMLP Layer")
    parser.add_argument("--data-dir", type=str, required=True, help="Path to pre-extracted .pt features")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--model-out", type=str, default="fusion_weights.pth", help="Path to save best weights")
    args = parser.parse_args()
    
    train(args.data_dir, args.epochs, args.batch_size, args.lr, args.model_out)
