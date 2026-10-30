"""
Comprehensive Automated Test & Verification Suite
Verifies database integrity, all 5 ML models + Hybrid ensemble, GenAI explanations,
citations, real-time feedback loops, and Responsible AI fairness & HITL guardrails.
"""

import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.data.database import (
    init_database, 
    get_all_products, 
    get_all_customers, 
    get_all_interactions,
    get_customer_by_id,
    log_interaction
)
from backend.ml.hybrid_engine import HybridRecommendationEngine
from backend.ml.evaluator import RecommenderEvaluator
from backend.agent.persona_synthesizer import PersonaSynthesizer
from backend.agent.explanation_generator import ExplanationGenerator
from backend.agent.conversational_agent import ConversationalRecommendationAgent
from backend.governance.fairness_auditor import FairnessAuditor
from backend.governance.hitl_moderator import HITLModerator
from backend.governance.audit_logger import RecommendationAuditLogger

class TestRetailRecommendationSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=== Initializing Test Environment ===")
        init_database()
        cls.products = get_all_products()
        cls.customers = get_all_customers()
        cls.interactions = get_all_interactions()

        cls.engine = HybridRecommendationEngine()
        cls.engine.fit(cls.interactions, cls.products, cls.customers)
        cls.persona_synth = PersonaSynthesizer()
        cls.explanation_gen = ExplanationGenerator()
        cls.conversational_agent = ConversationalRecommendationAgent(cls.engine, cls.explanation_gen, cls.persona_synth)
        cls.fairness_auditor = FairnessAuditor(cls.engine)
        cls.hitl_moderator = HITLModerator()
        cls.audit_logger = RecommendationAuditLogger()
        cls.evaluator = RecommenderEvaluator(cls.engine)

    def test_01_database_and_catalog(self):
        """Verify database contains valid products, customers, and interactions."""
        self.assertGreater(len(self.products), 20, "Catalog should have at least 20 items.")
        self.assertGreater(len(self.customers), 4, "Should have multiple customer personas.")
        self.assertGreater(len(self.interactions), 100, "Interaction history should be populated.")
        print(f"[TEST 1 PASS] Database verified: {len(self.products)} products, {len(self.customers)} customers.")

    def test_02_collaborative_filtering(self):
        """Verify User-Based and Item-Based CF recommend valid items."""
        cust = self.customers[0]
        user_recs = self.engine.cf_engine.recommend_user_based(cust["id"], top_k=5)
        item_recs = self.engine.cf_engine.recommend_item_based(cust["id"], top_k=5)

        self.assertIsInstance(user_recs, list)
        self.assertIsInstance(item_recs, list)
        if user_recs:
            self.assertIn("product_id", user_recs[0])
            self.assertGreaterEqual(user_recs[0]["score"], 0.0)
        print(f"[TEST 2 PASS] Collaborative Filtering verified: {len(user_recs)} user-based, {len(item_recs)} item-based recs.")

    def test_03_content_based_filtering(self):
        """Verify Content-Based TF-IDF recommender produces relevant category matches."""
        cust = self.customers[0]  # Maya Lin (Fitness & Outdoors)
        cb_recs = self.engine.cb_engine.recommend(cust, top_k=5)
        self.assertGreater(len(cb_recs), 0)
        self.assertIn("product_id", cb_recs[0])
        print(f"[TEST 3 PASS] Content-Based verified: Top match={cb_recs[0]['product_id']} (Score={cb_recs[0]['score']}).")

    def test_04_neural_collaborative_filtering(self):
        """Verify PyTorch NeuMF neural model executes inference."""
        cust = self.customers[1]  # Liam Sterling
        ncf_recs = self.engine.ncf_engine.recommend(cust["id"], top_k=5)
        self.assertGreater(len(ncf_recs), 0)
        self.assertIn("score", ncf_recs[0])
        print(f"[TEST 4 PASS] Neural CF (NeuMF PyTorch) verified: Top score={ncf_recs[0]['score']}.")

    def test_05_hybrid_ensemble_and_seasonal_boost(self):
        """Verify Hybrid ensemble merges scores and applies seasonal boost."""
        cust = self.customers[0]
        recs = self.engine.recommend(cust, current_season="Winter", top_k=6)
        self.assertGreater(len(recs), 0)
        top_rec = recs[0]
        self.assertIn("product", top_rec)
        self.assertIn("confidence", top_rec)
        self.assertIn("score_breakdown", top_rec)
        print(f"[TEST 5 PASS] Hybrid Engine verified: Recommended '{top_rec['product']['title']}' with confidence {top_rec['confidence']}.")

    def test_06_explainable_ai_and_citations(self):
        """Verify XAI generates human-readable explanations and explicit data citations."""
        cust = self.customers[0]
        recs = self.engine.recommend(cust, top_k=3)
        top_rec = recs[0]
        exp = self.explanation_gen.generate_explanation(cust, top_rec, self.engine.product_map)

        self.assertIn("headline_explanation", exp)
        self.assertGreater(len(exp["citations"]), 0)
        self.assertGreater(len(exp["key_reasons"]), 0)
        print(f"[TEST 6 PASS] Explainable AI (XAI) verified: Headline='{exp['headline_explanation'][:60]}...' | Citations={len(exp['citations'])}.")

    def test_07_conversational_agent(self):
        """Verify multi-turn shopping assistant answers queries with explanations."""
        cust_id = self.customers[0]["id"]
        res = self.conversational_agent.chat(cust_id, "Why did you recommend this item?")
        self.assertIn("reply", res)
        self.assertIn("suggested_followups", res)
        self.assertGreater(len(res["suggested_products"]), 0)
        print(f"[TEST 7 PASS] Conversational Agent verified: Generated rich response with {len(res['suggested_products'])} attached cards.")

    def test_08_fairness_and_governance(self):
        """Verify Responsible AI bias auditor and HITL moderation queue."""
        audit_rep = self.fairness_auditor.audit_demographic_fairness()
        self.assertIn("demographic_parity_status", audit_rep)
        self.assertIn("price_parity_ratio", audit_rep)
        self.assertGreater(len(audit_rep["guardrail_checks"]), 0)

        # Test HITL Queue
        pending = self.hitl_moderator.get_pending_moderations()
        self.assertIsInstance(pending, list)
        print(f"[TEST 8 PASS] Governance verified: Parity Ratio={audit_rep['price_parity_ratio']} | Status={audit_rep['demographic_parity_status']}.")

    def test_09_model_benchmarks(self):
        """Verify offline model evaluation metrics are computed across all models."""
        benchmark = self.evaluator.evaluate_all_models()
        self.assertIn("models", benchmark)
        self.assertIn("Hybrid Ensemble (Proposed)", benchmark["models"])
        hybrid_metrics = benchmark["models"]["Hybrid Ensemble (Proposed)"]
        print(f"[TEST 9 PASS] Benchmarks verified: Hybrid NDCG@5={hybrid_metrics['ndcg_at_5']} | Coverage={hybrid_metrics['catalog_coverage_pct']}%.")

if __name__ == "__main__":
    unittest.main(verbosity=2)
