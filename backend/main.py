"""
FastAPI Server for Personalized Retail Recommendation Agent
Exposes high-performance REST endpoints for recommendation generation,
real-time session telemetry, GenAI persona & explanation generation,
conversational shopping assistant, governance & bias auditing, and model benchmarking.
"""

import time
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.data.database import (
    init_database,
    get_all_products,
    get_product_by_id,
    get_all_customers,
    get_customer_by_id,
    update_customer_session,
    log_interaction,
    get_all_interactions
)
from backend.data.generator import get_seasonal_signals
from backend.ml.hybrid_engine import HybridRecommendationEngine
from backend.ml.evaluator import RecommenderEvaluator
from backend.agent.persona_synthesizer import PersonaSynthesizer
from backend.agent.explanation_generator import ExplanationGenerator
from backend.agent.conversational_agent import ConversationalRecommendationAgent
from backend.governance.fairness_auditor import FairnessAuditor
from backend.governance.hitl_moderator import HITLModerator
from backend.governance.audit_logger import RecommendationAuditLogger

# Initialize FastAPI App
app = FastAPI(
    title="Personalized Retail Recommendation Agent API",
    description="Enterprise Dual AI/ML + GenAI Retail Recommendation Agent with Responsible AI Guardrails",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Engine & Agent Singletons
hybrid_engine = HybridRecommendationEngine()
evaluator = None
persona_synth = PersonaSynthesizer()
explanation_gen = ExplanationGenerator()
conversational_agent = None
fairness_auditor = None
hitl_moderator = HITLModerator()
audit_logger = RecommendationAuditLogger()

@app.on_event("startup")
def startup_event():
    global evaluator, conversational_agent, fairness_auditor
    print("[Startup] Initializing Database...")
    init_database()

    products = get_all_products()
    customers = get_all_customers()
    interactions = get_all_interactions()

    print(f"[Startup] Loaded {len(products)} products, {len(customers)} customers, {len(interactions)} interactions.")
    print("[Startup] Training and fitting ML recommendation models...")
    hybrid_engine.fit(interactions, products, customers)

    evaluator = RecommenderEvaluator(hybrid_engine)
    conversational_agent = ConversationalRecommendationAgent(hybrid_engine, explanation_gen, persona_synth)
    fairness_auditor = FairnessAuditor(hybrid_engine)
    print("[Startup] Personalized Retail Recommendation Agent is live and ready!")

# Pydantic Request Models
class InteractionRequest(BaseModel):
    customer_id: str
    product_id: str
    event_type: str  # view, click, like, dislike, add_to_cart, purchase
    rating: Optional[float] = None
    dwell_time_sec: Optional[int] = 0

class ChatRequest(BaseModel):
    customer_id: str
    message: str
    chat_history: Optional[List[Dict[str, str]]] = []

class HITLActionRequest(BaseModel):
    decision: str  # APPROVED or REJECTED
    reviewed_by: Optional[str] = "Admin Specialist"
    notes: Optional[str] = ""

# --- REST Endpoints ---

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Personalized Retail Recommendation Agent",
        "models_loaded": hybrid_engine.is_fitted,
        "catalog_size": len(hybrid_engine.products),
        "active_customers": len(hybrid_engine.customers)
    }

@app.get("/api/seasonal")
def get_season_info():
    return get_seasonal_signals()

@app.get("/api/customers")
def list_customers():
    return get_all_customers()

@app.get("/api/customers/{customer_id}")
def get_customer_profile(customer_id: str):
    cust = get_customer_by_id(customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Enriched synthesized persona
    persona_synthesis = persona_synth.synthesize_persona(cust, hybrid_engine.product_map)
    return {
        "profile": cust,
        "persona_synthesis": persona_synthesis
    }

@app.get("/api/products")
def list_products(category: Optional[str] = None, search: Optional[str] = None):
    products = get_all_products()
    if category and category != "All":
        products = [p for p in products if p["category"].lower() == category.lower()]
    if search:
        s = search.lower()
        products = [p for p in products if s in p["title"].lower() or s in p["brand"].lower() or any(s in t for t in p["tags"])]
    return products

@app.get("/api/recommendations")
def get_recommendations(
    customer_id: str = Query(..., description="Customer ID, e.g. CUST-001"),
    season: str = Query("Winter", description="Current season context"),
    model_type: str = Query("hybrid", description="hybrid | user_cf | item_cf | content | svd | ncf"),
    top_k: int = Query(6, description="Number of recommendations")
):
    start_time = time.time()
    cust = get_customer_by_id(customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    catalog_map = hybrid_engine.product_map
    recs = []

    if model_type == "user_cf":
        raw = hybrid_engine.cf_engine.recommend_user_based(customer_id, top_k=top_k)
        for r in raw:
            prod = catalog_map.get(r["product_id"])
            if prod:
                recs.append({
                    "product": prod,
                    "final_score": r["score"],
                    "confidence": r["score"],
                    "primary_driver": "User Collaborative Filtering",
                    "score_breakdown": {"user_cf": r["score"]}
                })
    elif model_type == "item_cf":
        raw = hybrid_engine.cf_engine.recommend_item_based(customer_id, top_k=top_k)
        for r in raw:
            prod = catalog_map.get(r["product_id"])
            if prod:
                recs.append({
                    "product": prod,
                    "final_score": r["score"],
                    "confidence": r["score"],
                    "primary_driver": "Item Collaborative Filtering",
                    "score_breakdown": {"item_cf": r["score"]}
                })
    elif model_type == "content":
        raw = hybrid_engine.cb_engine.recommend(cust, top_k=top_k)
        for r in raw:
            prod = catalog_map.get(r["product_id"])
            if prod:
                recs.append({
                    "product": prod,
                    "final_score": r["score"],
                    "confidence": r["score"],
                    "primary_driver": "Content-Based Matching",
                    "score_breakdown": {"content_based": r["score"]}
                })
    elif model_type == "svd":
        raw = hybrid_engine.svd_engine.recommend(customer_id, top_k=top_k)
        for r in raw:
            prod = catalog_map.get(r["product_id"])
            if prod:
                recs.append({
                    "product": prod,
                    "final_score": r["score"],
                    "confidence": r["score"],
                    "primary_driver": "SVD Latent Factor",
                    "score_breakdown": {"svd_factor": r["score"]}
                })
    elif model_type == "ncf":
        raw = hybrid_engine.ncf_engine.recommend(customer_id, top_k=top_k)
        for r in raw:
            prod = catalog_map.get(r["product_id"])
            if prod:
                recs.append({
                    "product": prod,
                    "final_score": r["score"],
                    "confidence": r["score"],
                    "primary_driver": "Neural CF Deep Embeddings",
                    "score_breakdown": {"neural_cf": r["score"]}
                })
    else:
        # Default: Hybrid Ensemble
        recs = hybrid_engine.recommend(cust, current_season=season, top_k=top_k)

    # Attach Natural Language Explanations and Citations (XAI)
    enriched_recs = []
    recommended_pids = []
    avg_confidence = 0.0

    for item in recs:
        exp = explanation_gen.generate_explanation(cust, item, catalog_map)
        recommended_pids.append(item["product"]["id"])
        avg_confidence += item.get("confidence", 0.8)

        # Check HITL guardrail
        hitl_moderator.inspect_and_intercept(customer_id, item)

        enriched_recs.append({
            **item,
            "explanation": exp
        })

    latency_ms = round((time.time() - start_time) * 1000, 2)
    overall_confidence = round(avg_confidence / max(1, len(recs)), 2)

    # Log to immutable audit trail
    all_citations = []
    for r in enriched_recs:
        all_citations.extend(r["explanation"]["citations"])

    audit_id = audit_logger.log_recommendation_event(
        customer_id=customer_id,
        recommended_product_ids=recommended_pids,
        model=model_type,
        explanation=f"Generated {len(enriched_recs)} personalized recommendations using {model_type}",
        citations=list(set(all_citations))[:5],
        confidence=overall_confidence,
        latency_ms=latency_ms
    )

    persona_summary = persona_synth.synthesize_persona(cust, catalog_map)

    return {
        "customer_id": customer_id,
        "persona": persona_summary,
        "model_type": model_type,
        "season_context": season,
        "latency_ms": latency_ms,
        "confidence_score": overall_confidence,
        "audit_id": audit_id,
        "recommendations": enriched_recs
    }

@app.post("/api/interact")
def handle_interaction(payload: InteractionRequest):
    """Processes live customer interaction telemetry and updates session context in real-time."""
    cust = get_customer_by_id(payload.customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Record telemetry event
    log_interaction(
        customer_id=payload.customer_id,
        product_id=payload.product_id,
        event_type=payload.event_type,
        rating=payload.rating,
        dwell_time_sec=payload.dwell_time_sec or 0
    )

    # Update in-session state
    recent_browsed = list(cust.get("recent_browsed", []))
    cart = list(cust.get("cart", []))
    past_purchases = list(cust.get("past_purchases", []))

    if payload.event_type in ["view", "click", "like"]:
        if payload.product_id not in recent_browsed:
            recent_browsed.insert(0, payload.product_id)
            recent_browsed = recent_browsed[:8]

    elif payload.event_type == "add_to_cart":
        if payload.product_id not in cart:
            cart.append(payload.product_id)

    elif payload.event_type == "purchase":
        if payload.product_id not in past_purchases:
            past_purchases.append(payload.product_id)
        if payload.product_id in cart:
            cart.remove(payload.product_id)

    elif payload.event_type == "dislike":
        if payload.product_id in recent_browsed:
            recent_browsed.remove(payload.product_id)
        if payload.product_id in cart:
            cart.remove(payload.product_id)

    update_customer_session(
        customer_id=payload.customer_id,
        browsed=recent_browsed,
        cart=cart,
        purchases=past_purchases
    )

    # Update runtime memory map
    updated_cust = get_customer_by_id(payload.customer_id)
    hybrid_engine.customer_map[payload.customer_id] = updated_cust

    return {
        "status": "success",
        "message": f"Recorded {payload.event_type} on product {payload.product_id}",
        "session_state": {
            "recent_browsed_count": len(recent_browsed),
            "cart_count": len(cart),
            "past_purchases_count": len(past_purchases)
        }
    }

@app.post("/api/chat")
def handle_chat(payload: ChatRequest):
    """Conversational Shopping Assistant endpoint."""
    res = conversational_agent.chat(
        customer_id=payload.customer_id,
        message=payload.message,
        chat_history=payload.chat_history or []
    )
    return res

@app.get("/api/governance/fairness")
def get_fairness_audit():
    """Returns demographic parity and segment bias audit report."""
    return fairness_auditor.audit_demographic_fairness()

@app.get("/api/governance/audit-logs")
def list_audit_logs(limit: int = Query(30, description="Log entry limit")):
    """Returns immutable recommendation audit trail."""
    return audit_logger.fetch_audit_trail(limit=limit)

@app.get("/api/governance/hitl")
def get_hitl_queue_items():
    """Returns pending human-in-the-loop review items."""
    return hitl_moderator.get_pending_moderations()

@app.post("/api/governance/hitl/{entry_id}/action")
def take_hitl_action(entry_id: str, payload: HITLActionRequest):
    """Approves or rejects a flagged high-value/sensitive recommendation."""
    if payload.decision == "APPROVED":
        hitl_moderator.approve_item(entry_id, reviewed_by=payload.reviewed_by, notes=payload.notes)
    else:
        hitl_moderator.reject_item(entry_id, reviewed_by=payload.reviewed_by, notes=payload.notes)
    return {"status": "success", "entry_id": entry_id, "decision": payload.decision}

@app.get("/api/metrics/benchmark")
def get_model_benchmarks():
    """Calculates offline evaluation metrics across all 5 models."""
    return evaluator.evaluate_all_models()

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
