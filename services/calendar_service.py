"""
Crop Planting Calendar Service
Provides agro-climatic zone and season-based planting recommendations,
growth timelines, and monthly schedules.
"""

REGIONS = [
    {"id": "all", "name": "All Regions"},
    {"id": "north", "name": "Northern Plains (Punjab, Haryana, UP)"},
    {"id": "central", "name": "Central & Western (MP, Maharashtra, Gujarat)"},
    {"id": "south", "name": "Southern Peninsula (Karnataka, AP, TN, Telangana)"},
    {"id": "east", "name": "Eastern Plains (Bihar, Bengal, Odisha, Assam)"},
    {"id": "arid", "name": "Arid / Semi-Arid (Rajasthan, North Gujarat)"}
]

SEASONS = [
    {"id": "all", "name": "All Seasons"},
    {"id": "kharif", "name": "Kharif (Monsoon / Summer: Jun - Oct)"},
    {"id": "rabi", "name": "Rabi (Winter / Post-Monsoon: Oct - Apr)"},
    {"id": "zaid", "name": "Zaid (Summer / Spring: Mar - Jun)"}
]

CATEGORIES = [
    {"id": "all", "name": "All Categories"},
    {"id": "cereals", "name": "Cereals & Grains"},
    {"id": "pulses", "name": "Pulses & Legumes"},
    {"id": "oilseeds", "name": "Oilseeds"},
    {"id": "vegetables", "name": "Vegetables"},
    {"id": "cash_crops", "name": "Cash & Commercial"}
]

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CROPS_CALENDAR = [
    {
        "id": "wheat",
        "name": "Wheat (Kanak / Gehun)",
        "category": "cereals",
        "season": "rabi",
        "regions": ["north", "central", "east", "arid"],
        "sowing_months": [10, 11],  # Nov - Dec (0-indexed: 10=Nov, 11=Dec)
        "harvest_months": [2, 3],   # Mar - Apr
        "duration_days": "120 - 145 days",
        "temp_range": "10°C - 25°C (Cool climate with sunny ripening)",
        "soil": "Well-drained fertile loam and clay loam (pH 6.0 - 7.5)",
        "seed_rate": "40 - 50 kg/acre (100 kg/ha)",
        "water_need": "Medium (4 - 6 irrigations at CRI, tillering, heading, milking)",
        "icon": "🌾",
        "pro_tip": "Apply the first Critical Root Initiation (CRI) irrigation exactly 21 days after sowing for 30% higher tillering."
    },
    {
        "id": "rice",
        "name": "Rice / Paddy (Dhan)",
        "category": "cereals",
        "season": "kharif",
        "regions": ["north", "central", "south", "east"],
        "sowing_months": [4, 5, 6],  # May - Jul
        "harvest_months": [9, 10],   # Oct - Nov
        "duration_days": "115 - 150 days",
        "temp_range": "22°C - 35°C (High humidity & ample sunshine)",
        "soil": "Clayey, heavy loams with good water retention capacity (pH 5.5 - 7.0)",
        "seed_rate": "10 - 12 kg/acre for nursery transplanting",
        "water_need": "High (1200 - 1500 mm, standing water 3-5 cm during tillering)",
        "icon": "🍚",
        "pro_tip": "Adopt Direct Seeded Rice (DSR) with seed drill to save 30% irrigation water and reduce 25 days nursery labor."
    },
    {
        "id": "maize",
        "name": "Maize / Corn (Makka)",
        "category": "cereals",
        "season": "kharif",
        "regions": ["north", "central", "south", "east", "arid"],
        "sowing_months": [5, 6],     # Jun - Jul
        "harvest_months": [8, 9],    # Sep - Oct
        "duration_days": "90 - 110 days",
        "temp_range": "20°C - 32°C",
        "soil": "Deep, well-aerated sandy loam to silt loam rich in organic matter",
        "seed_rate": "7 - 8 kg/acre",
        "water_need": "Medium (500 - 650 mm, sensitive to waterlogging)",
        "icon": "🌽",
        "pro_tip": "Ensure ridge and furrow planting to avoid water stagnation which suffocates young maize seedlings."
    },
    {
        "id": "mustard",
        "name": "Mustard / Rapeseed (Sarson)",
        "category": "oilseeds",
        "season": "rabi",
        "regions": ["north", "central", "east", "arid"],
        "sowing_months": [9, 10],    # Oct - Nov
        "harvest_months": [1, 2],    # Feb - Mar
        "duration_days": "105 - 130 days",
        "temp_range": "15°C - 25°C (Dry clear weather during flowering)",
        "soil": "Light to heavy loams with good drainage (pH 6.5 - 8.0)",
        "seed_rate": "1.5 - 2.0 kg/acre",
        "water_need": "Low to Medium (2 - 3 timely irrigations)",
        "icon": "🌼",
        "pro_tip": "Apply Sulfur (20 kg/ha elemental S) alongside basal NPK to increase seed oil content by 2-3%."
    },
    {
        "id": "soybean",
        "name": "Soybean (Bhat)",
        "category": "oilseeds",
        "season": "kharif",
        "regions": ["central", "north", "south"],
        "sowing_months": [5, 6],     # Jun - Jul
        "harvest_months": [8, 9],    # Sep - Oct
        "duration_days": "90 - 105 days",
        "temp_range": "22°C - 30°C",
        "soil": "Fertile clay loam to black cotton soils with good drainage (pH 6.0 - 7.5)",
        "seed_rate": "25 - 30 kg/acre",
        "water_need": "Medium (450 - 600 mm)",
        "icon": "🌱",
        "pro_tip": "Inoculate seeds with Bradyrhizobium japonicum culture before sowing to maximize biological nitrogen fixation."
    },
    {
        "id": "chickpea",
        "name": "Chickpea / Bengal Gram (Chana)",
        "category": "pulses",
        "season": "rabi",
        "regions": ["north", "central", "arid", "south"],
        "sowing_months": [9, 10],    # Oct - Nov
        "harvest_months": [1, 2],    # Feb - Mar
        "duration_days": "110 - 130 days",
        "temp_range": "15°C - 28°C",
        "soil": "Medium to deep black soils, sandy loam with good drainage (pH 6.5 - 8.0)",
        "seed_rate": "30 - 35 kg/acre (Desi), 40 - 45 kg/acre (Kabuli)",
        "water_need": "Low (Requires only 1-2 irrigations: pre-flowering and pod development)",
        "icon": "🧆",
        "pro_tip": "Nip/pinch terminal apical shoots at 30-35 days after sowing to stimulate vigorous secondary branching and pod count."
    },
    {
        "id": "cotton",
        "name": "Cotton (Kapas)",
        "category": "cash_crops",
        "season": "kharif",
        "regions": ["north", "central", "south", "arid"],
        "sowing_months": [3, 4, 5],  # Apr - Jun
        "harvest_months": [9, 10, 11], # Oct - Dec
        "duration_days": "150 - 180 days",
        "temp_range": "21°C - 35°C (Requires 180-200 frost-free sunny days)",
        "soil": "Deep black cotton soils (Vertisols) or alluvial loam (pH 6.5 - 8.5)",
        "seed_rate": "1.5 - 2.0 kg/acre (Bt hybrid)",
        "water_need": "Medium to High (700 - 1000 mm)",
        "icon": "☁️",
        "pro_tip": "Install pheromone traps @ 5 per acre at 45 DAS to monitor pink bollworm moth flights before larvae enter bolls."
    },
    {
        "id": "potato",
        "name": "Potato (Aloo)",
        "category": "vegetables",
        "season": "rabi",
        "regions": ["north", "east", "central"],
        "sowing_months": [9, 10],    # Oct - Nov
        "harvest_months": [0, 1],    # Jan - Feb
        "duration_days": "80 - 110 days",
        "temp_range": "15°C - 22°C (Cool nights below 18°C are crucial for tuberization)",
        "soil": "Loose, friable sandy loam rich in humus (pH 5.2 - 6.5)",
        "seed_rate": "10 - 12 quintals/acre of disease-free seed tubers",
        "water_need": "Medium (5-7 light irrigations; stop 10 days prior to harvest)",
        "icon": "🥔",
        "pro_tip": "Perform de-haulming (cutting off green foliage) 10-12 days before digging to cure and harden the potato skin."
    },
    {
        "id": "tomato",
        "name": "Tomato (Tamatar)",
        "category": "vegetables",
        "season": "all",
        "regions": ["north", "central", "south", "east"],
        "sowing_months": [6, 7, 9, 10], # Jul-Aug & Oct-Nov
        "harvest_months": [9, 10, 0, 1, 2],
        "duration_days": "90 - 120 days",
        "temp_range": "18°C - 28°C",
        "soil": "Well-drained sandy loam or clay loam with pH 6.0 - 7.0",
        "seed_rate": "60 - 80 grams/acre (Hybrid nursery)",
        "water_need": "Medium (Consistent moisture prevents Blossom End Rot and fruit cracking)",
        "icon": "🍅",
        "pro_tip": "Stake plants with bamboo trellis and prune bottom suckers to keep fruit off the ground and eliminate soil-borne blight."
    },
    {
        "id": "onion",
        "name": "Onion (Pyaaz)",
        "category": "vegetables",
        "season": "rabi",
        "regions": ["central", "north", "south", "arid"],
        "sowing_months": [10, 11],   # Nov - Dec
        "harvest_months": [3, 4],    # Apr - May
        "duration_days": "120 - 140 days",
        "temp_range": "13°C - 24°C vegetative; 25°C - 32°C for bulb maturity",
        "soil": "Deep friable loam with high organic matter, free from stones",
        "seed_rate": "3 - 4 kg/acre (nursery seed)",
        "water_need": "Medium (Stop watering 15 days before harvest when tops start falling)",
        "icon": "🧅",
        "pro_tip": "Cure harvested onions in shade with good cross-ventilation for 7 days to seal necks and prevent Aspergillus rot."
    },
    {
        "id": "green_gram",
        "name": "Green Gram / Moong",
        "category": "pulses",
        "season": "zaid",
        "regions": ["north", "central", "south", "east", "arid"],
        "sowing_months": [2, 3],     # Mar - Apr
        "harvest_months": [4, 5],    # May - Jun
        "duration_days": "60 - 70 days (Short duration)",
        "temp_range": "25°C - 35°C",
        "soil": "Well-drained fertile loamy soil (pH 6.5 - 7.5)",
        "seed_rate": "8 - 10 kg/acre",
        "water_need": "Low (2-3 irrigations in summer)",
        "icon": "🫘",
        "pro_tip": "Ideal catch crop between wheat harvest and paddy transplanting that restores 35 kg atmospheric Nitrogen per hectare."
    },
    {
        "id": "sugarcane",
        "name": "Sugarcane (Ganna)",
        "category": "cash_crops",
        "season": "all",
        "regions": ["north", "central", "south", "east"],
        "sowing_months": [1, 2, 9, 10], # Feb-Mar or Oct
        "harvest_months": [10, 11, 0, 1], # 10-12 months later
        "duration_days": "300 - 365 days (Full year crop)",
        "temp_range": "24°C - 35°C",
        "soil": "Deep, well-drained rich alluvial or black soils",
        "seed_rate": "35,000 - 40,000 two-budded setts/hectare",
        "water_need": "High (1500 - 2500 mm with 15 - 20 irrigations)",
        "icon": "🎋",
        "pro_tip": "Trash mulching between cane rows suppresses 80% weed emergence and conserves vital soil moisture during dry heat."
    }
]

def get_calendar_data(region="all", season="all", category="all"):
    """
    Filters crops and constructs the 12-month calendar state for each crop.
    Monthly states:
    - 'sow': Sowing window
    - 'grow': Vegetative / Flowering
    - 'harvest': Harvesting window
    - 'off': Off-season
    """
    filtered = []
    for crop in CROPS_CALENDAR:
        # Region filter
        if region != "all" and region not in crop["regions"]:
            continue
        # Season filter
        if season != "all" and crop["season"] != season and crop["season"] != "all":
            continue
        # Category filter
        if category != "all" and crop["category"] != category:
            continue

        # Build month state array (length 12)
        month_states = []
        sow_m = crop["sowing_months"]
        harv_m = crop["harvest_months"]

        for m in range(12):
            if m in sow_m:
                month_states.append({"month": MONTHS[m], "status": "sow", "label": "Sowing"})
            elif m in harv_m:
                month_states.append({"month": MONTHS[m], "status": "harvest", "label": "Harvest"})
            else:
                # Determine if in-between growth
                # Simple logic for growth period
                is_growing = False
                min_sow = min(sow_m)
                max_harv = max(harv_m)
                if min_sow <= max_harv:
                    if min_sow < m < max_harv:
                        is_growing = True
                else: # wraps around year (e.g. Nov to Mar)
                    if m > min_sow or m < max_harv:
                        is_growing = True

                if is_growing:
                    month_states.append({"month": MONTHS[m], "status": "grow", "label": "Growing"})
                else:
                    month_states.append({"month": MONTHS[m], "status": "off", "label": "Off-season"})

        crop_copy = dict(crop)
        crop_copy["month_states"] = month_states
        filtered.append(crop_copy)

    return {
        "crops": filtered,
        "total_count": len(filtered),
        "regions": REGIONS,
        "seasons": SEASONS,
        "categories": CATEGORIES,
        "months": MONTHS
    }
