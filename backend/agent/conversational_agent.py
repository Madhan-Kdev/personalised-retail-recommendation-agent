"""
Conversational Recommendation Agent (GenAI / LLM Shopping Assistant)
Multi-turn conversational assistant providing interactive product discovery,
natural language explanation breakdown, comparative analysis, and budget search.
"""

from typing import List, Dict, Any, Optional
import re

class ConversationalRecommendationAgent:
    def __init__(self, hybrid_engine, explanation_gen, persona_synth):
        self.engine = hybrid_engine
        self.explanation_gen = explanation_gen
        self.persona_synth = persona_synth

    def chat(self, customer_id: str, message: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Processes customer natural language chat query and returns rich conversational response with item cards."""
        customer = self.engine.customer_map.get(customer_id)
        if not customer:
            return {
                "reply": "I couldn't locate your customer profile. Please select an active persona above.",
                "suggested_products": [],
                "suggested_followups": ["Show my personalized recommendations", "What is trending this season?"]
            }

        msg_lower = message.lower()
        catalog = self.engine.products
        catalog_map = self.engine.product_map

        suggested_products = []
        followups = []

        # Intent 1: Why did you recommend X?
        if "why" in msg_lower and ("recommend" in msg_lower or "suggest" in msg_lower or "this" in msg_lower):
            # Check if a specific product title or id was mentioned
            matched_prod = None
            for p in catalog:
                if p["title"].lower() in msg_lower or p["id"].lower() in msg_lower:
                    matched_prod = p
                    break

            if not matched_prod:
                # Default to top current recommendation
                recs = self.engine.recommend(customer, top_k=1)
                if recs:
                    matched_prod = recs[0]["product"]

            if matched_prod:
                rec_struct = {"product": matched_prod, "final_score": 0.92, "confidence": 0.88, "primary_driver": "Collaborative & Content Synergy"}
                exp = self.explanation_gen.generate_explanation(customer, rec_struct, catalog_map)
                
                reply = (
                    f"**Why we recommended the {matched_prod['title']}:**\n\n"
                    f"💡 *{exp['headline_explanation']}*\n\n"
                    f"**Key Supporting Signals:**\n" +
                    "\n".join([f"- {r}" for r in exp["key_reasons"]]) +
                    f"\n\n**Data Citations:**\n" +
                    "\n".join([f"- `{c}`" for c in exp["citations"]])
                )
                suggested_products = [matched_prod]
                followups = [
                    f"Show me alternatives to {matched_prod['brand']}",
                    "Compare this with similar items",
                    "Add this to my cart"
                ]
                return {
                    "reply": reply,
                    "suggested_products": suggested_products,
                    "suggested_followups": followups
                }

        # Intent 2: Budget search (e.g. "under $100", "under $50")
        price_match = re.search(r'under\s*\$?(\d+)', msg_lower)
        if price_match or "cheap" in msg_lower or "budget" in msg_lower:
            max_price = float(price_match.group(1)) if price_match else 100.0
            budget_items = [p for p in catalog if p["price"] <= max_price and p["id"] not in customer.get("past_purchases", [])]
            # Prioritize customer preferred categories
            budget_items.sort(key=lambda x: (x["category"] in customer.get("preferred_categories", []), x["rating"]), reverse=True)
            suggested_products = budget_items[:3]

            reply = (
                f"I found {len(suggested_products)} top-rated options tailored to your preferences under **${max_price:.2f}**:\n\n"
                + "\n".join([f"- **{p['title']}** (${p['price']}) — {p['rating']}★ ({p['category']})" for p in suggested_products]) +
                f"\n\nEach of these items matches your {customer.get('price_sensitivity', 'balanced')} budget profile."
            )
            followups = [
                "Show me options under $50",
                "Explain why the top one fits my profile",
                "View full recommendations feed"
            ]
            return {
                "reply": reply,
                "suggested_products": suggested_products,
                "suggested_followups": followups
            }

        # Intent 3: Comparison between items
        if "compare" in msg_lower or "difference" in msg_lower or "vs" in msg_lower:
            recs = self.engine.recommend(customer, top_k=2)
            if len(recs) >= 2:
                p1 = recs[0]["product"]
                p2 = recs[1]["product"]
                reply = (
                    f"### 🔍 Side-by-Side Product Comparison:\n\n"
                    f"**1. {p1['title']}** (${p1['price']})\n"
                    f"- Category: {p1['category']} ({p1['subcategory']})\n"
                    f"- Best For: {', '.join(p1.get('tags', [])[:3])}\n"
                    f"- Customer Rating: {p1['rating']}★ ({p1['review_count']} reviews)\n\n"
                    f"**2. {p2['title']}** (${p2['price']})\n"
                    f"- Category: {p2['category']} ({p2['subcategory']})\n"
                    f"- Best For: {', '.join(p2.get('tags', [])[:3])}\n"
                    f"- Customer Rating: {p2['rating']}★ ({p2['review_count']} reviews)\n\n"
                    f"**Recommendation Verdict**: If you prioritize direct synergy with your past purchases, go with the **{p1['title']}**."
                )
                suggested_products = [p1, p2]
                followups = [
                    f"Add {p1['brand']} to cart",
                    f"Add {p2['brand']} to cart",
                    "Show other categories"
                ]
                return {
                    "reply": reply,
                    "suggested_products": suggested_products,
                    "suggested_followups": followups
                }

        # Intent 4: Category / General Search (e.g., "winter", "running", "coffee", "audio", "skin")
        matched_items = []
        for p in catalog:
            combined = f"{p['title']} {p['category']} {p['subcategory']} {' '.join(p.get('tags', []))} {p['description']}".lower()
            # check any token match
            tokens = [t for t in msg_lower.split() if len(t) > 3]
            if any(t in combined for t in tokens):
                matched_items.append(p)

        if matched_items:
            # Sort by rating and category affinity
            matched_items.sort(key=lambda x: (x["category"] in customer.get("preferred_categories", []), x["rating"]), reverse=True)
            suggested_products = matched_items[:3]
            reply = (
                f"Here are the most relevant items I found matching your query:\n\n"
                + "\n".join([f"• **{p['title']}** (${p['price']}) — {p['rating']}★\n  *{p['description'][:90]}...*" for p in suggested_products])
            )
            followups = [
                "Why are these recommended for me?",
                "Are there any winter deals for these?",
                "Show items under $100"
            ]
            return {
                "reply": reply,
                "suggested_products": suggested_products,
                "suggested_followups": followups
            }

        # Default conversational assistance fallback
        recs = self.engine.recommend(customer, top_k=3)
        suggested_products = [r["product"] for r in recs]
        reply = (
            f"Hello {customer['name']}! As your AI Recommendation Agent, I have analyzed your shopping history and in-session interests. "
            f"Based on your affinity for **{', '.join(customer.get('preferred_categories', ['curated gear']))}**, "
            f"I have tailored several suggestions with full transparency.\n\n"
            f"How can I assist your shopping experience today?"
        )
        followups = [
            "Why did you recommend these specific items?",
            "Find top-rated products under $100",
            "What items are trending for Winter?"
        ]

        return {
            "reply": reply,
            "suggested_products": suggested_products,
            "suggested_followups": followups
        }
