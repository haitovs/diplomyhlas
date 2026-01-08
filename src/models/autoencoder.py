"""
LSTM Autoencoder Module
Unsupervised anomaly detection using reconstruction error
"""

import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from typing import Tuple, Optional
import yaml
from pathlib import Path
from tqdm import tqdm


class LSTMAutoencoder(nn.Module):
    """
    LSTM-based Autoencoder for sequence anomaly detection
    
    Architecture:
        Encoder: LSTM -> Dense -> Latent
        Decoder: Dense -> LSTM -> Output
    """
    
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 64,
        latent_dim: int = 32,
        num_layers: int = 2,
        dropout: float = 0.2
    ):
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        self.num_layers = num_layers
        
        # Encoder
        self.encoder_lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        self.encoder_fc = nn.Linear(hidden_dim, latent_dim)
        
        # Decoder
        self.decoder_fc = nn.Linear(latent_dim, hidden_dim)
        self.decoder_lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        self.output_fc = nn.Linear(hidden_dim, input_dim)
        
        # Activation
        self.relu = nn.ReLU()
        
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to latent space"""
        # x: (batch, seq_len, input_dim) or (batch, input_dim)
        if x.dim() == 2:
            x = x.unsqueeze(1)  # Add sequence dimension
        
        _, (h_n, _) = self.encoder_lstm(x)
        # h_n: (num_layers, batch, hidden_dim)
        h_n = h_n[-1]  # Take last layer
        z = self.relu(self.encoder_fc(h_n))
        return z
    
    def decode(self, z: torch.Tensor, seq_len: int = 1) -> torch.Tensor:
        """Decode from latent space"""
        # z: (batch, latent_dim)
        h = self.relu(self.decoder_fc(z))
        # Repeat for sequence
        h = h.unsqueeze(1).repeat(1, seq_len, 1)
        output, _ = self.decoder_lstm(h)
        reconstructed = self.output_fc(output)
        return reconstructed.squeeze(1)  # Remove seq dim if added
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass: encode and decode"""
        seq_len = x.size(1) if x.dim() == 3 else 1
        z = self.encode(x)
        reconstructed = self.decode(z, seq_len)
        return reconstructed, z
    
    def get_reconstruction_error(self, x: torch.Tensor) -> torch.Tensor:
        """Calculate reconstruction error for each sample"""
        reconstructed, _ = self.forward(x)
        # Mean squared error per sample
        error = torch.mean((x - reconstructed) ** 2, dim=-1)
        if error.dim() > 1:
            error = error.mean(dim=-1)
        return error


class AnomalyDetector:
    """Wrapper class for training and using the autoencoder"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model = None
        self.device = torch.device(self.config['hardware']['device'])
        self.threshold = None  # Anomaly threshold
    
    def create_model(self, input_dim: int) -> LSTMAutoencoder:
        """Create the autoencoder model"""
        params = self.config['models']['lstm_autoencoder']
        
        self.model = LSTMAutoencoder(
            input_dim=input_dim,
            hidden_dim=params['hidden_dim'],
            latent_dim=params['latent_dim'],
            num_layers=params['num_layers'],
            dropout=params['dropout']
        ).to(self.device)
        
        print(f"Created LSTM Autoencoder on {self.device}")
        print(f"  Input dim: {input_dim}")
        print(f"  Hidden dim: {params['hidden_dim']}")
        print(f"  Latent dim: {params['latent_dim']}")
        
        return self.model
    
    def train(
        self,
        X_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        epochs: Optional[int] = None,
        batch_size: Optional[int] = None
    ) -> dict:
        """
        Train the autoencoder on NORMAL traffic only
        
        Args:
            X_train: Training data (should be normal traffic only!)
            X_val: Validation data
            epochs: Number of epochs
            batch_size: Batch size
            
        Returns:
            Training history
        """
        if self.model is None:
            self.create_model(X_train.shape[1])
        
        epochs = epochs or self.config['training']['epochs']
        batch_size = batch_size or self.config['training']['batch_size']
        lr = self.config['training']['learning_rate']
        
        # Create data loaders
        train_tensor = torch.FloatTensor(X_train).to(self.device)
        train_dataset = TensorDataset(train_tensor, train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        val_loader = None
        if X_val is not None:
            val_tensor = torch.FloatTensor(X_val).to(self.device)
            val_dataset = TensorDataset(val_tensor, val_tensor)
            val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Optimizer and loss
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
        criterion = nn.MSELoss()
        
        # Mixed precision
        scaler = torch.cuda.amp.GradScaler() if self.config['training']['mixed_precision'] else None
        
        history = {'train_loss': [], 'val_loss': []}
        best_val_loss = float('inf')
        patience_counter = 0
        patience = self.config['training']['early_stopping_patience']
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0
            
            for batch_x, _ in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
                optimizer.zero_grad()
                
                if scaler:
                    with torch.cuda.amp.autocast():
                        reconstructed, _ = self.model(batch_x)
                        loss = criterion(reconstructed, batch_x)
                    scaler.scale(loss).backward()
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    reconstructed, _ = self.model(batch_x)
                    loss = criterion(reconstructed, batch_x)
                    loss.backward()
                    optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            history['train_loss'].append(train_loss)
            
            # Validation
            val_loss = 0
            if val_loader:
                self.model.eval()
                with torch.no_grad():
                    for batch_x, _ in val_loader:
                        reconstructed, _ = self.model(batch_x)
                        loss = criterion(reconstructed, batch_x)
                        val_loss += loss.item()
                val_loss /= len(val_loader)
                history['val_loss'].append(val_loss)
            
            scheduler.step()
            
            # Logging
            log_msg = f"Epoch {epoch+1}: Train Loss = {train_loss:.6f}"
            if val_loader:
                log_msg += f", Val Loss = {val_loss:.6f}"
            print(log_msg)
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch+1}")
                    break
        
        return history
    
    def set_threshold(self, X_normal: np.ndarray, percentile: float = 95):
        """
        Set anomaly threshold based on normal traffic
        
        Args:
            X_normal: Normal traffic samples
            percentile: Percentile for threshold (samples above are anomalies)
        """
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X_normal).to(self.device)
            errors = self.model.get_reconstruction_error(X_tensor)
            errors = errors.cpu().numpy()
        
        self.threshold = np.percentile(errors, percentile)
        print(f"Anomaly threshold set to: {self.threshold:.6f} (at {percentile}th percentile)")
        return self.threshold
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomalies
        
        Args:
            X: Input data
            
        Returns:
            Binary array: 1 = anomaly, 0 = normal
        """
        if self.threshold is None:
            raise ValueError("Threshold not set! Call set_threshold first.")
        
        errors = self.get_reconstruction_errors(X)
        return (errors > self.threshold).astype(int)
    
    def get_reconstruction_errors(self, X: np.ndarray) -> np.ndarray:
        """Get reconstruction errors for all samples"""
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            errors = self.model.get_reconstruction_error(X_tensor)
            return errors.cpu().numpy()
    
    def save(self, path: str = 'models'):
        """Save model and threshold"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'threshold': self.threshold,
            'config': self.model.input_dim
        }, path / 'autoencoder.pth')
        print(f"Saved autoencoder to {path / 'autoencoder.pth'}")
    
    def load(self, path: str = 'models'):
        """Load model and threshold"""
        path = Path(path)
        checkpoint = torch.load(path / 'autoencoder.pth', map_location=self.device)
        
        if self.model is None:
            self.create_model(checkpoint['config'])
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.threshold = checkpoint['threshold']
        print(f"Loaded autoencoder from {path / 'autoencoder.pth'}")


if __name__ == "__main__":
    # Test model creation
    detector = AnomalyDetector()
    model = detector.create_model(input_dim=78)
    print(model)
    
    # Test forward pass
    x = torch.randn(32, 78).to(detector.device)
    reconstructed, z = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Latent shape: {z.shape}")
    print(f"Reconstructed shape: {reconstructed.shape}")
