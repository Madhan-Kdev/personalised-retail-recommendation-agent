"""
Human-in-the-Loop (HITL) Moderation & Guardrails
Automatically intercepts sensitive or high-value recommendations for human review
and maintains an audit trail of operator decisions.
"""

from typing import List, Dict, Any, Optional
from backend.data.database import (
    get_hitl_queue, 
    add_hitl_entry, 
    resolve_hitl_entry, 
    get_product_by_id, 
    get_customer_by_id
)

class HITLModerator:
    def __init__(self, price_threshold: float = 500.0, confidence_threshold: float = 0.65):
        self.price_threshold = price_threshold
        self.confidence_threshold = confidence_threshold

    def inspect_and_intercept(self, customer_id: str, rec_item: Dict[str, Any]) -> bool:
        """Evaluates whether a recommendation must be flagged for Human-in-the-loop approval."""
        prod = rec_item["product"]
        confidence = rec_item.get("confidence", 1.0)

        flag_reasons = []
        if prod.get("price", 0.0) >= self.price_threshold:
            flag_reasons.append(f"High-Value Item (${prod['price']:.2f} >= ${self.price_threshold:.2f})")
        if prod.get("sensitive", False):
            flag_reasons.append("Sensitive Category Item")
        if confidence < self.confidence_threshold:
            flag_reasons.append(f"Low Model Confidence ({confidence:.2f} < {self.confidence_threshold:.2f})")

        if flag_reasons:
            reason_str = " | ".join(flag_reasons)
            # Avoid creating a duplicate PENDING entry for the same
            # customer/product if one already exists in the queue.
            existing_pending = any(
                item.get("customer_id") == customer_id
                and item.get("product_id") == prod["id"]
                and item.get("status") == "PENDING"
                for item in get_hitl_queue()
            )
            if not existing_pending:
                # Add to HITL queue in DB
                add_hitl_entry(customer_id, prod["id"], reason_str)
            return True
        return False

    def get_pending_moderations(self) -> List[Dict[str, Any]]:
        """Retrieves all pending moderation queue items with enriched product & customer info."""
        raw_items = get_hitl_queue()
        enriched = []
        for item in raw_items:
            prod = get_product_by_id(item["product_id"])
            cust = get_customer_by_id(item["customer_id"])
            enriched.append({
                **item,
                "product_title": prod["title"] if prod else "Unknown Product",
                "product_price": prod["price"] if prod else 0.0,
                "product_category": prod["category"] if prod else "N/A",
                "customer_name": cust["name"] if cust else "Unknown Customer",
                "customer_tier": cust["income_tier"] if cust else "N/A"
            })
        return enriched

    def approve_item(self, entry_id: str, reviewed_by: str = "Admin Specialist", notes: str = "Approved for customer display"):
        """Approves a flagged item for customer presentation."""
        resolve_hitl_entry(entry_id, "APPROVED", reviewed_by, notes)

    def reject_item(self, entry_id: str, reviewed_by: str = "Admin Specialist", notes: str = "Suppressed due to policy"):
        """Rejects and suppresses a flagged item."""
        resolve_hitl_entry(entry_id, "REJECTED", reviewed_by, notes)
