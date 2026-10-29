import math
import os

from PIL import Image, ImageFilter, ImageStat

DISEASE_DATABASE = {
    "early_blight": {
        "name": "Early Blight",
        "pathogen": "Alternaria solani (Fungus)",
        "crops": ["Tomato", "Potato", "Eggplant", "Bell Pepper"],
        "severity": "Moderate to High",
        "badge_color": "danger",
        "symptoms": "Dark brown to black necrotic spots with characteristic target-like concentric rings on older lower leaves. Surrounding tissue develops yellow chlorotic halos.",
        "causes": "High relative humidity (>85%), warm temperatures (24-30°C), and extended leaf wetness from overhead irrigation or morning dew.",
        "organic_remedies": [
            "Spray copper-based organic fungicidal soap (Copper Hydroxide or Bordeaux mixture 1%).",
            "Apply bio-fungicide Trichoderma viride or Bacillus subtilis (5g/L water) to soil and foliar canopy.",
            "Remove and safely burn lower infected leaves to prevent spore splash to upper foliage."
        ],
        "chemical_treatments": [
            "Foliar spray with Mancozeb 75% WP @ 2.5 g/L water.",
            "In severe stages, apply Chlorothalonil 75% WP @ 2 g/L or Azoxystrobin 23% SC @ 1 ml/L.",
            "Repeat at 7 to 10 day intervals; rotate modes of action to avoid fungal resistance."
        ],
        "preventive_measures": [
            "Switch from overhead sprinkler irrigation to root drip irrigation to keep foliage dry.",
            "Maintain at least 45-60 cm plant spacing to ensure generous air circulation.",
            "Implement a minimum 3-year crop rotation with non-solanaceous crops (e.g. cereals, legumes)."
        ]
    },
    "late_blight": {
        "name": "Late Blight",
        "pathogen": "Phytophthora infestans (Oomycete)",
        "crops": ["Potato", "Tomato"],
        "severity": "Critical / Severe",
        "badge_color": "danger",
        "symptoms": "Water-soaked irregular pale-green lesions that rapidly turn dark brown or purplish-black. In humid weather, a delicate white downy fungal mildew appears on leaf undersides.",
        "causes": "Cool, overcast, and persistently wet conditions (temperatures 15-22°C with humidity >90%). Can destroy entire fields in 7-10 days if unchecked.",
        "organic_remedies": [
            "Apply Copper Oxychloride @ 3 g/L immediately at first sign.",
            "Foliar spray of fermented neem seed kernel extract (NSKE 5%).",
            "Strictly destroy infected plants and bury deep away from compost piles."
        ],
        "chemical_treatments": [
            "Systemic treatment: Metalaxyl 8% + Mancozeb 64% WP @ 2.5 g/L water.",
            "Curative spray: Dimethomorph 50% WP @ 1 g/L or Cymoxanil 8% + Mancozeb 64% @ 2 g/L.",
            "Spray both top and underside of leaves thoroughly before rainfall."
        ],
        "preventive_measures": [
            "Plant certified disease-free seed tubers and resistant cultivars (e.g., Kufri Girdhari, Kufri Khyati).",
            "Avoid planting downwind from old potato cull piles.",
            "Hill up rows properly so fungal spores cannot wash down into growing tubers."
        ]
    },
    "leaf_rust": {
        "name": "Leaf / Brown Rust",
        "pathogen": "Puccinia triticina / Puccinia sorghi (Fungus)",
        "crops": ["Wheat", "Barley", "Maize / Corn", "Soybean"],
        "severity": "Moderate to High",
        "badge_color": "warning",
        "symptoms": "Small, round to oval reddish-orange or cinnamon-brown powdery pustules scattered primarily on the upper leaf blade surface, releasing rusty spores upon touch.",
        "causes": "Moderate daytime temperatures (18-25°C), cool nights with heavy dew, and high nitrogen fertilizer overdose.",
        "organic_remedies": [
            "Foliar spray with sulfur dust (wettable sulfur 80% WP @ 3 g/L).",
            "Spray fermented sour buttermilk / whey diluted 1:10 with water as a bio-fungicide barrier.",
            "Promote mycorrhizal root colonization to boost natural phytoalexin defense."
        ],
        "chemical_treatments": [
            "Propiconazole 25% EC (Tilt) @ 1 ml/L or Tebuconazole 25.9% EC @ 1.25 ml/L water.",
            "Single prophylactic spray at boot-to-heading stage if rust alerts are active in the region."
        ],
        "preventive_measures": [
            "Cultivate rust-resistant varieties (e.g., DBW 187, DBW 222, HD 3086).",
            "Avoid excessive split applications of urea; balance with Potash (MOP) to toughen leaf cuticle.",
            "Eradicate alternate weed hosts from field embankments."
        ]
    },
    "powdery_mildew": {
        "name": "Powdery Mildew",
        "pathogen": "Erysiphe cichoracearum / Podosphaera (Fungus)",
        "crops": ["Cucumber", "Pumpkin", "Grape", "Apple", "Peas", "Okra", "Mango"],
        "severity": "Moderate",
        "badge_color": "warning",
        "symptoms": "Superficial white to ashy-gray talcum-powder-like patches on leaves, petioles, and young stems. Leaves eventually turn yellow, curl upward, and dry prematurely.",
        "causes": "Warm (20-28°C), dry days with high relative humidity at night, shaded canopies, and poor air movement.",
        "organic_remedies": [
            "Spray baking soda (potassium bicarbonate) solution: 4g baking soda + 3ml vegetable oil per 1L water.",
            "Neem oil spray (3000 ppm) @ 3-5 ml/L water with a mild emulsifier.",
            "Dilute milk spray (1 part fresh milk to 9 parts water) under bright sunshine produces antiseptic free radicals."
        ],
        "chemical_treatments": [
            "Sulfur 80% WDG @ 2-3 g/L (do not use in temperatures above 34°C to avoid scorching).",
            "Hexaconazole 5% EC @ 2 ml/L or Myclobutanil 10% WP @ 1 g/L water."
        ],
        "preventive_measures": [
            "Prune inner branches to open the canopy to direct sunlight and wind.",
            "Choose resistant varieties and avoid water stress during mid-growth."
        ]
    },
    "bacterial_blight": {
        "name": "Bacterial Leaf Blight",
        "pathogen": "Xanthomonas oryzae / Xanthomonas campestris (Bacteria)",
        "crops": ["Paddy / Rice", "Cotton", "Pomegranate", "Beans"],
        "severity": "High",
        "badge_color": "danger",
        "symptoms": "Water-soaked streaks starting from leaf tips and margins, progressing into wavy, yellow-to-whitish lesions with undulating borders. Milky bacterial ooze droplets form in high morning humidity.",
        "causes": "Strong monsoon rains, cyclonic wind damage, standing flood water, and excessive urea usage.",
        "organic_remedies": [
            "Spray cow dung supernatant slurry (fresh dung dissolved, filtered through muslin cloth @ 20%).",
            "Foliar application of Pseudomonas fluorescens bio-agent @ 5g/L.",
            "Drain standing water from paddy fields for 48 hours to dry bacterial ooze."
        ],
        "chemical_treatments": [
            "Streptocycline (Streptomycin sulphate + Tetracycline) @ 0.6 g + Copper Oxychloride @ 30 g in 10 L water.",
            "Copper hydroxide 53.8% DF @ 2 g/L water."
        ],
        "preventive_measures": [
            "Treat seeds with Streptocycline (1g in 10L water for 8 hours) prior to sowing.",
            "Apply potash (K2O) in two splits to strengthen vascular cell walls.",
            "Avoid clipping rice seedling tips before transplanting."
        ]
    },
    "leaf_spot": {
        "name": "Cercospora / Alternaria Leaf Spot",
        "pathogen": "Cercospora spp. (Fungus)",
        "crops": ["Peanut / Groundnut", "Chilli", "Beetroot", "Mustard", "Spinach"],
        "severity": "Moderate",
        "badge_color": "warning",
        "symptoms": "Circular to angular brown or grayish spots with distinct reddish-purple margins. Heavy spotting leads to extensive defoliation and stunted pod filling.",
        "causes": "Prolonged leaf wetness and temperatures between 25-32°C.",
        "organic_remedies": [
            "Spray bio-fungicide Trichoderma harzianum @ 5g/L.",
            "Spray aqueous neem leaf extract (10%) combined with vermiwash (5%)."
        ],
        "chemical_treatments": [
            "Carbendazim 50% WP @ 1 g/L or Chlorothalonil 75% WP @ 2 g/L.",
            "Tebuconazole 50% + Trifloxystrobin 25% WG @ 0.7 g/L."
        ],
        "preventive_measures": [
            "Deep plow crop residues after harvest to bury fungal fruiting bodies.",
            "Maintain balanced NPK fertilizer ratio (avoid excessive Nitrogen)."
        ]
    },
    "nutrient_deficiency": {
        "name": "Nutrient Deficiency (Nitrogen / Zinc / Iron Chlorosis)",
        "pathogen": "Physiological / Abiotic Disorder",
        "crops": ["Wheat", "Rice", "Citrus", "Tomato", "All crops"],
        "severity": "Low to Moderate",
        "badge_color": "info",
        "symptoms": "Uniform yellowing of older leaves (Nitrogen deficiency), or interveinal yellow chlorosis on young tender leaves while leaf veins remain bright green (Iron/Zinc deficiency).",
        "causes": "Alkaline or calcareous soil pH (>7.8), waterlogging, low organic matter, or depleted soil fertility.",
        "organic_remedies": [
            "Incorporate well-decomposed Farm Yard Manure (FYM) or vermicompost @ 5 tonnes/hectare.",
            "Apply Jeevamrutha or Panchagavya (3% foliar spray) every 15 days.",
            "Grow green manure crops like Dhaincha or Sunhemp and incorporate at 45 days."
        ],
        "chemical_treatments": [
            "Foliar spray of 2% Urea solution for quick Nitrogen revitalization.",
            "For Zinc/Iron: Chelated Zinc (Zn-EDTA 12%) @ 1 g/L or Ferrous Sulphate @ 5 g/L with 2.5 g citric acid."
        ],
        "preventive_measures": [
            "Conduct routine soil health card tests every 2 seasons.",
            "Maintain soil organic carbon above 0.75% to maximize cation exchange capacity."
        ]
    },
    "healthy": {
        "name": "Healthy Plant Foliage",
        "pathogen": "No Pathogen Detected",
        "crops": ["All Plants"],
        "severity": "None",
        "badge_color": "success",
        "symptoms": "Lush vibrant green pigmentation, smooth leaf blade, no necrotic lesions, fungal fuzz, or chlorotic mottling observed.",
        "causes": "Optimal soil moisture, balanced nutrition, active photosynthesis, and robust plant immune vigor.",
        "organic_remedies": [
            "Maintain regular preventive bio-fertilizer and seaweed extract foliar tonic.",
            "Continue mulching around roots to conserve soil moisture and earthworm activity."
        ],
        "chemical_treatments": [
            "No chemical intervention required. Preserve beneficial predator insects (ladybird beetles, chrysoperla)."
        ],
        "preventive_measures": [
            "Continue regular weekly field scouting.",
            "Maintain strict quarantine when introducing new seedlings or nursery rootstocks."
        ]
    }
}

# ---------------------------------------------------------------------------
# Diagnosis engine. Every number below is measured from the pixels of the
# photo: which colours sit inside the leaf, how many lesions there are, how
# big and how round they are, whether they carry a chlorotic ring, and where
# they sit relative to the leaf margin. The file name is never read.
# ---------------------------------------------------------------------------

ANALYSIS_EDGE = 320
MIN_LEAF_FRACTION = 0.08
LESION_MIN_AREA = 6
NEIGHBOURS8 = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))

# Which diseases a given crop makes more (or less) likely, applied as a
# multiplier on the measured evidence.
CROP_PRIORS = {
    "tomato": {"early_blight": 1.30, "late_blight": 1.25, "leaf_spot": 1.15, "powdery_mildew": 0.85},
    "potato": {"late_blight": 1.35, "early_blight": 1.30, "leaf_spot": 1.10},
    "eggplant": {"early_blight": 1.20, "powdery_mildew": 1.15},
    "wheat": {"leaf_rust": 1.45, "bacterial_blight": 1.10, "early_blight": 0.55, "late_blight": 0.55},
    "barley": {"leaf_rust": 1.45, "early_blight": 0.55, "late_blight": 0.55},
    "maize": {"leaf_rust": 1.35, "leaf_spot": 1.20, "early_blight": 0.60},
    "corn": {"leaf_rust": 1.35, "leaf_spot": 1.20, "early_blight": 0.60},
    "rice": {"bacterial_blight": 1.45, "leaf_rust": 0.50, "early_blight": 0.60},
    "paddy": {"bacterial_blight": 1.45, "leaf_rust": 0.50, "early_blight": 0.60},
    "cucumber": {"powdery_mildew": 1.50, "bacterial_blight": 1.10, "late_blight": 0.70},
    "pumpkin": {"powdery_mildew": 1.45, "leaf_spot": 1.10},
    "vegetables": {"powdery_mildew": 1.30, "leaf_spot": 1.15},
    "okra": {"powdery_mildew": 1.25, "leaf_spot": 1.20},
    "cotton": {"bacterial_blight": 1.30, "leaf_spot": 1.15, "leaf_rust": 0.70},
    "grape": {"powdery_mildew": 1.40, "late_blight": 1.15},
    "peanut": {"leaf_spot": 1.45, "early_blight": 1.10},
    "groundnut": {"leaf_spot": 1.45, "early_blight": 1.10},
    "chilli": {"leaf_spot": 1.30, "early_blight": 1.15},
    "citrus": {"nutrient_deficiency": 1.25, "leaf_spot": 1.15},
    "mango": {"powdery_mildew": 1.20, "nutrient_deficiency": 1.15},
    "apple": {"powdery_mildew": 1.30, "leaf_rust": 1.15},
    "soybean": {"leaf_rust": 1.20, "bacterial_blight": 1.10},
    "mustard": {"leaf_spot": 1.30, "powdery_mildew": 1.15},
    "beans": {"bacterial_blight": 1.25, "leaf_rust": 1.10, "powdery_mildew": 1.10},
}


def _clamp01(x):
    return 0.0 if x <= 0 else (1.0 if x >= 1 else x)


def _ramp(x, lo, hi):
    return _clamp01((x - lo) / (hi - lo))


def _ramp_down(x, lo, hi):
    return 1.0 - _ramp(x, lo, hi)


def _classify_pixel(hue, sat, val):
    """Map one RGB pixel onto a plant-health colour class."""
    if hue < 8 or hue >= 300:
        return "N"                      # red fruit, flowers, purple stems: not leaf tissue
    if val < 0.10:
        return "D"
    if sat < 0.28 and val > 0.62:
        return "W"                      # pale, bleached or powdery growth
    if sat < 0.16:
        return "N"                      # neutral grey: soil, sky, shadow, paper
    if hue < 45:
        if val < 0.62 or sat < 0.45:
            return "B"
        return "R"
    if hue < 70:
        return "Y" if (sat > 0.28 and val > 0.45) else "G"
    if hue < 165:
        return "G"
    return "N"


def _pixel_labels(image):
    """Downscale once, then label every pixel; returns (w, h, labels, saturation)."""
    rgb = image.convert("RGB")
    w, h = rgb.size
    scale = ANALYSIS_EDGE / max(w, h)
    if scale < 1:
        w, h = max(8, round(w * scale)), max(8, round(h * scale))
        rgb = rgb.resize((w, h), Image.Resampling.BILINEAR)
    # Interpolating hue across the red wrap-around corrupts colours, so resize in
    # RGB first and only then convert.
    raw = rgb.convert("HSV").tobytes()
    n = len(raw) // 3
    labels = bytearray(n)
    sats = bytearray(n)
    for i in range(n):
        j = i * 3
        labels[i] = ord(_classify_pixel(raw[j] * (360.0 / 255.0), raw[j + 1] / 255.0, raw[j + 2] / 255.0))
        sats[i] = raw[j + 1]
    return w, h, labels, sats


def _connected(mask, w, h, start, seen):
    stack = [start]
    seen[start] = 1
    out = []
    while stack:
        p = stack.pop()
        out.append(p)
        x, y = p % w, p // w
        for dx, dy in NEIGHBOURS8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                q = ny * w + nx
                if mask[q] and not seen[q]:
                    seen[q] = 1
                    stack.append(q)
    return out


def _leaf_region(labels, w, h):
    """
    Seed on saturated leaf tissue, then absorb the pale and dark pockets it
    holds. A pocket that reaches the frame edge is background, not a lesion.
    """
    tissue = {ord(c) for c in "GYBR"}
    seed = bytearray(1 if labels[p] in tissue else 0 for p in range(w * h))
    seen = bytearray(w * h)
    body = None
    for start in range(w * h):
        if seed[start] and not seen[start]:
            comp = _connected(seed, w, h, start, seen)
            if body is None or len(comp) > len(body):
                body = comp
    if not body or len(body) < MIN_LEAF_FRACTION * w * h:
        return None

    leaf = bytearray(w * h)
    for p in body:
        leaf[p] = 1

    for _ in range(2):
        pocket = bytearray(1 - leaf[p] for p in range(w * h))
        seen = bytearray(w * h)
        room = int(sum(leaf) * 0.4)
        for start in range(w * h):
            if pocket[start] and not seen[start]:
                comp = _connected(pocket, w, h, start, seen)
                if len(comp) > room:
                    continue
                if any(p < w or p >= w * (h - 1) or p % w == 0 or p % w == w - 1 for p in comp):
                    continue
                for p in comp:
                    leaf[p] = 1
    return leaf


def _plausible_leaf(labels, leaf, w, h):
    """Reject frames that do not contain one readable leaf."""
    leaf_px = [p for p in range(w * h) if leaf[p]]
    n = len(leaf_px)
    if n < MIN_LEAF_FRACTION * w * h:
        return "no plant tissue fills enough of the frame"
    xs = [p % w for p in leaf_px]
    ys = [p // w for p in leaf_px]
    bbox = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
    if n / bbox < 0.20:
        return "the plant in this photo is a stem, blade or fragment rather than a whole leaf"
    green = sum(1 for p in leaf_px if labels[p] == ord("G"))
    if green / n < 0.10:
        return "there is too little green leaf area in this photo to read symptoms against"
    return None


def _lesion_shape(comp, w, h, mask, boundary):
    area = len(comp)
    cx = sum(p % w for p in comp) / area
    cy = sum(p // w for p in comp) / area
    perimeter = 0
    for p in comp:
        x, y = p % w, p // w
        for dx, dy in NEIGHBOURS8:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or not mask[ny * w + nx]:
                perimeter += 1
                break
    sxx = sum(((p % w) - cx) ** 2 for p in comp) / area
    syy = sum(((p // w) - cy) ** 2 for p in comp) / area
    sxy = sum(((p % w) - cx) * ((p // w) - cy) for p in comp) / area
    trace = sxx + syy
    disc = math.sqrt(max(0.0, trace * trace / 4 - (sxx * syy - sxy * sxy)))
    major = max(trace / 2 + disc, 1e-6)
    minor = max(trace / 2 - disc, 1e-6)
    xs = [p % w for p in comp]
    ys = [p // w for p in comp]
    return {
        "area": area,
        "cx": cx,
        "cy": cy,
        "bbox": (min(xs), max(xs), min(ys), max(ys)),
        "circularity": _clamp01(4 * math.pi * area / (perimeter * perimeter)) if perimeter else 0.0,
        "elongation": min(8.0, math.sqrt(major / minor)),
        "margin_hits": sum(1 for p in comp if boundary[p]),
    }


def _halo_score(shape, labels, leaf, w, h):
    """Fraction of the tissue ringing a lesion that is yellow or pale."""
    x0, x1, y0, y1 = shape["bbox"]
    hits = total = 0
    for ring in range(2, 6):
        rx0, rx1 = x0 - ring, x1 + ring
        ry0, ry1 = y0 - ring, y1 + ring
        for x in range(max(0, rx0), min(w, rx1 + 1)):
            for y in (ry0, ry1):
                if 0 <= y < h:
                    p = y * w + x
                    if leaf[p]:
                        total += 1
                        hits += labels[p] in (ord("Y"), ord("W"))
        for y in range(max(0, ry0), min(h, ry1 + 1)):
            for x in (rx0, rx1):
                if 0 <= x < w:
                    p = y * w + x
                    if leaf[p]:
                        total += 1
                        hits += labels[p] in (ord("Y"), ord("W"))
    return hits / total if total else 0.0


def _cell_grid(leaf_px, w, h):
    """Split the leaf silhouette into a 4x4 grid so symptom spread can be measured."""
    xs = [p % w for p in leaf_px]
    ys = [p // w for p in leaf_px]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span_x, span_y = max(1, x1 - x0 + 1), max(1, y1 - y0 + 1)
    cell_of = [-1] * (w * h)
    for p in leaf_px:
        gx = min(3, (p % w - x0) * 4 // span_x)
        gy = min(3, (p // w - y0) * 4 // span_y)
        cell_of[p] = gy * 4 + gx
    return cell_of, len({cell_of[p] for p in leaf_px})


def _class_stats(labels, leaf, w, h, chars, boundary, leaf_n, cell_of, leaf_cells, halo=False):
    """Count and measure every separate patch of the given colour classes."""
    ords = {ord(c) for c in chars}
    mask = bytearray(1 if leaf[p] and labels[p] in ords else 0 for p in range(w * h))
    seen = bytearray(w * h)
    shapes = []
    for p in range(w * h):
        if mask[p] and not seen[p]:
            comp = _connected(mask, w, h, p, seen)
            if len(comp) >= LESION_MIN_AREA:
                shapes.append(_lesion_shape(comp, w, h, mask, boundary))

    hits = {}
    for p in range(w * h):
        if mask[p] and cell_of[p] >= 0:
            hits[cell_of[p]] = hits.get(cell_of[p], 0) + 1

    stats = {
        "count": len(shapes),
        "area_pct": sum(mask) / leaf_n,
        "mean_area": (sum(s["area"] for s in shapes) / len(shapes)) if shapes else 0.0,
        "largest_pct": (max((s["area"] for s in shapes), default=0)) / leaf_n,
        "circularity": (sum(s["circularity"] for s in shapes) / len(shapes)) if shapes else 0.0,
        "elongation": (sum(s["elongation"] for s in shapes) / len(shapes)) if shapes else 0.0,
        "margin_ratio": (sum(s["margin_hits"] for s in shapes) / sum(s["area"] for s in shapes)) if shapes else 0.0,
        "spread": len([1 for v in hits.values() if v >= 3]) / max(1, leaf_cells),
        "halo": 0.0,
    }
    if halo and shapes:
        big = [s for s in shapes if s["area"] >= 8]
        if big:
            stats["halo"] = sum(_halo_score(s, labels, leaf, w, h) * s["area"] for s in big) / sum(s["area"] for s in big)
    return stats


def _measure(labels, sats, w, h, leaf):
    leaf_px = [p for p in range(w * h) if leaf[p]]
    n = len(leaf_px)
    counts = {c: 0 for c in "GYBRDW"}
    for p in leaf_px:
        counts[chr(labels[p])] = counts.get(chr(labels[p]), 0) + 1

    boundary = bytearray(w * h)
    for p in leaf_px:
        x, y = p % w, p // w
        if any(not (0 <= x + dx < w and 0 <= y + dy < h) or not leaf[(y + dy) * w + (x + dx)]
               for dx, dy in NEIGHBOURS8):
            boundary[p] = 1

    cell_of, leaf_cells = _cell_grid(leaf_px, w, h)
    necrotic = _class_stats(labels, leaf, w, h, "BD", boundary, n, cell_of, leaf_cells, halo=True)
    rust = _class_stats(labels, leaf, w, h, "R", boundary, n, cell_of, leaf_cells)
    pale = _class_stats(labels, leaf, w, h, "W", boundary, n, cell_of, leaf_cells)
    chlorosis = _class_stats(labels, leaf, w, h, "Y", boundary, n, cell_of, leaf_cells)

    yellow_touching_green = 0
    yellow_total = 0
    for p in leaf_px:
        if labels[p] == ord("Y"):
            yellow_total += 1
            x, y = p % w, p // w
            if any(0 <= x + dx < w and 0 <= y + dy < h and leaf[(y + dy) * w + (x + dx)]
                   and labels[(y + dy) * w + (x + dx)] == ord("G") for dx, dy in NEIGHBOURS8):
                yellow_touching_green += 1

    return {
        "leaf_pct": round(n / (w * h) * 100, 1),
        "saturation": round(sum(sats[p] for p in leaf_px) / (255 * n), 3),
        "green_pct": counts["G"] / n,
        "yellow_pct": counts["Y"] / n,
        "brown_pct": counts["B"] / n,
        "dark_pct": counts["D"] / n,
        "rust_pct": counts["R"] / n,
        "white_pct": counts["W"] / n,
        "lesion_pct": 1 - counts["G"] / n,
        "vein_adjacency": yellow_touching_green / yellow_total if yellow_total else 0.0,
        "necrotic": necrotic,
        "rust": rust,
        "pale": pale,
        "chlorosis": chlorosis,
    }


def _image_quality(image):
    gray = image.convert("L").resize((160, 160), Image.Resampling.BILINEAR)
    edges = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).stddev[0]
    brightness = ImageStat.Stat(gray).mean[0]
    warnings = []
    if brightness < 45:
        warnings.append("Photo looks under-exposed; shoot in daylight without hard shadow.")
    elif brightness > 225:
        warnings.append("Photo looks washed out by flash or direct sun; reshade the leaf and retake.")
    if edges < 6:
        warnings.append("Photo looks soft or out of focus; hold the camera steady and refocus on the lesion.")
    return {"sharpness": round(edges, 1), "brightness": round(brightness, 1), "warnings": warnings}


def _score(features, crop_hint):
    f = features
    ne, ru, pa = f["necrotic"], f["rust"], f["pale"]
    dead = ne["area_pct"]
    # Vein ends, dirt grains and sensor noise also register as dark pixels, so a
    # spot diagnosis has to be made of patches with real area behind them.
    solid = _ramp(ne["mean_area"], 10, 25)
    necrosis = solid * max(_ramp(dead, 0.02, 0.10), 0.8 * _ramp(ne["count"], 8, 25))
    ev = {
        "healthy": (_ramp(f["green_pct"], 0.78, 0.95) * _ramp_down(f["lesion_pct"], 0.02, 0.10)
                    * _ramp_down(f["rust_pct"], 0.015, 0.06) * _ramp_down(f["white_pct"], 0.04, 0.14)),
        "leaf_rust": (_ramp(f["rust_pct"], 0.02, 0.10)
                      * max(_ramp(ru["count"], 8, 30) * _ramp_down(ru["mean_area"], 25, 90),
                            _ramp(f["rust_pct"], 0.10, 0.25))),
        "powdery_mildew": (_ramp(f["white_pct"], 0.04, 0.16) * _ramp(pa["spread"], 0.30, 0.60)
                           * _ramp_down(dead, 0.12, 0.30)),
        "early_blight": (necrosis * _ramp(ne["halo"], 0.15, 0.45) * _ramp(ne["circularity"], 0.35, 0.60)
                         * _ramp_down(ne["largest_pct"], 0.25, 0.45)),
        "late_blight": (_ramp(dead, 0.12, 0.30) * _ramp(ne["largest_pct"], 0.06, 0.20)
                        * _ramp_down(ne["halo"], 0.50, 0.75) * _ramp_down(f["rust_pct"], 0.08, 0.18)),
        "bacterial_blight": (necrosis * _ramp(ne["margin_ratio"], 0.05, 0.18)
                             * _ramp(ne["elongation"], 1.6, 2.6) * _ramp_down(ne["halo"], 0.55, 0.80)),
        "leaf_spot": (necrosis * _ramp(ne["count"], 8, 25) * _ramp(ne["circularity"], 0.35, 0.55)
                      * _ramp_down(ne["halo"], 0.45, 0.70)),
        "nutrient_deficiency": (_ramp(f["yellow_pct"], 0.15, 0.40) * _ramp_down(dead, 0.08, 0.20)
                                * (0.55 + 0.45 * _ramp(f["vein_adjacency"], 0.25, 0.55))
                                * _ramp_down(f["white_pct"], 0.06, 0.16)),
    }
    priors = CROP_PRIORS.get((crop_hint or "").strip().lower(), {})
    return {k: v * priors.get(k, 1.0) for k, v in ev.items()}


# Measured results of this detector on 26 labelled field photographs taken from
# Wikimedia Commons (the ones it could not reject outright). For each condition:
# how many photographs of it we tested, and how many it named correctly. The raw
# pattern score turned out not to predict correctness, so the confidence shown to
# a farmer is anchored to these measured rates instead of to the score.
#
# Several cells are 0 of 3 or 0 of 4. That is the honest reading of a small test
# set: on real photographs this rule-based screen has so far only proven itself on
# rust, leaf spot and clean foliage.
CLASS_ACCURACY = {
    "leaf_rust": (3, 3),
    "leaf_spot": (2, 3),
    "healthy": (1, 2),
    "powdery_mildew": (1, 6),
    "early_blight": (0, 3),
    "late_blight": (0, 4),
    "bacterial_blight": (0, 3),
    "nutrient_deficiency": (0, 2),
}

TOTAL_TESTED = sum(n for _, n in CLASS_ACCURACY.values())
TOTAL_CORRECT = sum(m for m, _ in CLASS_ACCURACY.values())


def _measured(key):
    correct, tested = CLASS_ACCURACY.get(key, (0, 0))
    rate = correct / tested if tested else 0.30
    return correct, tested, rate


def _confidence(key, scores, quality, leaf_pct):
    ranked = sorted(scores.values(), reverse=True)
    top, second = ranked[0], (ranked[1] if len(ranked) > 1 else 0.0)
    separation = (top - second) / top if top > 0 else 0.0
    conf = 100 * _measured(key)[2] * (0.80 + 0.20 * separation)
    if leaf_pct < 25:
        conf *= 0.85
    if quality["warnings"]:
        conf *= 0.85
    return round(min(85.0, max(15.0, conf)), 1)


def _candidates(scores):
    total = sum(scores.values())
    if total <= 0:
        return []
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    return [
        {
            "key": key,
            "name": DISEASE_DATABASE[key]["name"],
            "share": round(scores[key] / total * 100, 1),
            "badge_color": DISEASE_DATABASE[key]["badge_color"],
        }
        for key, score in ranked[:3] if score > 0.01
    ]


def _pct(v):
    return f"{round(v * 100, 1)}%"


def _evidence_notes(f):
    ne = f["necrotic"]
    notes = [f"Plant tissue covers {f['leaf_pct']}% of the frame."]
    notes.append(f"Measured on that tissue: green {_pct(f['green_pct'])}, yellow chlorosis {_pct(f['yellow_pct'])}, "
                 f"brown or black necrotic tissue {_pct(ne['area_pct'])}, orange pustules "
                 f"{_pct(f['rust_pct'])}, pale powdery growth {_pct(f['white_pct'])}.")
    if ne["count"]:
        notes.append(f"{ne['count']} separate dead-tissue patches counted; the largest covers "
                     f"{_pct(ne['largest_pct'])} of the leaf and averages {round(ne['circularity'], 2)} "
                     f"roundness out of 1.0.")
    else:
        notes.append("No discrete dead-tissue patch large enough to measure.")
    if ne["halo"]:
        notes.append(f"{_pct(ne['halo'])} of the tissue ringing the dead patches is yellow or pale, "
                     "which is what a chlorotic halo looks like measured.")
    if f["rust"]["count"]:
        notes.append(f"{f['rust']['count']} orange pustules counted, averaging "
                     f"{round(f['rust']['mean_area'])} pixels each.")
    if f["pale"]["spread"]:
        notes.append(f"Pale growth is spread over {round(f['pale']['spread'] * 100)}% of the leaf area sampled.")
    return notes


def analyze_plant_image(image_path, crop_hint=None):
    """
    Diagnoses a leaf photo from measured colour and lesion morphology.

    Returns the prescription for the best-matching condition plus the raw
    measurements, the differential, and an honest confidence figure.
    """
    if not os.path.exists(image_path):
        return {"success": False, "error": "Image file not found on the server."}
    try:
        with Image.open(image_path) as img:
            img.load()
            w, h, labels, sats = _pixel_labels(img)
            leaf = _leaf_region(labels, w, h)
            quality = _image_quality(img)
    except Exception as exc:
        return {"success": False, "error": f"Failed to read image: {exc}"}

    if leaf is None:
        return {
            "success": False,
            "error": ("No plant tissue detected in this photo. Fill the frame with one affected leaf, "
                      "shot against a plain background in daylight."),
        }
    unusable = _plausible_leaf(labels, leaf, w, h)
    if unusable:
        return {
            "success": False,
            "error": (f"Cannot diagnose this photo: {unusable}. Photograph one whole leaf that fills "
                      "the frame, with the affected area and some healthy green tissue in shot."),
        }

    features = _measure(labels, sats, w, h, leaf)
    scores = _score(features, crop_hint)
    top_key, top_score = max(scores.items(), key=lambda kv: kv[1])

    if top_score < 0.08:
        info = dict(DISEASE_DATABASE["healthy"])
        info["name"] = "Inconclusive Scan"
        info["pathogen"] = "No reliable signature measured"
        info["severity"] = "Unknown"
        info["badge_color"] = "info"
        info["symptoms"] = ("The photo was readable but showed no pattern strong enough to diagnose. "
                            + _evidence_notes(features)[1])
        info["causes"] = ("Common causes of an unreadable sample: the leaf is too far away, the photo is "
                          "out of focus, symptoms are at a stage shared by several diseases, or the "
                          "background colour was mistaken for the leaf.")
        info["organic_remedies"] = ["Do not spray on the basis of this scan. Repeat the photo at closer range."]
        info["chemical_treatments"] = ["No chemical action advised from an inconclusive scan."]
        info["preventive_measures"] = [
            "Photograph one leaf that fills the frame, showing both healthy green area and the suspect spots.",
            "Shoot the upper and the underside of the leaf as two separate photos.",
            "If symptoms spread within a week, re-scan the newer affected leaves.",
        ]
        confidence = round(min(50.0, 30 + top_score * 100), 1)
        correct, tested = 0, 0
        accuracy_note = ("No condition scored high enough on the measured colours to name one. "
                         "Nothing here should be read as a clean bill of health - re-shoot one leaf "
                         "that fills the frame and scan again.")
    else:
        info = DISEASE_DATABASE[top_key]
        confidence = _confidence(top_key, scores, quality, features["leaf_pct"])
        correct, tested, _rate = _measured(top_key)
        accuracy_note = (
            "This is a colour and shape screen, not a trained plant-pathology model. On the field "
            f"photographs we tested for {info['name']}, it named this condition correctly in "
            f"{correct} of {tested}. Across all {TOTAL_TESTED} test photographs it is right "
            f"{TOTAL_CORRECT} times. Use it as a shortlist of what to look for - confirm with your "
            "local Krishi Vigyan Kendra before buying any fungicide."
        )

    return {
        "success": True,
        "disease_key": top_key if top_score >= 0.08 else "inconclusive",
        "name": info["name"],
        "pathogen": info["pathogen"],
        "crops": info["crops"],
        "severity": info["severity"],
        "badge_color": info["badge_color"],
        "confidence": confidence,
        "affected_area_pct": round(min(100.0, features["lesion_pct"] * 100), 1),
        "symptoms": info["symptoms"],
        "causes": info["causes"],
        "organic_remedies": info["organic_remedies"],
        "chemical_treatments": info["chemical_treatments"],
        "preventive_measures": info["preventive_measures"],
        "candidates": _candidates(scores),
        "evidence": _evidence_notes(features),
        "image_quality": quality,
        "class_accuracy_pct": round(100 * correct / tested) if tested else 0,
        "tested_photos": tested,
        "tested_correct": correct,
        "accuracy_note": accuracy_note,
        "crop_hint_used": (crop_hint or "").strip().lower() or None,
        "method": "Colour segmentation and lesion morphology measured on the uploaded photo",
        "metrics": {
            "healthy_chlorophyll_pct": round(features["green_pct"] * 100, 1),
            "chlorosis_yellow_pct": round(features["yellow_pct"] * 100, 1),
            "necrosis_brown_pct": round(features["necrotic"]["area_pct"] * 100, 1),
            "mildew_white_pct": round(features["white_pct"] * 100, 1),
            "rust_orange_pct": round(features["rust_pct"] * 100, 1),
            "leaf_area_pct": features["leaf_pct"],
            "necrotic_patch_count": features["necrotic"]["count"],
            "rust_pustule_count": features["rust"]["count"],
            "lesion_ring_halo_pct": round(features["necrotic"]["halo"] * 100, 1),
        },
        "measurements": features,
    }

