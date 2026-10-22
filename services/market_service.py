"""
Market Price Estimation Service
Provides commodity market prices across major Mandis (APMCs),
7-day price movement trends, and an intelligent "When & Where to Sell" advisory engine.
"""

COMMODITIES_MARKET = {
    "wheat": {
        "id": "wheat",
        "name": "Wheat (Mill Quality / Lokwan)",
        "category": "Cereals",
        "unit": "Quintal (100 kg)",
        "modal_price": 2680,
        "min_price": 2520,
        "max_price": 2840,
        "change_pct": 1.5,
        "trend": "up",
        "history_7d": [2610, 2625, 2630, 2650, 2660, 2670, 2680],
        "primary_mandi": "Khanna (Punjab)",
        "nearby_mandis": [
            {"name": "Khanna Mandi", "distance_km": 15, "price": 2680, "transport_cost_qtl": 25},
            {"name": "Ludhiana APMC", "distance_km": 28, "price": 2720, "transport_cost_qtl": 45},
            {"name": "Karnal Mandi", "distance_km": 95, "price": 2760, "transport_cost_qtl": 110}
        ],
        "supply_status": "Moderate Arrivals",
        "advisory": "Government procurement targets and robust flour mill demand are supporting prices. Holding for 2-3 weeks recommended as private millers compete for premium lots."
    },
    "rice_basmati": {
        "id": "rice_basmati",
        "name": "Paddy (Basmati 1121)",
        "category": "Cereals",
        "unit": "Quintal (100 kg)",
        "modal_price": 4350,
        "min_price": 3950,
        "max_price": 4650,
        "change_pct": 2.8,
        "trend": "up",
        "history_7d": [4150, 4200, 4220, 4280, 4310, 4330, 4350],
        "primary_mandi": "Taraori (Haryana)",
        "nearby_mandis": [
            {"name": "Taraori APMC", "distance_km": 18, "price": 4350, "transport_cost_qtl": 30},
            {"name": "Karnal Yard", "distance_km": 25, "price": 4390, "transport_cost_qtl": 40},
            {"name": "Narela Mandi", "distance_km": 80, "price": 4480, "transport_cost_qtl": 95}
        ],
        "supply_status": "High Export Inquiries",
        "advisory": "Strong Gulf and European export quotas are driving aggressive bidding. Stagger sales over the next month to capture premium price peaks."
    },
    "paddy_common": {
        "id": "paddy_common",
        "name": "Paddy (Common / PR-126)",
        "category": "Cereals",
        "unit": "Quintal (100 kg)",
        "modal_price": 2320,
        "min_price": 2250,
        "max_price": 2380,
        "change_pct": 0.4,
        "trend": "stable",
        "history_7d": [2300, 2305, 2310, 2315, 2315, 2320, 2320],
        "primary_mandi": "Rajpura (Punjab)",
        "nearby_mandis": [
            {"name": "Rajpura Yard", "distance_km": 12, "price": 2320, "transport_cost_qtl": 20},
            {"name": "Patiala Mandi", "distance_km": 30, "price": 2340, "transport_cost_qtl": 42}
        ],
        "supply_status": "Heavy Government MSP Procurement",
        "advisory": "Prices are closely pegged to official MSP. Sell directly to designated procurement centers with verified moisture under 17%."
    },
    "soybean": {
        "id": "soybean",
        "name": "Soybean (Yellow)",
        "category": "Oilseeds",
        "unit": "Quintal (100 kg)",
        "modal_price": 4680,
        "min_price": 4450,
        "max_price": 4900,
        "change_pct": -0.8,
        "trend": "down",
        "history_7d": [4760, 4740, 4720, 4710, 4700, 4690, 4680],
        "primary_mandi": "Indore (Madhya Pradesh)",
        "nearby_mandis": [
            {"name": "Indore Chhawani", "distance_km": 10, "price": 4680, "transport_cost_qtl": 20},
            {"name": "Ujjain Mandi", "distance_km": 55, "price": 4710, "transport_cost_qtl": 65},
            {"name": "Dewas Mandi", "distance_km": 38, "price": 4690, "transport_cost_qtl": 48}
        ],
        "supply_status": "Heavy Domestic Arrivals",
        "advisory": "Crush margins are thin due to cheap imported palm oil. Recommend selling 50% of stock now to hedge against further downward pressure."
    },
    "mustard": {
        "id": "mustard",
        "name": "Mustard Seed (Sarson 42% Oil)",
        "category": "Oilseeds",
        "unit": "Quintal (100 kg)",
        "modal_price": 5750,
        "min_price": 5500,
        "max_price": 6050,
        "change_pct": 1.9,
        "trend": "up",
        "history_7d": [5610, 5640, 5680, 5700, 5720, 5735, 5750],
        "primary_mandi": "Jaipur (Rajasthan)",
        "nearby_mandis": [
            {"name": "Jaipur APMC", "distance_km": 14, "price": 5750, "transport_cost_qtl": 25},
            {"name": "Alwar Mandi", "distance_km": 110, "price": 5840, "transport_cost_qtl": 105},
            {"name": "Bharatpur Mandi", "distance_km": 140, "price": 5890, "transport_cost_qtl": 130}
        ],
        "supply_status": "Tight Physical Stock in Mills",
        "advisory": "Oil millers are stocking up. Prices projected to climb further by 3-5% over next month. Favorable to hold in dry storage."
    },
    "cotton": {
        "id": "cotton",
        "name": "Cotton (Medium Staple Shankar-6)",
        "category": "Cash Crops",
        "unit": "Quintal (100 kg)",
        "modal_price": 7250,
        "min_price": 6800,
        "max_price": 7600,
        "change_pct": 2.1,
        "trend": "up",
        "history_7d": [7050, 7100, 7120, 7160, 7200, 7220, 7250],
        "primary_mandi": "Rajkot (Gujarat)",
        "nearby_mandis": [
            {"name": "Rajkot Yard", "distance_km": 20, "price": 7250, "transport_cost_qtl": 35},
            {"name": "Surendranagar", "distance_km": 85, "price": 7360, "transport_cost_qtl": 90}
        ],
        "supply_status": "Active Spinning Mill Demand",
        "advisory": "Spinning units are actively rebuilding raw cotton inventory. Hold clean, dry lots for optimum bargaining power."
    },
    "chickpea": {
        "id": "chickpea",
        "name": "Chickpea / Chana (Desi)",
        "category": "Pulses",
        "unit": "Quintal (100 kg)",
        "modal_price": 5950,
        "min_price": 5700,
        "max_price": 6250,
        "change_pct": 0.8,
        "trend": "up",
        "history_7d": [5880, 5900, 5910, 5925, 5930, 5940, 5950],
        "primary_mandi": "Bikaner (Rajasthan)",
        "nearby_mandis": [
            {"name": "Bikaner Mandi", "distance_km": 15, "price": 5950, "transport_cost_qtl": 25},
            {"name": "Neemuch Mandi", "distance_km": 220, "price": 6120, "transport_cost_qtl": 180}
        ],
        "supply_status": "Steady Festival Offtake",
        "advisory": "Pulse processing mills have steady orders. Prices likely to remain resilient; sell in gradual tranches."
    },
    "tomato": {
        "id": "tomato",
        "name": "Tomato (Hybrid Red)",
        "category": "Vegetables",
        "unit": "Crate (25 kg)",
        "modal_price": 420,  # ~16.8 / kg
        "min_price": 350,
        "max_price": 520,
        "change_pct": 4.5,
        "trend": "up",
        "history_7d": [380, 390, 395, 400, 410, 415, 420],
        "primary_mandi": "Nashik (Maharashtra)",
        "nearby_mandis": [
            {"name": "Pimpalgaon (Nashik)", "distance_km": 25, "price": 420, "transport_cost_qtl": 20},
            {"name": "Vashi APMC (Mumbai)", "distance_km": 165, "price": 490, "transport_cost_qtl": 60}
        ],
        "supply_status": "Moderate Supplies; High Urban Demand",
        "advisory": "Perishable commodity. Do not hold without cold storage. Sending graded crates to metropolitan wholesale markets yields 15% higher net realization."
    },
    "onion": {
        "id": "onion",
        "name": "Onion (Nashik Red / Garwa)",
        "category": "Vegetables",
        "unit": "Quintal (100 kg)",
        "modal_price": 2150,
        "min_price": 1850,
        "max_price": 2450,
        "change_pct": -1.4,
        "trend": "down",
        "history_7d": [2240, 2220, 2200, 2180, 2170, 2160, 2150],
        "primary_mandi": "Lasalgaon (Maharashtra)",
        "nearby_mandis": [
            {"name": "Lasalgaon APMC", "distance_km": 18, "price": 2150, "transport_cost_qtl": 25},
            {"name": "Yeola Mandi", "distance_km": 32, "price": 2180, "transport_cost_qtl": 38},
            {"name": "Azadpur (Delhi)", "distance_km": 1150, "price": 2650, "transport_cost_qtl": 450}
        ],
        "supply_status": "Heavy Seasonal Arrivals",
        "advisory": "Fresh arrivals are dampening spot prices. If properly cured in aerated chawls, hold for 40-50 days until monsoon supplies decline."
    },
    "potato": {
        "id": "potato",
        "name": "Potato (Jyoti / Pukhraj)",
        "category": "Vegetables",
        "unit": "Quintal (100 kg)",
        "modal_price": 1420,
        "min_price": 1250,
        "max_price": 1600,
        "change_pct": 1.2,
        "trend": "up",
        "history_7d": [1380, 1390, 1400, 1400, 1410, 1415, 1420],
        "primary_mandi": "Agra (Uttar Pradesh)",
        "nearby_mandis": [
            {"name": "Agra Mandi", "distance_km": 12, "price": 1420, "transport_cost_qtl": 20},
            {"name": "Hathras Yard", "distance_km": 42, "price": 1460, "transport_cost_qtl": 40},
            {"name": "Delhi Azadpur", "distance_km": 210, "price": 1580, "transport_cost_qtl": 120}
        ],
        "supply_status": "Cold Storage Loading Season",
        "advisory": "Cold storage loading is near completion. Table potatoes seeing steady city demand. Retain top-grade lots for staggered off-season release."
    }
}

def get_market_overview():
    """
    Returns full list of commodities with today's prices and sparkline trends.
    """
    items = []
    for k, v in COMMODITIES_MARKET.items():
        modal = v["modal_price"]
        # Per kg equivalent
        if "Crate" in v["unit"]:
            per_kg = round(modal / 25, 2)
        else:
            per_kg = round(modal / 100, 2)

        items.append({
            "id": v["id"],
            "name": v["name"],
            "category": v["category"],
            "unit": v["unit"],
            "modal_price": modal,
            "min_price": v["min_price"],
            "max_price": v["max_price"],
            "per_kg": per_kg,
            "change_pct": v["change_pct"],
            "trend": v["trend"],
            "history_7d": v["history_7d"],
            "primary_mandi": v["primary_mandi"],
            "advisory": v["advisory"]
        })
    return items

def calculate_sell_vs_hold(crop_id, quantity_qtl, monthly_storage_cost=30):
    """
    Simulates whether the farmer should sell now vs hold for 30 days.
    """
    commodity = COMMODITIES_MARKET.get(crop_id)
    if not commodity:
        return {"error": "Invalid commodity"}

    current_price = commodity["modal_price"]
    current_revenue = current_price * quantity_qtl

    # Projected price change percentage based on current trend and fundamentals
    trend = commodity["trend"]
    if trend == "up":
        projected_pct = 7.5
        urgency = "Hold Recommended"
        badge = "badge-success"
        verdict = f"HOLD FOR 2-4 WEEKS: Strong demand and tight supply indicate prices could rise by ~{projected_pct}%."
    elif trend == "down":
        projected_pct = -4.0
        urgency = "Sell Now"
        badge = "badge-danger"
        verdict = "SELL IMMEDIATELY: Surging market arrivals and weakened buyer bids pose downward price risk."
    else:
        projected_pct = 1.0
        urgency = "Flexible / Staggered Sale"
        badge = "badge-warning"
        verdict = "STAGGERED SALE: Market is sideways. Sell 40% now to meet cash needs, hold 60% with good storage."

    projected_price = round(current_price * (1 + projected_pct / 100))
    gross_future_revenue = projected_price * quantity_qtl
    total_storage_cost = monthly_storage_cost * quantity_qtl
    net_future_revenue = gross_future_revenue - total_storage_cost
    net_gain_loss = net_future_revenue - current_revenue

    # Nearby mandi comparisons
    mandi_options = []
    for m in commodity.get("nearby_mandis", []):
        gross_p = m["price"] * quantity_qtl
        t_cost = m["transport_cost_qtl"] * quantity_qtl
        net_mandi_p = gross_p - t_cost
        diff_from_primary = net_mandi_p - current_revenue

        mandi_options.append({
            "name": m["name"],
            "distance_km": m["distance_km"],
            "price_per_qtl": m["price"],
            "transport_cost_total": t_cost,
            "net_revenue": net_mandi_p,
            "profit_difference": diff_from_primary,
            "is_profitable": diff_from_primary > 0
        })

    # Sort mandis by net revenue
    mandi_options.sort(key=lambda x: x["net_revenue"], reverse=True)

    return {
        "crop_name": commodity["name"],
        "unit": commodity["unit"],
        "quantity_qtl": quantity_qtl,
        "current_price": current_price,
        "current_revenue": current_revenue,
        "projected_price_30d": projected_price,
        "projected_pct_change": projected_pct,
        "gross_future_revenue": gross_future_revenue,
        "storage_cost": total_storage_cost,
        "net_future_revenue": net_future_revenue,
        "net_gain_loss": net_gain_loss,
        "verdict": verdict,
        "urgency": urgency,
        "badge": badge,
        "mandi_options": mandi_options,
        "best_mandi": mandi_options[0] if mandi_options else None
    }
