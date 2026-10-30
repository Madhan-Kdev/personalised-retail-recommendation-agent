"""
Hybrid Recommendation Engine & Ensemble Ranker
Blends scores across Collaborative Filtering, Content-Based, SVD Matrix Factorization,
and Neural CF, factoring in real-time session signals and seasonal multipliers.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from backend.ml.collaborative import CollaborativeFilteringRecommender
from backend.ml.content_based import ContentBasedRecommender
from backend.ml.matrix_factorization import MatrixFactorizationRecommender
from backend.ml.neural_cf import NeuralCFRecommender
from backend.data.generator import get_seasonal_signals

class HybridRecommendationEngine:
    def __init__(self):
        self.cf_engine = CollaborativeFilteringRecommender(k_neighbors=4)
        self.cb_engine = ContentBasedRecommender()
        self.svd_engine = MatrixFactorizationRecommender(n_components=6)
        self.ncf_engine = NeuralCFRecommender(epochs=12)
        self.is_fitted = False
        self.products = []
        self.product_map = {}
        self.customers = []
        self.customer_map = {}

    def fit(self, interactions: List[Dict[str, Any]], products: List[Dict[str, Any]], customers: List[Dict[str, Any]]):
        """Fits all sub-models with available data."""
        self.products = products
        self.product_map = {p["id"]: p for p in products}
        self.customers = customers
        self.customer_map = {c["id"]: c for c in customers}

        print("[Hybrid Engine] Fitting Collaborative Filtering...")
        self.cf_engine.fit(interactions, products, customers)

        print("[Hybrid Engine] Fitting Content-Based Filtering...")
        self.cb_engine.fit(products)

        print("[Hybrid Engine] Fitting SVD Matrix Factorization...")
        self.svd_engine.fit(interactions, products, customers)

        print("[Hybrid Engine] Fitting Neural Collaborative Filtering (PyTorch)...")
        self.ncf_engine.fit(interactions, products, customers)

        self.is_fitted = True
        print("[Hybrid Engine] All recommendation models successfully fitted and ready.")

    def recommend(self, customer: Dict[str, Any], current_season: str = "Winter", top_k: int = 6) -> List[Dict[str, Any]]:
        """Generates contextual hybrid recommendations with score attribution."""
        if not self.is_fitted:
            return []

        customer_id = customer["id"]
        is_cold_start = customer.get("is_cold_start", False) or len(customer.get("past_purchases", [])) == 0

        # Dynamic model weights based on user cold-start status
        if is_cold_start:
            weights = {
                "content": 0.55,
                "ncf": 0.15,
                "svd": 0.10,
                "cf_user": 0.10,
                "cf_item": 0.10
            }
        else:
            weights = {
                "content": 0.25,
                "ncf": 0.25,
                "svd": 0.15,
                "cf_user": 0.15,
                "cf_item": 0.20
            }

        # Gather predictions from each model
        cf_user_recs = {r["product_id"]: r["score"] for r in self.cf_engine.recommend_user_based(customer_id, top_k=25)}
        cf_item_recs = {r["product_id"]: r["score"] for r in self.cf_engine.recommend_item_based(customer_id, top_k=25)}
        cb_recs = {r["product_id"]: r["score"] for r in self.cb_engine.recommend(customer, top_k=25)}
        svd_recs = {r["product_id"]: r["score"] for r in self.svd_engine.recommend(customer_id, top_k=25)}
        ncf_recs = {r["product_id"]: r["score"] for r in self.ncf_engine.recommend(customer_id, top_k=25)}

        all_candidate_pids = set(self.product_map.keys())
        # Filter out already purchased items
        past_purchases = set(customer.get("past_purchases", []))
        candidate_pids = [pid for pid in all_candidate_pids if pid not in past_purchases]

        seasonal_data = get_seasonal_signals()
        seasonal_boosts = seasonal_data.get("category_boosts", {})

        # Active in-session context
        recent_browsed = customer.get("recent_browsed", [])
        cart_items = customer.get("cart", [])
        active_session_cats = set()
        for pid in (recent_browsed + cart_items):
            if pid in self.product_map:
                active_session_cats.add(self.product_map[pid]["category"])

        scored_candidates = []
        for pid in candidate_pids:
            prod = self.product_map[pid]
            s_content = cb_recs.get(pid, 0.0)
            s_ncf = ncf_recs.get(pid, 0.0)
            s_svd = svd_recs.get(pid, 0.0)
            s_cf_user = cf_user_recs.get(pid, 0.0)
            s_cf_item = cf_item_recs.get(pid, 0.0)

            # Base ensemble weighted score
            base_score = (
                weights["content"] * s_content +
                weights["ncf"] * s_ncf +
                weights["svd"] * s_svd +
                weights["cf_user"] * s_cf_user +
                weights["cf_item"] * s_cf_item
            )

            # In-Session Real-Time Boost: +15% if product matches active session category
            session_boost = 1.0
            if prod["category"] in active_session_cats:
                session_boost = 1.20

            # Seasonal Trend Boost: +20-35% if product aligns with current season
            seasonal_boost = 1.0
            if current_season in prod.get("seasonal_affinity", []):
                seasonal_boost = seasonal_boosts.get(prod["category"], 1.15)

            # Rating / Popularity prior
            rating_multiplier = 0.8 + (prod.get("rating", 4.5) / 5.0) * 0.2

            final_score = base_score * session_boost * seasonal_boost * rating_multiplier

            # Primary driving algorithm
            algo_scores = {
                "Content-Based Matching": s_content * weights["content"],
                "Neural CF Deep Embeddings": s_ncf * weights["ncf"],
                "Item Collaborative Filtering": s_cf_item * weights["cf_item"],
                "User Collaborative Filtering": s_cf_user * weights["cf_user"],
                "SVD Latent Factor": s_svd * weights["svd"],
                "Seasonal Trending": (seasonal_boost - 1.0)
            }
            primary_driver = max(algo_scores, key=algo_scores.get)

            scored_candidates.append({
                "product": prod,
                "final_score": round(float(final_score), 4),
                "confidence": round(min(0.98, max(0.65, float(final_score * 0.95))), 2),
                "primary_driver": primary_driver,
                "score_breakdown": {
                    "content_based": round(s_content, 3),
                    "neural_cf": round(s_ncf, 3),
                    "svd_factor": round(s_svd, 3),
                    "user_cf": round(s_cf_user, 3),
                    "item_cf": round(s_cf_item, 3),
                    "session_boost": round(session_boost, 2),
                    "seasonal_boost": round(seasonal_boost, 2)
                }
            })

        # Sort by final score descending
        scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
        return scored_candidates[:top_k]
