"""
AGRI SMART — CNN Architecture for PlantVillage Disease Classification
File: backend/app/crop_ai/model.py
"""

import torch
import torch.nn as nn

class AgriLeafCNN(nn.Module):
    """
    Compact 4-stage convolutional neural network designed specifically
    for agricultural leaf disease classification on CPU.
    Trained on 15 classes from PlantVillage.
    """
    def __init__(self, num_classes=15):
        super().__init__()
        self.features = nn.Sequential(
            # Stage 1: 224x224 -> 112x112
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            # Stage 2: 112x112 -> 56x56
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            # Stage 3: 56x56 -> 28x28
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            # Stage 4: 28x28 -> 7x7
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((7, 7)),
        )

        self.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(256 * 7 * 7, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
