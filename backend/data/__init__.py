"""
Data module initialization.
"""
from backend.data.database import (
    init_database,
    get_all_products,
    get_product_by_id,
    get_all_customers,
    get_customer_by_id,
    update_customer_session,
    log_interaction,
    get_all_interactions,
    log_audit_event,
    get_audit_logs,
    add_hitl_entry,
    get_hitl_queue,
    resolve_hitl_entry
)
from backend.data.generator import get_seasonal_signals
