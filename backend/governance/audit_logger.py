"""
Audit Logger Module
Provides immutable audit trail logging and retrieval for regulatory compliance and transparency.
"""

from typing import List, Dict, Any
from backend.data.database import log_audit_event, get_audit_logs

class RecommendationAuditLogger:
    def __init__(self):
        pass

    def log_recommendation_event(
        self,
        customer_id: str,
        recommended_product_ids: List[str],
        model: str,
        explanation: str,
        citations: List[str],
        confidence: float,
        latency_ms: float
    ) -> str:
        """Records a completed recommendation generation event."""
        return log_audit_event(
            customer_id=customer_id,
            product_ids=recommended_product_ids,
            model=model,
            explanation=explanation,
            citations=citations,
            confidence=confidence,
            latency_ms=latency_ms
        )

    def fetch_audit_trail(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches recent audit log entries."""
        return get_audit_logs(limit=limit)
