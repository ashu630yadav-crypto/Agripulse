"""
Harvesting Guidance Service
Provides crop-specific harvesting standards, physical maturity indicators,
post-harvest storage guidelines, and an interactive Readiness Assessment Calculator.
"""

HARVEST_GUIDES = {
    "wheat": {
        "name": "Wheat (Kanak / Gehun)",
        "icon": "🌾",
        "optimal_moisture": "12% - 14%",
        "maturity_signs": [
            "Straw and ears turn from green to golden yellow or light amber.",
            "Grains become hard and cannot be easily indented by a thumbnail.",
            "Moisture content of grain falls to 14-16% for harvesting, 12% for safe bin storage.",
            "Flag leaf and upper peduncle turn dry and brittle."
        ],
        "best_time_of_day": "Mid-morning to afternoon (10:00 AM - 4:00 PM) once the morning dew has completely evaporated from the ears.",
        "harvesting_methods": [
            "Combine Harvester: Set cylinder drum speed at 850-950 RPM and concave clearance at 12-15 mm to prevent grain splitting.",
            "Manual Sickle: Cut 5-7 cm above ground level using serrated sickles to minimize shattered ear loss."
        ],
        "post_harvest_steps": [
            "Dry threshed grain on clean tarpaulin sheets under sun for 2-3 days until moisture drops below 12%.",
            "Winnow to remove chaff, weed seeds, and broken kernels.",
            "Store in clean, moisture-proof metal bins or hermetic Purdue Improved Crop Storage (PICS) bags.",
            "Treat storage rooms with Malathion 50% EC spray (1:100 dilution) prior to bag stacking."
        ],
        "losses_risk": "Delaying harvest causes grain shattering in high winds and lodging during unseasonal rain, dropping market grade."
    },
    "rice": {
        "name": "Rice / Paddy (Dhan)",
        "icon": "🍚",
        "optimal_moisture": "20% - 22% (Harvest) | 13% - 14% (Milling/Storage)",
        "maturity_signs": [
            "80% to 85% of grains in the panicle have turned golden straw-yellow.",
            "Grains in the lower portion of the panicle reach hard dough stage.",
            "Flag leaves start yellowing, though lower stems may still be slightly greenish.",
            "Field has been drained 10-14 days prior to harvest to facilitate mechanical movement."
        ],
        "best_time_of_day": "Early morning to early afternoon on bright, dry sunny days.",
        "harvesting_methods": [
            "Combine Harvester: Ensure cutter bar height is set above muddy soil; calibrate reel speed to avoid grain shatter.",
            "Manual Harvesting: Cut at 10-15 cm above ground; bundle into small sheaves and dry in field for 24 hours."
        ],
        "post_harvest_steps": [
            "Thresh immediately within 24 hours of harvest to prevent yellowing and internal microbial heating.",
            "Gradual mechanical or sun drying to bring moisture down from 21% to safe 14% without cracking the kernel.",
            "Store in raised godowns on wooden pallets (dunnage) away from damp walls."
        ],
        "losses_risk": "Premature harvest yields high percentage of chalky, broken kernels. Over-delayed harvest causes severe shattering and sun-cracking."
    },
    "maize": {
        "name": "Maize / Corn (Makka)",
        "icon": "🌽",
        "optimal_moisture": "18% - 20% (Cob Harvest) | 12% - 13% (Storage)",
        "maturity_signs": [
            "Husk covers turn dry, papery, and straw-brown.",
            "Formation of the prominent 'Black Layer' at the tip/base of the kernel where it attaches to the cob.",
            "Milk line on the kernel face disappears completely.",
            "Kernels become glassy, hard, and resist fingernail depression."
        ],
        "best_time_of_day": "Dry sunny days after dew dries off the outer husks.",
        "harvesting_methods": [
            "Manual De-husking: Snap cobs off the standing stalk by pulling downward and twisting.",
            "Corn Combine: calibrate corn head snapping rolls to prevent ear dropping or cob crushing."
        ],
        "post_harvest_steps": [
            "Sun dry cobs on concrete floor for 4-5 days before mechanical sheller de-husking.",
            "Dry shelled grain to 12% moisture to avoid deadly Aflatoxin (Aspergillus flavus) fungal contamination.",
            "Store in aerated silos or air-tight hermetic drums."
        ],
        "losses_risk": "Harvesting with moisture above 24% causes severe ear rot and high aflatoxin mold."
    },
    "potato": {
        "name": "Potato (Aloo)",
        "icon": "🥔",
        "optimal_moisture": "Cured skin, no skinning/peeling under thumb pressure",
        "maturity_signs": [
            "Vines turn naturally yellow and collapse (senescence).",
            "Perform de-haulming (cut stems at ground level) 10-12 days before digging.",
            "Tuber skin is fully set (does not slip or peel when rubbed firmly with thumb).",
            "Soil is moderately friable (neither dry rock-hard nor wet and sticky)."
        ],
        "best_time_of_day": "Cool morning hours (7:00 AM - 11:00 AM). Avoid hot afternoon sun which causes tuber scald and blackheart.",
        "harvesting_methods": [
            "Tractor-mounted potato digger elevator or gentle manual hand-spading.",
            "Avoid blade cuts or mechanical bruising which allows bacterial soft rot entry."
        ],
        "post_harvest_steps": [
            "Field curing: Leave tubers in heaps covered with paddy straw for 10-12 days at 15-20°C and 85-90% humidity to heal minor skin wounds.",
            "Sort and discard rotten, cut, or green sun-exposed tubers.",
            "Store in cold storage at 2-4°C (seed potatoes) or 8-10°C with CIPC sprout suppressant (table/chips potatoes)."
        ],
        "losses_risk": "Digging during wet soil leads to soil adherence and severe bacterial soft rot during transit."
    },
    "tomato": {
        "name": "Tomato (Tamatar)",
        "icon": "🍅",
        "optimal_moisture": "Harvest at 'Breaker' or 'Pink' stage depending on transport distance",
        "maturity_signs": [
            "For distant transport: 'Breaker stage' (first faint pinkish-yellow blush at blossom end).",
            "For local market: 'Pink to Light Red stage' (60-80% red surface).",
            "For direct home use / processing: 'Full Red Ripe stage' (firm, uniform red color).",
            "Fruit pulls cleanly from calyx with gentle upward snap."
        ],
        "best_time_of_day": "Early morning before field temperature rises above 24°C.",
        "harvesting_methods": [
            "Manual hand picking with gentle twisting motion, leaving calyx intact if required.",
            "Place gently into padded plastic crates (never more than 3 layers deep to prevent crushing bottom fruits)."
        ],
        "post_harvest_steps": [
            "Pre-cool in shaded packing shed immediately to remove field heat.",
            "Wash in 100 ppm chlorinated water to eliminate surface pathogens.",
            "Grade by size and color; never store below 10°C to prevent chilling injury and flavor loss."
        ],
        "losses_risk": "Harvesting during hot midday leads to rapid softening, water loss, and transit shriveling."
    },
    "cotton": {
        "name": "Cotton (Kapas)",
        "icon": "☁️",
        "optimal_moisture": "< 8% lint moisture",
        "maturity_signs": [
            "Bolls are fully cracked open and white fluffy lint is completely exposed.",
            "Boll bracts are dried and brown.",
            "Picking is carried out in 3-4 clean passes as bolls mature progressively from lower to upper branches."
        ],
        "best_time_of_day": "After 10:00 AM once solar warmth has dried all morning dew from the open lint fibers.",
        "harvesting_methods": [
            "Manual clean picking: Pluck only dry white fluffy seed-cotton without dried leaves, bracts, or immature lock trash."
        ],
        "post_harvest_steps": [
            "Spread picked cotton on clean tarpaulins in sun for 4 hours to evaporate moisture.",
            "Do not store or pack wet cotton; it causes yellow fiber discoloration and spontaneous combustion.",
            "Pack into clean cotton cloth bags (avoid polypropylene plastic bags which contaminate lint fibers)."
        ],
        "losses_risk": "Rain on open bolls stains lint gray-brown, reducing sale price by up to 40%."
    }
}

READINESS_CRITERIA = {
    "wheat": [
        {"id": "w1", "text": "Over 80% of ears have turned from green to golden yellow / amber", "points": 30},
        {"id": "w2", "text": "Grains are hard and cannot be dented with your fingernail", "points": 30},
        {"id": "w3", "text": "Peduncle (stem just beneath ear) has turned completely dry and yellow", "points": 20},
        {"id": "w4", "text": "Grain moisture test or bite test feels dry, brittle, and snaps cleanly", "points": 20}
    ],
    "rice": [
        {"id": "r1", "text": "80% to 85% of panicle grains have turned golden straw yellow", "points": 30},
        {"id": "r2", "text": "Grains at the bottom end of the panicle are firm (hard dough stage)", "points": 30},
        {"id": "r3", "text": "Field water has been drained for 10-12 days and ground is firm", "points": 20},
        {"id": "r4", "text": "Estimated grain moisture is between 20% and 22%", "points": 20}
    ],
    "maize": [
        {"id": "m1", "text": "Cob husk leaves are completely dry, paper-thin, and brownish", "points": 30},
        {"id": "m2", "text": "Kernels show clear 'Black Layer' at connection tip with the cob", "points": 35},
        {"id": "m3", "text": "Kernel milk line is zero; grain is hard and glossy", "points": 20},
        {"id": "m4", "text": "Silks are dry, dark brown, and brittle", "points": 15}
    ],
    "potato": [
        {"id": "p1", "text": "Vines have turned yellow and foliage has been de-haulmed for 10+ days", "points": 35},
        {"id": "p2", "text": "Tuber skin does not slip or peel off when rubbed firmly with thumb", "points": 35},
        {"id": "p3", "text": "Soil is reasonably dry and crumbly (not sticky wet)", "points": 15},
        {"id": "p4", "text": "Sample tubers dug have reached commercial target grade size", "points": 15}
    ],
    "tomato": [
        {"id": "t1", "text": "Fruit has reached target size and star pattern at blossom end turns yellowish-pink", "points": 30},
        {"id": "t2", "text": "Internal gel in seed cavity has developed and seeds are mature", "points": 25},
        {"id": "t3", "text": "Flesh firmness is solid without puffiness or hollow spots", "points": 25},
        {"id": "t4", "text": "Harvesting is scheduled for cool morning hours before 10 AM", "points": 20}
    ],
    "cotton": [
        {"id": "c1", "text": "At least 60% of lower and middle bolls are wide open and fluffy", "points": 35},
        {"id": "c2", "text": "Morning dew has completely evaporated; lint feels dry and warm to touch", "points": 30},
        {"id": "c3", "text": "Open bolls are free from pink bollworm entry frass", "points": 20},
        {"id": "c4", "text": "Cotton picking bags are clean cloth bags without plastic threads", "points": 15}
    ]
}

def evaluate_readiness(crop_id, checked_ids):
    """
    Calculates harvest readiness percentage and actionable advice.
    """
    criteria = READINESS_CRITERIA.get(crop_id, [])
    if not criteria:
        return {"error": "Invalid crop selected"}

    total_points = sum(c["points"] for c in criteria)
    earned_points = sum(c["points"] for c in criteria if c["id"] in checked_ids)

    score_pct = round((earned_points / total_points) * 100, 1)

    if score_pct >= 85:
        verdict = "Ready for Immediate Harvest"
        badge = "badge-success"
        recommendation = "Your crop has achieved optimal biological and physiological maturity. Harvest within the next 24 to 48 hours during recommended morning hours to prevent shattering losses and weather risks."
        urgency = "High Priority"
    elif score_pct >= 60:
        verdict = "Approaching Maturity (Wait 3 - 6 Days)"
        badge = "badge-warning"
        recommendation = "The crop is in the final ripening phase. Monitor grain hardness and skin set daily. Withhold further irrigation and prepare harvesting machinery and storage bags."
        urgency = "Moderate"
    else:
        verdict = "Not Ready / Immature"
        badge = "badge-danger"
        recommendation = "Crop is still accumulating dry matter and grains/tubers have not fully filled. Premature harvest will cause severe shrinkage, moisture mold, and low market prices."
        urgency = "Standby"

    return {
        "crop_id": crop_id,
        "score_pct": score_pct,
        "verdict": verdict,
        "badge": badge,
        "recommendation": recommendation,
        "urgency": urgency,
        "checked_count": len(checked_ids),
        "total_criteria": len(criteria)
    }
