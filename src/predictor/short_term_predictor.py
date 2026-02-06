"""
Short-term microstructure predictor
Predicts next-period signed return or adverse selection probability
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


class MicrostructurePredictor(nn.Module):
    """
    Neural network predictor for short-term returns
    """
    
    def __init__(self, input_dim: int = 12, hidden_dims: list = [64, 32], output_dim: int = 1):
        super().__init__()
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.1))
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, output_dim))
        self.network = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class PredictorWrapper:
    """
    Wrapper for predictor model (NN or sklearn)
    """
    
    def __init__(self, model_type: str = "nn", input_dim: int = 12):
        self.model_type = model_type
        self.input_dim = input_dim
        self.scaler = StandardScaler()
        
        if model_type == "nn":
            self.model = MicrostructurePredictor(input_dim=input_dim)
        else:
            self.model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the predictor"""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        if self.model_type == "nn":
            # Convert to tensors
            X_tensor = torch.FloatTensor(X_scaled)
            y_tensor = torch.FloatTensor(y).reshape(-1, 1)
            
            # Training loop
            optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
            criterion = nn.MSELoss()
            
            self.model.train()
            for epoch in range(100):
                optimizer.zero_grad()
                pred = self.model(X_tensor)
                loss = criterion(pred, y_tensor)
                loss.backward()
                optimizer.step()
        else:
            self.model.fit(X_scaled, y)
        
        self.is_trained = True
    
    def predict(self, features: np.ndarray) -> float:
        """Predict short-term return"""
        if not self.is_trained:
            return 0.0
        
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        features_scaled = self.scaler.transform(features)
        
        if self.model_type == "nn":
            self.model.eval()
            with torch.no_grad():
                pred = self.model(torch.FloatTensor(features_scaled))
                return pred.item()
        else:
            return self.model.predict(features_scaled)[0]
    
    def predict_batch(self, features: np.ndarray) -> np.ndarray:
        """Predict for batch of features"""
        if not self.is_trained:
            return np.zeros(len(features))
        
        features_scaled = self.scaler.transform(features)
        
        if self.model_type == "nn":
            self.model.eval()
            with torch.no_grad():
                pred = self.model(torch.FloatTensor(features_scaled))
                return pred.numpy().flatten()
        else:
            return self.model.predict(features_scaled)
