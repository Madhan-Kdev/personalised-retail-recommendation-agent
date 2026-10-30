"""
Collaborative Filtering Module
Implements User-Based and Item-Based Collaborative Filtering using Cosine Similarity
and k-Nearest Neighbors on the user-item interaction matrix.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

class CollaborativeFilteringRecommender:
    def __init__(self, k_neighbors: int = 5):
        self.k_neighbors = k_neighbors
        self.user_item_matrix = None
        self.user_ids = []
        self.item_ids = []
        self.user_to_idx = {}
        self.item_to_idx = {}
        self.idx_to_item = {}
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None

    def fit(self, interactions: List[Dict[str, Any]], products: List[Dict[str, Any]], customers: List[Dict[str, Any]]):
        """Builds interaction matrix and calculates similarity matrices."""
        self.user_ids = [c["id"] for c in customers]
        self.item_ids = [p["id"] for p in products]

        self.user_to_idx = {uid: i for i, uid in enumerate(self.user_ids)}
        self.item_to_idx = {iid: i for i, iid in enumerate(self.item_ids)}
        self.idx_to_item = {i: iid for i, iid in enumerate(self.item_ids)}

        num_users = len(self.user_ids)
        num_items = len(self.item_ids)
        self.user_item_matrix = np.zeros((num_users, num_items), dtype=np.float32)

        # Weight scale by event type
        event_weights = {
            "purchase": 5.0,
            "rating": 4.5,
            "add_to_cart": 3.0,
            "click": 1.5,
            "view": 1.0
        }

        # Fill with customer past purchases
        for c in customers:
            u_idx = self.user_to_idx.get(c["id"])
            if u_idx is not None:
                for pid in c.get("past_purchases", []):
                    p_idx = self.item_to_idx.get(pid)
                    if p_idx is not None:
                        self.user_item_matrix[u_idx, p_idx] = max(self.user_item_matrix[u_idx, p_idx], 5.0)

        # Fill with interaction logs
        for inter in interactions:
            u_idx = self.user_to_idx.get(inter["customer_id"])
            p_idx = self.item_to_idx.get(inter["product_id"])
            if u_idx is not None and p_idx is not None:
                wt = event_weights.get(inter["event_type"], 1.0)
                if inter.get("rating"):
                    wt = float(inter["rating"])
                self.user_item_matrix[u_idx, p_idx] = max(self.user_item_matrix[u_idx, p_idx], wt)

        # Compute User-User Cosine Similarity
        user_norms = np.linalg.norm(self.user_item_matrix, axis=1, keepdims=True)
        user_norms[user_norms == 0] = 1.0
        normalized_users = self.user_item_matrix / user_norms
        self.user_similarity_matrix = np.dot(normalized_users, normalized_users.T)

        # Compute Item-Item Cosine Similarity
        item_matrix = self.user_item_matrix.T
        item_norms = np.linalg.norm(item_matrix, axis=1, keepdims=True)
        item_norms[item_norms == 0] = 1.0
        normalized_items = item_matrix / item_norms
        self.item_similarity_matrix = np.dot(normalized_items, normalized_items.T)

    def recommend_user_based(self, customer_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Recommends products based on similar users' preferences."""
        if customer_id not in self.user_to_idx:
            return []

        u_idx = self.user_to_idx[customer_id]
        user_vector = self.user_item_matrix[u_idx]

        # Top similar users (excluding self)
        sim_scores = self.user_similarity_matrix[u_idx].copy()
        sim_scores[u_idx] = -1.0
        top_user_indices = np.argsort(sim_scores)[::-1][:self.k_neighbors]

        # Aggregate weighted scores for items
        predicted_scores = np.zeros(len(self.item_ids))
        similarity_sum = 0.0

        for sim_u_idx in top_user_indices:
            weight = sim_scores[sim_u_idx]
            if weight <= 0:
                continue
            predicted_scores += weight * self.user_item_matrix[sim_u_idx]
            similarity_sum += weight

        if similarity_sum > 0:
            predicted_scores /= similarity_sum

        # Suppress already purchased items
        predicted_scores[user_vector >= 4.5] = 0.0

        # Rank items
        top_item_indices = np.argsort(predicted_scores)[::-1][:top_k]
        results = []
        max_score = np.max(predicted_scores) if np.max(predicted_scores) > 0 else 1.0

        for idx in top_item_indices:
            score = float(predicted_scores[idx])
            if score > 0:
                norm_score = min(1.0, score / max_score)
                results.append({
                    "product_id": self.idx_to_item[idx],
                    "score": round(norm_score, 4),
                    "algorithm": "User-Based Collaborative Filtering",
                    "reason_hint": "Customers with shopping profiles similar to yours frequently chose this item."
                })

        return results

    def recommend_item_based(self, customer_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Recommends products based on items similar to customer's history."""
        if customer_id not in self.user_to_idx:
            return []

        u_idx = self.user_to_idx[customer_id]
        user_vector = self.user_item_matrix[u_idx]
        interacted_items = np.where(user_vector > 0)[0]

        if len(interacted_items) == 0:
            return []

        # Predict score for each unvisited item based on similarity to interacted items
        predicted_scores = np.zeros(len(self.item_ids))
        for item_idx in interacted_items:
            user_rating = user_vector[item_idx]
            sim_to_others = self.item_similarity_matrix[item_idx]
            predicted_scores += sim_to_others * user_rating

        # Suppress already heavily purchased items
        predicted_scores[user_vector >= 4.5] = 0.0

        top_item_indices = np.argsort(predicted_scores)[::-1][:top_k]
        results = []
        max_score = np.max(predicted_scores) if np.max(predicted_scores) > 0 else 1.0

        for idx in top_item_indices:
            score = float(predicted_scores[idx])
            if score > 0:
                norm_score = min(1.0, score / max_score)
                results.append({
                    "product_id": self.idx_to_item[idx],
                    "score": round(norm_score, 4),
                    "algorithm": "Item-Based Collaborative Filtering",
                    "reason_hint": "Complements items you have interacted with or purchased previously."
                })

        return results
