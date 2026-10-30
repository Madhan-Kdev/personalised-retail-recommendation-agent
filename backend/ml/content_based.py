"""
Content-Based Filtering Module
Uses TF-IDF vectorization and semantic feature representations of product metadata
(title, category, subcategory, brand, description, tags) to match with customer preferences.
"""

import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.product_vectors = None
        self.products = []
        self.product_map = {}
        self.id_to_idx = {}
        self.idx_to_id = {}

    def fit(self, products: List[Dict[str, Any]]):
        """Builds TF-IDF feature matrix from product catalog."""
        self.products = products
        self.product_map = {p["id"]: p for p in products}
        self.id_to_idx = {p["id"]: i for i, p in enumerate(products)}
        self.idx_to_id = {i: p["id"] for i, p in enumerate(products)}

        # Construct rich corpus string for each product
        corpus = []
        for p in products:
            tags_str = " ".join(p.get("tags", []))
            season_str = " ".join(p.get("seasonal_affinity", []))
            text = f"{p['title']} {p['category']} {p['subcategory']} {p['brand']} {tags_str} {season_str} {p['description']}"
            corpus.append(text)

        self.product_vectors = self.vectorizer.fit_transform(corpus)

    def get_user_profile_vector(self, customer: Dict[str, Any]) -> np.ndarray:
        """Constructs a composite preference vector for a customer."""
        weights = []
        vectors = []

        # Past purchases (high weight = 3.0)
        for pid in customer.get("past_purchases", []):
            if pid in self.id_to_idx:
                vectors.append(self.product_vectors[self.id_to_idx[pid]].toarray())
                weights.append(3.0)

        # Cart items (weight = 2.5)
        for pid in customer.get("cart", []):
            if pid in self.id_to_idx:
                vectors.append(self.product_vectors[self.id_to_idx[pid]].toarray())
                weights.append(2.5)

        # Recent browsed (weight = 1.5)
        for pid in customer.get("recent_browsed", []):
            if pid in self.id_to_idx:
                vectors.append(self.product_vectors[self.id_to_idx[pid]].toarray())
                weights.append(1.5)

        if len(vectors) > 0:
            weighted_sum = np.zeros_like(vectors[0])
            total_weight = sum(weights)
            for vec, wt in zip(vectors, weights):
                weighted_sum += vec * wt
            profile_vec = weighted_sum / total_weight
            return profile_vec

        # Cold-start fallback: build profile from preferred categories
        pref_cats = customer.get("preferred_categories", [])
        if pref_cats:
            cat_text = " ".join(pref_cats) + " " + customer.get("persona_title", "")
            return self.vectorizer.transform([cat_text]).toarray()

        return np.zeros((1, self.product_vectors.shape[1]))

    def recommend(self, customer: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """Recommends products based on content similarity to user profile."""
        user_vec = self.get_user_profile_vector(customer)
        if np.all(user_vec == 0):
            return []

        # Cosine similarity against all products
        sim_scores = cosine_similarity(user_vec, self.product_vectors)[0]

        # Suppress items already purchased
        for pid in customer.get("past_purchases", []):
            if pid in self.id_to_idx:
                sim_scores[self.id_to_idx[pid]] = 0.0

        top_indices = np.argsort(sim_scores)[::-1][:top_k]
        results = []
        max_score = np.max(sim_scores) if np.max(sim_scores) > 0 else 1.0

        for idx in top_indices:
            score = float(sim_scores[idx])
            if score > 0.05:
                norm_score = min(1.0, score / max_score)
                prod = self.products[idx]
                results.append({
                    "product_id": prod["id"],
                    "score": round(norm_score, 4),
                    "algorithm": "Content-Based Filtering (TF-IDF)",
                    "matching_category": prod["category"],
                    "matching_tags": prod.get("tags", [])[:3],
                    "reason_hint": f"Matches your interest in {prod['category']} ({prod['subcategory']}) with similar attributes."
                })

        return results
