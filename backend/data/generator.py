"""
Realistic Retail Dataset Generator
Produces high-quality retail catalog data, diverse customer personas, 
interaction logs (views, clicks, carts, purchases, ratings), and seasonal trend signals.
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Seed for reproducibility
random.seed(42)

CATEGORIES = [
    "Electronics & Audio",
    "Fitness & Outdoors",
    "Apparel & Fashion",
    "Home & Kitchen",
    "Beauty & Skincare",
    "Gourmet & Coffee"
]

SEASONS = ["Winter", "Summer", "Spring", "Holiday/Festive", "All-Season"]

SAMPLE_PRODUCTS = [
    # Electronics & Audio
    {
        "id": "PROD-001",
        "title": "AeroBeat Pro Wireless Noise-Canceling Headphones",
        "category": "Electronics & Audio",
        "subcategory": "Headphones",
        "brand": "SonicWave",
        "price": 249.99,
        "rating": 4.8,
        "review_count": 342,
        "seasonal_affinity": ["Holiday/Festive", "All-Season"],
        "tags": ["audio", "bluetooth", "noise-canceling", "travel", "bass", "premium"],
        "description": "High-fidelity wireless headphones with adaptive active noise cancellation, 40-hour battery life, and spatial audio support.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-002",
        "title": "NovaSmart 4K Ultra-Portable Projector",
        "category": "Electronics & Audio",
        "subcategory": "Home Theater",
        "brand": "LuminaVision",
        "price": 599.99,
        "rating": 4.6,
        "review_count": 128,
        "seasonal_affinity": ["Winter", "Holiday/Festive"],
        "tags": ["projector", "4k", "smart-home", "cinema", "wireless", "premium"],
        "description": "Compact smart projector with built-in streaming apps, 120-inch projection capability, and Dolby audio.",
        "image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&q=80",
        "sensitive": False,
        "high_value": True
    },
    {
        "id": "PROD-003",
        "title": "PulseVibe Ergonomic Mechanical Keyboard",
        "category": "Electronics & Audio",
        "subcategory": "Computer Accessories",
        "brand": "KeyForge",
        "price": 129.99,
        "rating": 4.7,
        "review_count": 512,
        "seasonal_affinity": ["All-Season"],
        "tags": ["keyboard", "mechanical", "ergonomic", "rgb", "productivity", "office"],
        "description": "Hot-swappable tactile switches with wireless Bluetooth 5.2 and customized wrist cushion.",
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-004",
        "title": "ZenCharge Qi2 3-in-1 Fast Wireless Charging Station",
        "category": "Electronics & Audio",
        "subcategory": "Charging",
        "brand": "SonicWave",
        "price": 69.99,
        "rating": 4.5,
        "review_count": 289,
        "seasonal_affinity": ["Holiday/Festive", "All-Season"],
        "tags": ["charging", "wireless", "desk", "iphone", "apple-watch", "minimalist"],
        "description": "Magnetic 15W high-speed charging dock for smartphone, earbuds, and smartwatch.",
        "image_url": "https://images.unsplash.com/photo-1622445262464-84b1456045b6?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },

    # Fitness & Outdoors
    {
        "id": "PROD-005",
        "title": "ApexGrip Carbon-Plated Marathon Running Shoes",
        "category": "Fitness & Outdoors",
        "subcategory": "Footwear",
        "brand": "StrideMax",
        "price": 189.99,
        "rating": 4.9,
        "review_count": 480,
        "seasonal_affinity": ["Spring", "Summer", "All-Season"],
        "tags": ["running", "marathon", "carbon-plate", "breathable", "lightweight", "endurance"],
        "description": "Ultralight marathon racing shoes with dynamic carbon fiber propulsion plate and responsive energy-return foam.",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-006",
        "title": "ThermoHydrate Smart Vacuum Water Bottle 1L",
        "category": "Fitness & Outdoors",
        "subcategory": "Hydration",
        "brand": "HydroPeak",
        "price": 44.99,
        "rating": 4.7,
        "review_count": 760,
        "seasonal_affinity": ["Summer", "All-Season"],
        "tags": ["hydration", "gym", "hiking", "insulated", "bpa-free", "eco-friendly"],
        "description": "Double-wall stainless steel bottle that keeps beverages ice-cold for 36 hours with integrated sip reminder LED.",
        "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-007",
        "title": "SummitTrek 65L All-Weather Tactical Backpack",
        "category": "Fitness & Outdoors",
        "subcategory": "Camping & Hiking",
        "brand": "TerraQuest",
        "price": 179.99,
        "rating": 4.8,
        "review_count": 215,
        "seasonal_affinity": ["Spring", "Summer"],
        "tags": ["backpack", "hiking", "camping", "waterproof", "ergonomic", "outdoors"],
        "description": "Ripstop waterproof expedition pack with adjustable torso suspension and integrated rain cover.",
        "image_url": "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-008",
        "title": "ProFlow Moisture-Wicking Performance Compression Socks (3-Pack)",
        "category": "Fitness & Outdoors",
        "subcategory": "Athletic Wear",
        "brand": "StrideMax",
        "price": 29.99,
        "rating": 4.6,
        "review_count": 640,
        "seasonal_affinity": ["All-Season"],
        "tags": ["running", "compression", "socks", "recovery", "breathable", "gym"],
        "description": "Graduated compression socks designed for muscle fatigue reduction and moisture management during distance runs.",
        "image_url": "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },

    # Apparel & Fashion
    {
        "id": "PROD-009",
        "title": "NordicShield Arctic Goose Down Parka",
        "category": "Apparel & Fashion",
        "subcategory": "Outerwear",
        "brand": "FjordLiving",
        "price": 389.99,
        "rating": 4.8,
        "review_count": 310,
        "seasonal_affinity": ["Winter", "Holiday/Festive"],
        "tags": ["winter", "jacket", "parka", "warm", "waterproof", "thermal", "fashion"],
        "description": "Heavy-duty windproof arctic parka insulated with 800-fill responsible down, fleece-lined storm pockets, and faux-fur hood.",
        "image_url": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-010",
        "title": "EcoWeave 100% Organic Linen Summer Shirt",
        "category": "Apparel & Fashion",
        "subcategory": "Shirts",
        "brand": "VerdeStyle",
        "price": 74.99,
        "rating": 4.5,
        "review_count": 195,
        "seasonal_affinity": ["Summer", "Spring"],
        "tags": ["linen", "summer", "sustainable", "organic", "breathable", "casual"],
        "description": "Relaxed fit lightweight shirt crafted from sustainably harvested European flax linen.",
        "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-011",
        "title": "AuraCashmere Oversized Ribbed Turtleneck Sweater",
        "category": "Apparel & Fashion",
        "subcategory": "Knitwear",
        "brand": "FjordLiving",
        "price": 219.99,
        "rating": 4.9,
        "review_count": 182,
        "seasonal_affinity": ["Winter", "Holiday/Festive"],
        "tags": ["cashmere", "sweater", "cozy", "luxury", "winter", "fashion"],
        "description": "Ultra-soft Mongolian grade-A cashmere sweater with relaxed mock neck and ribbed hem.",
        "image_url": "https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-012",
        "title": "LuxeCraft Italian Full-Grain Leather Briefcase",
        "category": "Apparel & Fashion",
        "subcategory": "Bags & Leather",
        "brand": "ArtisanAtelier",
        "price": 649.99,
        "rating": 4.9,
        "review_count": 89,
        "seasonal_affinity": ["All-Season", "Holiday/Festive"],
        "tags": ["leather", "luxury", "briefcase", "executive", "handcrafted", "office"],
        "description": "Handcrafted vegetable-tanned full-grain leather business briefcase with brass hardware and 16-inch laptop compartment.",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80",
        "sensitive": False,
        "high_value": True
    },

    # Home & Kitchen
    {
        "id": "PROD-013",
        "title": "BaristaTouch Precision Espresso Machine & Grinder",
        "category": "Home & Kitchen",
        "subcategory": "Coffee Appliances",
        "brand": "AromaCraft",
        "price": 699.99,
        "rating": 4.9,
        "review_count": 420,
        "seasonal_affinity": ["All-Season", "Holiday/Festive"],
        "tags": ["espresso", "coffee", "barista", "kitchen", "gourmet", "luxury"],
        "description": "Commercial-grade PID thermal heating with conical burr grinder, microfoam steam wand, and touchscreen interface.",
        "image_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500&q=80",
        "sensitive": False,
        "high_value": True
    },
    {
        "id": "PROD-014",
        "title": "CastIron Chef 6-Quart Enameled Dutch Oven",
        "category": "Home & Kitchen",
        "subcategory": "Cookware",
        "brand": "CulinaryForge",
        "price": 149.99,
        "rating": 4.8,
        "review_count": 590,
        "seasonal_affinity": ["Winter", "Holiday/Festive"],
        "tags": ["cookware", "dutch-oven", "baking", "stew", "kitchen", "durable"],
        "description": "Heavy-duty cast iron with chip-resistant glossy enamel finish, ideal for slow braises, sourdough bread, and soups.",
        "image_url": "https://images.unsplash.com/photo-1584990347449-399066606f75?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-015",
        "title": "PureAir HEPA 13 Smart Air Purifier & Ionizer",
        "category": "Home & Kitchen",
        "subcategory": "Home Air",
        "brand": "LuminaVision",
        "price": 189.99,
        "rating": 4.7,
        "review_count": 378,
        "seasonal_affinity": ["Spring", "All-Season"],
        "tags": ["air-purifier", "hepa", "allergies", "smart-home", "clean-air", "quiet"],
        "description": "Filters 99.97% of dust, pet dander, allergens, and odors with real-time PM2.5 air quality laser sensor.",
        "image_url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-016",
        "title": "LoomLuxe 1000-Thread-Count Egyptian Cotton Bedding Set",
        "category": "Home & Kitchen",
        "subcategory": "Bedding",
        "brand": "VerdeStyle",
        "price": 159.99,
        "rating": 4.8,
        "review_count": 290,
        "seasonal_affinity": ["All-Season"],
        "tags": ["bedding", "cotton", "sheets", "luxury", "sleep", "cozy"],
        "description": "Silky sateen weave crafted from long-staple certified Egyptian cotton for temperature-regulated luxury sleep.",
        "image_url": "https://images.unsplash.com/photo-1616046229478-9901c5536a45?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },

    # Beauty & Skincare
    {
        "id": "PROD-017",
        "title": "BotanicalGlow Triple-Hyaluronic Hydrating Serum",
        "category": "Beauty & Skincare",
        "subcategory": "Serums",
        "brand": "NaturaBotanics",
        "price": 58.00,
        "rating": 4.8,
        "review_count": 680,
        "seasonal_affinity": ["Winter", "All-Season"],
        "tags": ["skincare", "serum", "hyaluronic-acid", "hydrating", "vegan", "anti-aging"],
        "description": "Deeply plumping multi-molecular weight hyaluronic acid enriched with snow mushroom and niacinamide.",
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-018",
        "title": "DermaRevive Red Light Therapy LED Face Mask",
        "category": "Beauty & Skincare",
        "subcategory": "Beauty Tech",
        "brand": "NaturaBotanics",
        "price": 320.00,
        "rating": 4.7,
        "review_count": 145,
        "seasonal_affinity": ["All-Season", "Holiday/Festive"],
        "tags": ["skincare", "led-mask", "red-light", "anti-aging", "collagen", "tech"],
        "description": "Clinical-grade dual wavelength (633nm red & 830nm near-infrared) flexible silicone mask for collagen renewal.",
        "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-019",
        "title": "SolShield Mineral Zinc Oxide SPF 50+ Invisible Sunscreen",
        "category": "Beauty & Skincare",
        "subcategory": "Sun Protection",
        "brand": "NaturaBotanics",
        "price": 34.00,
        "rating": 4.6,
        "review_count": 510,
        "seasonal_affinity": ["Summer", "Spring"],
        "tags": ["sunscreen", "spf50", "mineral", "reef-safe", "summer", "skincare"],
        "description": "Ultra-sheer broad spectrum mineral sunscreen with non-greasy matte finish and antioxidant blue light protection.",
        "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },

    # Gourmet & Coffee
    {
        "id": "PROD-020",
        "title": "Single-Origin Ethiopian Yirgacheffe Specialty Coffee Beans (2lb)",
        "category": "Gourmet & Coffee",
        "subcategory": "Coffee Beans",
        "brand": "AromaCraft",
        "price": 38.50,
        "rating": 4.9,
        "review_count": 890,
        "seasonal_affinity": ["All-Season"],
        "tags": ["coffee", "single-origin", "espresso", "beans", "gourmet", "ethiopia"],
        "description": "Micro-lot naturally processed beans with vibrant tasting notes of jasmine, bergamot, and sweet blueberry.",
        "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-021",
        "title": "Ceremonial Grade Uji Matcha Green Tea Powder (100g)",
        "category": "Gourmet & Coffee",
        "subcategory": "Tea & Matcha",
        "brand": "ArtisanAtelier",
        "price": 42.00,
        "rating": 4.8,
        "review_count": 330,
        "seasonal_affinity": ["All-Season", "Spring"],
        "tags": ["matcha", "tea", "antioxidant", "japanese", "organic", "wellness"],
        "description": "First-harvest stone-ground ceremonial matcha from Kyoto, Japan with vibrant jade color and rich umami sweetness.",
        "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&q=80",
        "sensitive": False,
        "high_value": False
    },
    {
        "id": "PROD-022",
        "title": "Artisanal White Truffle Infused Extra Virgin Olive Oil (250ml)",
        "category": "Gourmet & Coffee",
        "subcategory": "Pantry & Oils",
        "brand": "CulinaryForge",
        "price": 48.00,
        "rating": 4.7,
        "review_count": 175,
        "seasonal_affinity": ["Holiday/Festive", "Winter"],
        "tags": ["truffle", "olive-oil", "gourmet", "cooking", "gift", "culinary"],
        "description": "First cold-pressed Italian olive oil steeped with genuine Alba white truffles for finishing pasta, meats, and risottos.",
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80",
        "sensitive": False,
        "high_value": False
    }
]

SAMPLE_CUSTOMERS = [
    {
        "id": "CUST-001",
        "name": "Maya Lin",
        "persona_title": "Marathon Runner & Fitness Enthusiast",
        "age": 29,
        "gender": "Female",
        "location": "Seattle, WA",
        "income_tier": "High",
        "price_sensitivity": "Low",
        "preferred_categories": ["Fitness & Outdoors", "Gourmet & Coffee", "Beauty & Skincare"],
        "bio": "Competitive distance runner preparing for autumn marathon. Values high-performance gear, rapid recovery, and clean nutrition.",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&q=80",
        "past_purchases": ["PROD-005", "PROD-006", "PROD-020"],
        "recent_browsed": ["PROD-008", "PROD-019", "PROD-007"],
        "cart": ["PROD-008"],
        "is_cold_start": False
    },
    {
        "id": "CUST-002",
        "name": "Liam Sterling",
        "persona_title": "Audiophile & Smart-Home Technologist",
        "age": 34,
        "gender": "Male",
        "location": "Austin, TX",
        "income_tier": "High",
        "price_sensitivity": "Medium",
        "preferred_categories": ["Electronics & Audio", "Home & Kitchen"],
        "bio": "Software architect and music producer. Loves smart home automation, high-fidelity acoustics, and minimalist productivity setups.",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&q=80",
        "past_purchases": ["PROD-001", "PROD-003", "PROD-004"],
        "recent_browsed": ["PROD-002", "PROD-015"],
        "cart": [],
        "is_cold_start": False
    },
    {
        "id": "CUST-003",
        "name": "Elena Rostova",
        "persona_title": "Eco-Conscious Fashion & Nordic Aesthetic",
        "age": 27,
        "gender": "Female",
        "location": "Boston, MA",
        "income_tier": "Medium",
        "price_sensitivity": "Medium",
        "preferred_categories": ["Apparel & Fashion", "Beauty & Skincare", "Home & Kitchen"],
        "bio": "Sustainable design consultant focused on timeless wardrobe capsules, organic skincare, and cozy hygge home decor.",
        "avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&q=80",
        "past_purchases": ["PROD-010", "PROD-017", "PROD-016"],
        "recent_browsed": ["PROD-009", "PROD-011", "PROD-018"],
        "cart": ["PROD-011"],
        "is_cold_start": False
    },
    {
        "id": "CUST-004",
        "name": "David Chen",
        "persona_title": "Artisanal Home Chef & Coffee Connoisseur",
        "age": 42,
        "gender": "Male",
        "location": "San Francisco, CA",
        "income_tier": "High",
        "price_sensitivity": "Low",
        "preferred_categories": ["Home & Kitchen", "Gourmet & Coffee"],
        "bio": "Culinary enthusiast who hosts weekend tasting dinners. Obsessed with specialty espresso roasts, cast iron techniques, and rare pantry staples.",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&q=80",
        "past_purchases": ["PROD-013", "PROD-020", "PROD-022"],
        "recent_browsed": ["PROD-014", "PROD-021"],
        "cart": ["PROD-014"],
        "is_cold_start": False
    },
    {
        "id": "CUST-005",
        "name": "Sophia Martinez",
        "persona_title": "New Explorer / Cold-Start Visitor",
        "age": 23,
        "gender": "Female",
        "location": "Chicago, IL",
        "income_tier": "Medium",
        "price_sensitivity": "High",
        "preferred_categories": ["Electronics & Audio", "Apparel & Fashion"],
        "bio": "New customer browsing trending college & lifestyle gadgets. No prior purchase history on the platform.",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&q=80",
        "past_purchases": [],
        "recent_browsed": ["PROD-003", "PROD-004"],
        "cart": [],
        "is_cold_start": True
    },
    {
        "id": "CUST-006",
        "name": "Marcus Vance",
        "persona_title": "Executive Professional & Luxury Connoisseur",
        "age": 48,
        "gender": "Male",
        "location": "New York, NY",
        "income_tier": "Ultra-High",
        "price_sensitivity": "Low",
        "preferred_categories": ["Apparel & Fashion", "Electronics & Audio", "Gourmet & Coffee"],
        "bio": "Managing director who travels between NYC and London. Seeks heritage craftsmanship, executive travel goods, and luxury tech.",
        "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&q=80",
        "past_purchases": ["PROD-012", "PROD-001", "PROD-022"],
        "recent_browsed": ["PROD-002", "PROD-013"],
        "cart": [],
        "is_cold_start": False
    }
]

def generate_full_catalog(target_count: int = 40) -> List[Dict[str, Any]]:
    """Expands sample catalog into a full rich product database."""
    catalog = list(SAMPLE_PRODUCTS)
    brands = {
        "Electronics & Audio": ["SonicWave", "LuminaVision", "KeyForge", "ApexAudio", "OmniTech"],
        "Fitness & Outdoors": ["StrideMax", "HydroPeak", "TerraQuest", "VelocityFit", "AlpinePro"],
        "Apparel & Fashion": ["FjordLiving", "VerdeStyle", "ArtisanAtelier", "UrbanKnit", "SilkLine"],
        "Home & Kitchen": ["AromaCraft", "CulinaryForge", "LuminaVision", "CasaBella", "ChefPrecision"],
        "Beauty & Skincare": ["NaturaBotanics", "DermaGlow", "PureEssence", "AuraSkin"],
        "Gourmet & Coffee": ["AromaCraft", "ArtisanAtelier", "CulinaryForge", "TerroirRoasters"]
    }

    subcategories = {
        "Electronics & Audio": ["Smart Audio", "Wearables", "Desk Setup", "Smart Display", "Gaming Acc"],
        "Fitness & Outdoors": ["Trail Gear", "Recovery Tools", "Yoga & Balance", "Smart Fitness", "Outdoor Apparel"],
        "Apparel & Fashion": ["Casual Wear", "Accessories", "Footwear", "Seasonal Layering", "Activewear"],
        "Home & Kitchen": ["Smart Living", "Espresso Tools", "Culinary Cutlery", "Ambient Lighting", "Storage"],
        "Beauty & Skincare": ["Cleansers", "Moisturizers", "Sun Care", "Facial Tools", "Night Treatments"],
        "Gourmet & Coffee": ["Single-Origin Beans", "Pour-Over Gear", "Specialty Salts", "Infused Syrups", "Artisanal Treats"]
    }

    existing_count = len(catalog)
    for i in range(existing_count + 1, target_count + 1):
        cat = random.choice(CATEGORIES)
        brand = random.choice(brands[cat])
        subcat = random.choice(subcategories[cat])
        price = round(random.uniform(25.0, 450.0), 2)
        rating = round(random.uniform(4.2, 5.0), 1)
        review_count = random.randint(30, 950)
        season = random.choice(SEASONS)

        title = f"{brand} {subcat} Edition {i}"
        tags = [cat.lower().replace("&", "").split()[0], subcat.lower().replace(" ", "-"), brand.lower(), "premium"]
        
        catalog.append({
            "id": f"PROD-{i:03d}",
            "title": title,
            "category": cat,
            "subcategory": subcat,
            "brand": brand,
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "seasonal_affinity": [season, "All-Season"] if season != "All-Season" else ["All-Season"],
            "tags": tags,
            "description": f"Engineered by {brand} for optimal performance, elegance, and durability in {cat.lower()}.",
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80",
            "sensitive": False,
            "high_value": price >= 500.0
        })

    return catalog

def generate_interaction_history(customers: List[Dict[str, Any]], products: List[Dict[str, Any]], count: int = 1200) -> List[Dict[str, Any]]:
    """Generates synthetic historical user-item interactions with realistic bias patterns."""
    interactions = []
    interaction_types = ["view", "click", "add_to_cart", "purchase", "rating"]
    weights = [0.45, 0.25, 0.15, 0.10, 0.05]

    product_map = {p["id"]: p for p in products}

    # First ingest explicit past purchases from customer personas
    event_id = 1
    base_time = datetime.now() - timedelta(days=90)

    for cust in customers:
        for p_id in cust.get("past_purchases", []):
            if p_id in product_map:
                p = product_map[p_id]
                t_offset = random.randint(5, 75)
                interactions.append({
                    "id": f"INT-{event_id:05d}",
                    "customer_id": cust["id"],
                    "product_id": p_id,
                    "product_title": p["title"],
                    "category": p["category"],
                    "event_type": "purchase",
                    "rating": random.choice([4.0, 5.0, 5.0]),
                    "timestamp": (base_time + timedelta(days=t_offset)).isoformat(),
                    "dwell_time_sec": random.randint(45, 240)
                })
                event_id += 1

    # Ingest synthetic interactions
    while len(interactions) < count:
        cust = random.choice(customers)
        if cust.get("is_cold_start") and random.random() > 0.1:
            continue

        # Affinity selection: 70% probability to pick from preferred categories
        if random.random() < 0.70 and cust.get("preferred_categories"):
            pref_cats = cust["preferred_categories"]
            matching_prods = [p for p in products if p["category"] in pref_cats]
            p = random.choice(matching_prods) if matching_prods else random.choice(products)
        else:
            p = random.choice(products)

        event = random.choices(interaction_types, weights=weights)[0]
        rating_val = None
        if event == "purchase":
            rating_val = random.choice([4.0, 4.5, 5.0, 5.0])
        elif event == "rating":
            rating_val = random.choice([3.0, 4.0, 4.5, 5.0])

        t_days = random.randint(1, 90)
        interactions.append({
            "id": f"INT-{event_id:05d}",
            "customer_id": cust["id"],
            "product_id": p["id"],
            "product_title": p["title"],
            "category": p["category"],
            "event_type": event,
            "rating": rating_val,
            "timestamp": (base_time + timedelta(days=t_days, hours=random.randint(0, 23))).isoformat(),
            "dwell_time_sec": random.randint(10, 300)
        })
        event_id += 1

    return interactions

def get_seasonal_signals() -> Dict[str, Any]:
    """Returns current retail seasonality trends, promotion multipliers, and category boosts."""
    return {
        "current_season": "Winter",
        "active_campaign": "Winter Warmth & New Year Wellness Fest",
        "category_boosts": {
            "Apparel & Fashion": 1.35,
            "Fitness & Outdoors": 1.25,
            "Home & Kitchen": 1.20,
            "Electronics & Audio": 1.15,
            "Beauty & Skincare": 1.30,
            "Gourmet & Coffee": 1.20
        },
        "trending_keywords": [
            "arctic parka", "cashmere", "marathon training", 
            "espresso", "hyaluronic serum", "noise-canceling", "air purifier"
        ]
    }
