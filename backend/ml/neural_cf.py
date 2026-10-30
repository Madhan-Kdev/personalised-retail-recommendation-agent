"""
Neural Collaborative Filtering (NCF / NeuMF) Module
PyTorch implementation combining Generalized Matrix Factorization (GMF)
and Deep Multi-Layer Perceptrons (MLP) for non-linear user-item interaction learning.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Dict, Any

class NeuMF(nn.Module):
    def __init__(self, num_users: int, num_items: int, latent_dim_gmf: int = 8, latent_dim_mlp: int = 16, mlp_hidden_dims: List[int] = [32, 16, 8]):
        super(NeuMF, self).__init__()

        # GMF Embeddings
        self.user_embed_gmf = nn.Embedding(num_users, latent_dim_gmf)
        self.item_embed_gmf = nn.Embedding(num_items, latent_dim_gmf)

        # MLP Embeddings
        self.user_embed_mlp = nn.Embedding(num_users, latent_dim_mlp)
        self.item_embed_mlp = nn.Embedding(num_items, latent_dim_mlp)

        # MLP Layers
        mlp_layers = []
        input_dim = latent_dim_mlp * 2
        for hidden_dim in mlp_hidden_dims:
            mlp_layers.append(nn.Linear(input_dim, hidden_dim))
            mlp_layers.append(nn.ReLU())
            mlp_layers.append(nn.Dropout(p=0.1))
            input_dim = hidden_dim
        self.mlp = nn.Sequential(*mlp_layers)

        # Final Prediction Layer
        final_input_dim = latent_dim_gmf + mlp_hidden_dims[-1]
        self.prediction_layer = nn.Linear(final_input_dim, 1)
        self.sigmoid = nn.Sigmoid()

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        nn.init.normal_(self.user_embed_gmf.weight, std=0.01)
        nn.init.normal_(self.item_embed_gmf.weight, std=0.01)
        nn.init.normal_(self.user_embed_mlp.weight, std=0.01)
        nn.init.normal_(self.item_embed_mlp.weight, std=0.01)

    def forward(self, user_indices: torch.Tensor, item_indices: torch.Tensor) -> torch.Tensor:
        # GMF Branch
        user_gmf = self.user_embed_gmf(user_indices)
        item_gmf = self.item_embed_gmf(item_indices)
        gmf_out = user_gmf * item_gmf

        # MLP Branch
        user_mlp = self.user_embed_mlp(user_indices)
        item_mlp = self.item_embed_mlp(item_indices)
        mlp_in = torch.cat([user_mlp, item_mlp], dim=-1)
        mlp_out = self.mlp(mlp_in)

        # Fusion
        fusion = torch.cat([gmf_out, mlp_out], dim=-1)
        out = self.prediction_layer(fusion)
        return self.sigmoid(out).squeeze(-1)

class NeuralCFRecommender:
    def __init__(self, latent_dim_gmf: int = 8, latent_dim_mlp: int = 16, epochs: int = 15, lr: float = 0.005):
        self.latent_dim_gmf = latent_dim_gmf
        self.latent_dim_mlp = latent_dim_mlp
        self.epochs = epochs
        self.lr = lr
        self.model = None
        self.user_to_idx = {}
        self.item_to_idx = {}
        self.idx_to_item = {}
        self.num_users = 0
        self.num_items = 0

    def fit(self, interactions: List[Dict[str, Any]], products: List[Dict[str, Any]], customers: List[Dict[str, Any]]):
        """Prepares dataset and trains the Neural Collaborative Filtering model."""
        self.user_to_idx = {c["id"]: i for i, c in enumerate(customers)}
        self.item_to_idx = {p["id"]: i for i, p in enumerate(products)}
        self.idx_to_item = {i: p["id"] for i, p in enumerate(products)}

        self.num_users = len(customers)
        self.num_items = len(products)

        # Build training pairs (user, item, label)
        user_list = []
        item_list = []
        label_list = []

        # Positive interactions
        for c in customers:
            u_idx = self.user_to_idx.get(c["id"])
            for pid in c.get("past_purchases", []):
                p_idx = self.item_to_idx.get(pid)
                if u_idx is not None and p_idx is not None:
                    user_list.append(u_idx)
                    item_list.append(p_idx)
                    label_list.append(1.0)

        for inter in interactions:
            u_idx = self.user_to_idx.get(inter["customer_id"])
            p_idx = self.item_to_idx.get(inter["product_id"])
            if u_idx is not None and p_idx is not None:
                user_list.append(u_idx)
                item_list.append(p_idx)
                label_list.append(1.0 if inter["event_type"] in ["purchase", "add_to_cart", "rating"] else 0.7)

        # Negative sampling (generate 2x negative pairs)
        existing_pairs = set(zip(user_list, item_list))
        num_negatives = len(user_list) * 2
        for _ in range(num_negatives):
            u = np.random.randint(0, self.num_users)
            i = np.random.randint(0, self.num_items)
            if (u, i) not in existing_pairs:
                user_list.append(u)
                item_list.append(i)
                label_list.append(0.0)

        u_tensor = torch.tensor(user_list, dtype=torch.long)
        i_tensor = torch.tensor(item_list, dtype=torch.long)
        y_tensor = torch.tensor(label_list, dtype=torch.float32)

        self.model = NeuMF(self.num_users, self.num_items, self.latent_dim_gmf, self.latent_dim_mlp)
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=1e-4)
        criterion = nn.BCELoss()

        self.model.train()
        dataset_size = len(user_list)
        batch_size = 64

        for epoch in range(self.epochs):
            indices = np.random.permutation(dataset_size)
            for start in range(0, dataset_size, batch_size):
                batch_idx = indices[start:start + batch_size]
                b_u = u_tensor[batch_idx]
                b_i = i_tensor[batch_idx]
                b_y = y_tensor[batch_idx]

                optimizer.zero_grad()
                preds = self.model(b_u, b_i)
                loss = criterion(preds, b_y)
                loss.backward()
                optimizer.step()

        self.model.eval()

    def recommend(self, customer_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Computes neural prediction scores for all items for the given user."""
        if customer_id not in self.user_to_idx or self.model is None:
            return []

        u_idx = self.user_to_idx[customer_id]
        u_tensor = torch.tensor([u_idx] * self.num_items, dtype=torch.long)
        i_tensor = torch.arange(self.num_items, dtype=torch.long)

        with torch.no_grad():
            scores = self.model(u_tensor, i_tensor).numpy()

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            results.append({
                "product_id": self.idx_to_item[int(idx)],
                "score": round(float(scores[idx]), 4),
                "algorithm": "Neural Collaborative Filtering (NeuMF Deep Learning)",
                "reason_hint": "Deep neural embeddings captured complex non-linear affinity with your preferences."
            })

        return results
