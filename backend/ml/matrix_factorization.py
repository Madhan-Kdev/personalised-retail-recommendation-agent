"""
Matrix Factorization Module
Applies Truncated Singular Value Decomposition (SVD) / Latent Factor Model
to extract latent user preferences and product features.
"""

import numpy as np
from typing import List, Dict, Any
from sklearn.decomposition import TruncatedSVD

class MatrixFactorizationRecommender:
    def __init__(self, n_components: int = 6):
        self.n_components = n_components
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.user_ids = []
        self.item_ids = []
        self.user_to_idx = {}
        self.item_to_idx = {}
        self.idx_to_item = {}
        self.reconstructed_matrix = None
        self.user_latent = None
        self.item_latent = None

    def fit(self, interactions: List[Dict[str, Any]], products: List[Dict[str, Any]], customers: List[Dict[str, Any]]):
        """Fits TruncatedSVD on the user-item interaction matrix."""
        self.user_ids = [c["id"] for c in customers]
        self.item_ids = [p["id"] for p in products]

        self.user_to_idx = {uid: i for i, uid in enumerate(self.user_ids)}
        self.item_to_idx = {iid: i for i, iid in enumerate(self.item_ids)}
        self.idx_to_item = {i: iid for i, iid in enumerate(self.item_ids)}

        num_users = len(self.user_ids)
        num_items = len(self.item_ids)
        R = np.zeros((num_users, num_items), dtype=np.float32)

        event_weights = {"purchase": 5.0, "rating": 4.5, "add_to_cart": 3.0, "click": 1.5, "view": 1.0}

        for c in customers:
            u_idx = self.user_to_idx.get(c["id"])
            if u_idx is not None:
                for pid in c.get("past_purchases", []):
                    p_idx = self.item_to_idx.get(pid)
                    if p_idx is not None:
                        R[u_idx, p_idx] = 5.0

        for inter in interactions:
            u_idx = self.user_to_idx.get(inter["customer_id"])
            p_idx = self.item_to_idx.get(inter["product_id"])
            if u_idx is not None and p_idx is not None:
                wt = event_weights.get(inter["event_type"], 1.0)
                if inter.get("rating"):
                    wt = float(inter["rating"])
                R[u_idx, p_idx] = max(R[u_idx, p_idx], wt)

        # Set components capped by min dimension
        components = min(self.n_components, num_users - 1, num_items - 1)
        if components < 2:
            components = 2

        self.svd = TruncatedSVD(n_components=components, random_state=42)
        self.user_latent = self.svd.fit_transform(R)
        self.item_latent = self.svd.components_
        self.reconstructed_matrix = np.dot(self.user_latent, self.item_latent)

    def recommend(self, customer_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Recommends products by ranking predicted latent scores."""
        if customer_id not in self.user_to_idx:
            return []

        u_idx = self.user_to_idx[customer_id]
        scores = self.reconstructed_matrix[u_idx].copy()

        # Normalize scores to [0, 1]
        min_val = np.min(scores)
        max_val = np.max(scores)
        if max_val > min_val:
            scores = (scores - min_val) / (max_val - min_val)
        else:
            scores = np.ones_like(scores) * 0.5

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            results.append({
                "product_id": self.idx_to_item[idx],
                "score": round(float(scores[idx]), 4),
                "algorithm": "Matrix Factorization (SVD Latent Factors)",
                "reason_hint": "Discovered through cross-category latent preference embedding patterns."
            })

        return results
