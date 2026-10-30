"""
Database abstraction and SQLite store for retail catalog, customer profiles,
live session telemetry, feedback loops, audit logs, and HITL moderation queue.
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.data.generator import (
    generate_full_catalog, 
    SAMPLE_CUSTOMERS, 
    generate_interaction_history, 
    get_seasonal_signals
)

DB_PATH = os.path.join(os.path.dirname(__file__), "retail_agent.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initializes schema and seeds initial data if database is empty."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Products Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT NOT NULL,
            brand TEXT NOT NULL,
            price REAL NOT NULL,
            rating REAL NOT NULL,
            review_count INTEGER NOT NULL,
            seasonal_affinity TEXT NOT NULL,
            tags TEXT NOT NULL,
            description TEXT NOT NULL,
            image_url TEXT,
            sensitive BOOLEAN DEFAULT 0,
            high_value BOOLEAN DEFAULT 0
        )
    """)

    # Customers Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            persona_title TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            location TEXT NOT NULL,
            income_tier TEXT NOT NULL,
            price_sensitivity TEXT NOT NULL,
            preferred_categories TEXT NOT NULL,
            bio TEXT NOT NULL,
            avatar TEXT,
            past_purchases TEXT NOT NULL,
            recent_browsed TEXT NOT NULL,
            cart TEXT NOT NULL,
            is_cold_start BOOLEAN DEFAULT 0
        )
    """)

    # Interactions Table (Telemetry & History)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_title TEXT NOT NULL,
            category TEXT NOT NULL,
            event_type TEXT NOT NULL,
            rating REAL,
            timestamp TEXT NOT NULL,
            dwell_time_sec INTEGER DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Audit Logs Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            recommended_product_ids TEXT NOT NULL,
            model_used TEXT NOT NULL,
            explanation TEXT NOT NULL,
            citations TEXT NOT NULL,
            confidence REAL NOT NULL,
            latency_ms REAL NOT NULL,
            feedback TEXT
        )
    """)

    # Human-in-the-Loop Moderation Queue
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hitl_moderation (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            reviewed_by TEXT,
            review_notes TEXT,
            decision_timestamp TEXT
        )
    """)

    conn.commit()

    # Check if products need seeding
    cur.execute("SELECT COUNT(*) as count FROM products")
    if cur.fetchone()["count"] == 0:
        print("[Database] Seeding initial products and customer profiles...")
        catalog = generate_full_catalog(40)
        for p in catalog:
            cur.execute("""
                INSERT INTO products (id, title, category, subcategory, brand, price, rating, review_count, seasonal_affinity, tags, description, image_url, sensitive, high_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["id"], p["title"], p["category"], p["subcategory"], p["brand"],
                p["price"], p["rating"], p["review_count"],
                json.dumps(p["seasonal_affinity"]), json.dumps(p["tags"]),
                p["description"], p.get("image_url", ""),
                1 if p.get("sensitive") else 0,
                1 if p.get("high_value") else 0
            ))

        for c in SAMPLE_CUSTOMERS:
            cur.execute("""
                INSERT INTO customers (id, name, persona_title, age, gender, location, income_tier, price_sensitivity, preferred_categories, bio, avatar, past_purchases, recent_browsed, cart, is_cold_start)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["id"], c["name"], c["persona_title"], c["age"], c["gender"],
                c["location"], c["income_tier"], c["price_sensitivity"],
                json.dumps(c["preferred_categories"]), c["bio"], c.get("avatar", ""),
                json.dumps(c.get("past_purchases", [])),
                json.dumps(c.get("recent_browsed", [])),
                json.dumps(c.get("cart", [])),
                1 if c.get("is_cold_start") else 0
            ))

        interactions = generate_interaction_history(SAMPLE_CUSTOMERS, catalog, 1200)
        for inter in interactions:
            cur.execute("""
                INSERT INTO interactions (id, customer_id, product_id, product_title, category, event_type, rating, timestamp, dwell_time_sec)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                inter["id"], inter["customer_id"], inter["product_id"], inter["product_title"],
                inter["category"], inter["event_type"], inter.get("rating"),
                inter["timestamp"], inter.get("dwell_time_sec", 0)
            ))

        conn.commit()
        print("[Database] Successfully seeded retail database.")

    conn.close()

# Data Access Helper Functions

def get_all_products() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    products = []
    for r in rows:
        p = dict(r)
        p["seasonal_affinity"] = json.loads(p["seasonal_affinity"])
        p["tags"] = json.loads(p["tags"])
        p["sensitive"] = bool(p["sensitive"])
        p["high_value"] = bool(p["high_value"])
        products.append(p)
    conn.close()
    return products

def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    p = dict(row)
    p["seasonal_affinity"] = json.loads(p["seasonal_affinity"])
    p["tags"] = json.loads(p["tags"])
    p["sensitive"] = bool(p["sensitive"])
    p["high_value"] = bool(p["high_value"])
    return p

def get_all_customers() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers")
    rows = cur.fetchall()
    customers = []
    for r in rows:
        c = dict(r)
        c["preferred_categories"] = json.loads(c["preferred_categories"])
        c["past_purchases"] = json.loads(c["past_purchases"])
        c["recent_browsed"] = json.loads(c["recent_browsed"])
        c["cart"] = json.loads(c["cart"])
        c["is_cold_start"] = bool(c["is_cold_start"])
        customers.append(c)
    conn.close()
    return customers

def get_customer_by_id(customer_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    c = dict(row)
    c["preferred_categories"] = json.loads(c["preferred_categories"])
    c["past_purchases"] = json.loads(c["past_purchases"])
    c["recent_browsed"] = json.loads(c["recent_browsed"])
    c["cart"] = json.loads(c["cart"])
    c["is_cold_start"] = bool(c["is_cold_start"])
    return c

def update_customer_session(customer_id: str, browsed: List[str] = None, cart: List[str] = None, purchases: List[str] = None):
    conn = get_db_connection()
    cur = conn.cursor()
    c = get_customer_by_id(customer_id)
    if not c:
        conn.close()
        return
    
    new_browsed = browsed if browsed is not None else c["recent_browsed"]
    new_cart = cart if cart is not None else c["cart"]
    new_purchases = purchases if purchases is not None else c["past_purchases"]

    cur.execute("""
        UPDATE customers 
        SET recent_browsed = ?, cart = ?, past_purchases = ?, is_cold_start = ?
        WHERE id = ?
    """, (
        json.dumps(new_browsed),
        json.dumps(new_cart),
        json.dumps(new_purchases),
        0 if len(new_purchases) > 0 else (1 if c["is_cold_start"] else 0),
        customer_id
    ))
    conn.commit()
    conn.close()

def log_interaction(customer_id: str, product_id: str, event_type: str, rating: Optional[float] = None, dwell_time_sec: int = 0):
    conn = get_db_connection()
    cur = conn.cursor()
    
    prod = get_product_by_id(product_id)
    prod_title = prod["title"] if prod else "Unknown"
    prod_cat = prod["category"] if prod else "General"

    event_id = f"INT-{int(datetime.now().timestamp()*1000)}"
    timestamp = datetime.now().isoformat()

    cur.execute("""
        INSERT INTO interactions (id, customer_id, product_id, product_title, category, event_type, rating, timestamp, dwell_time_sec)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (event_id, customer_id, product_id, prod_title, prod_cat, event_type, rating, timestamp, dwell_time_sec))

    conn.commit()
    conn.close()

def get_all_interactions() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM interactions ORDER BY timestamp DESC")
    rows = cur.fetchall()
    interactions = [dict(r) for r in rows]
    conn.close()
    return interactions

def log_audit_event(customer_id: str, product_ids: List[str], model: str, explanation: str, citations: List[str], confidence: float, latency_ms: float):
    conn = get_db_connection()
    cur = conn.cursor()
    audit_id = f"AUDIT-{int(datetime.now().timestamp()*1000)}"
    cur.execute("""
        INSERT INTO audit_logs (id, timestamp, customer_id, recommended_product_ids, model_used, explanation, citations, confidence, latency_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        audit_id, datetime.now().isoformat(), customer_id,
        json.dumps(product_ids), model, explanation, json.dumps(citations),
        confidence, latency_ms
    ))
    conn.commit()
    conn.close()
    return audit_id

def get_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    logs = []
    for r in rows:
        item = dict(r)
        item["recommended_product_ids"] = json.loads(item["recommended_product_ids"])
        item["citations"] = json.loads(item["citations"])
        logs.append(item)
    conn.close()
    return logs

def add_hitl_entry(customer_id: str, product_id: str, reason: str):
    conn = get_db_connection()
    cur = conn.cursor()
    hitl_id = f"HITL-{int(datetime.now().timestamp()*1000)}"
    cur.execute("""
        INSERT INTO hitl_moderation (id, timestamp, customer_id, product_id, reason, status)
        VALUES (?, ?, ?, ?, ?, 'PENDING')
    """, (hitl_id, datetime.now().isoformat(), customer_id, product_id, reason))
    conn.commit()
    conn.close()
    return hitl_id

def get_hitl_queue() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM hitl_moderation ORDER BY timestamp DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def resolve_hitl_entry(entry_id: str, decision: str, reviewed_by: str = "Admin", notes: str = ""):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE hitl_moderation 
        SET status = ?, reviewed_by = ?, review_notes = ?, decision_timestamp = ?
        WHERE id = ?
    """, (decision, reviewed_by, notes, datetime.now().isoformat(), entry_id))
    conn.commit()
    conn.close()
