import os
from pathlib import Path
from typing import Tuple, List

import torch
from torch.utils.data import Dataset

class DeepfakeFeatureDataset(Dataset):
    """
    Dataset for loading pre-extracted 2816-dim visual/audio features.
    
    Expects a directory populated with `.pt` files where each file contains:
    {"features": Tensor of shape (2816,), "label": 0 for Real, 1 for Fake}
    """
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.file_list: List[Path] = list(self.data_dir.glob("*.pt"))
        if not self.file_list:
            raise FileNotFoundError(f"No .pt files found in {self.data_dir}")
            
    def __len__(self) -> int:
        return len(self.file_list)
        
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        file_path = self.file_list[idx]
        data = torch.load(file_path, weights_only=True)
        # Assuming features are 1D (2816,) and label is a scalar/1D
        features = data["features"]
        label = data["label"]
        return features, label
