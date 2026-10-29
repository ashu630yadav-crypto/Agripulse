import os
from urllib.parse import quote_plus

from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

from services.weather_service import get_weather, get_active_weather_alerts, AGRI_LOCATIONS
from services.disease_service import analyze_plant_image, DISEASE_DATABASE
from services.calendar_service import get_calendar_data
from services.harvesting_service import HARVEST_GUIDES, READINESS_CRITERIA, evaluate_readiness
from services.quality_service import (assess_crop_quality, GRADE_PROFILES, A_MIN_SCORE,
                                      B_MIN_SCORE, TESTED_MATCHED, TESTED_PHOTOS,
                                      CATCH_C_FOUND, CATCH_C_TRUE, NON_PRODUCE_REFUSED,
                                      NON_PRODUCE_TESTED)
from services.market_service import get_market_overview, calculate_sell_vs_hold, COMMODITIES_MARKET

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "agripulse-dev-secret-change-me")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Context processor for global navbar alerts & locations
@app.context_processor
def inject_globals():
    # Follow whichever location the visitor selected, so the navbar never disagrees with the page.
    location = request.args.get("location")
    default_weather = get_weather(location or "ludhiana")
    active_alerts = get_active_weather_alerts(default_weather)
    return {
        "global_locations": AGRI_LOCATIONS,
        "global_alert_count": len(active_alerts),
        "global_alerts": active_alerts,
        "global_weather": default_weather,
        # Every navigation link carries the chosen place so the whole tool follows one location.
        "loc_query": f"?location={quote_plus(location)}" if location else ""
    }

# ----------------- HOME / DASHBOARD -----------------
@app.route("/")
def index():
    location = request.args.get("location", "ludhiana")
    weather_data = get_weather(location)
    alerts = get_active_weather_alerts(weather_data)
    market_items = get_market_overview()[:4] # top 4 for quick ticker
    calendar_preview = get_calendar_data(region="all", season="all")["crops"][:4]

    return render_template(
        "index.html",
        weather=weather_data,
        alerts=alerts,
        current_loc=location,
        market_items=market_items,
        calendar_preview=calendar_preview
    )

# ----------------- 1. WEATHER & FORECAST -----------------
@app.route("/weather")
def weather():
    location = request.args.get("location", "ludhiana")
    weather_data = get_weather(location)
    alerts = get_active_weather_alerts(weather_data)
    return render_template(
        "weather.html",
        weather=weather_data,
        alerts=alerts,
        current_loc=location
    )

# ----------------- 2. CROP DISEASE DETECTION -----------------
@app.route("/disease")
def disease():
    # Real photographs wherever possible; the early-blight picture is a drawn
    # diagram and the template labels it as such. Credits live in
    # static/images/samples/SOURCES.txt.
    sample_images = [
        {"file": "sample_leaf_rust.jpg", "label": "Leaf Rust (wheat)", "hint": "wheat",
         "kind": "photo", "credit": "USDA ARS / James Kolmer, public domain"},
        {"file": "sample_leaf_spot.jpg", "label": "Cercospora leaf spot (spinach)", "hint": "",
         "kind": "photo", "credit": "CABI slide series, CC0"},
        {"file": "sample_powdery_mildew.jpg", "label": "Powdery mildew (squash)", "hint": "vegetables",
         "kind": "photo", "credit": "Jerzy Opioła, CC BY-SA 4.0"},
        {"file": "sample_healthy_leaf.jpg", "label": "Healthy kale leaf", "hint": "",
         "kind": "photo", "credit": "Jules Verne Times Two, CC BY-SA 4.0"},
        {"file": "early_blight_leaf.jpg", "label": "Early blight (diagram)", "hint": "tomato",
         "kind": "diagram", "credit": "Illustration from the original AgriPulse mockups"},
    ]
    return render_template("disease.html", samples=sample_images, diseases=DISEASE_DATABASE)

@app.route("/api/disease/detect", methods=["POST"])
def detect_disease():
    crop_hint = request.form.get("crop_hint", "")
    sample_file = request.form.get("sample_file", "")

    # Check if a sample image was clicked
    if sample_file:
        safe_name = secure_filename(sample_file)
        sample_path = os.path.join(app.root_path, "static", "images", "samples", safe_name)
        if not os.path.exists(sample_path):
            return jsonify({"success": False, "error": "That sample image is not available."}), 404
        result = analyze_plant_image(sample_path, crop_hint)
        result["image_url"] = f"/static/images/samples/{safe_name}"
        return jsonify(result)

    # Check if a file was uploaded
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No image file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        result = analyze_plant_image(filepath, crop_hint)
        result["image_url"] = f"/uploads/{filename}"
        return jsonify(result)

    return jsonify({"success": False, "error": "File type not supported. Please upload JPG, PNG, or WEBP."}), 400

# ----------------- 3. CROP PLANTING CALENDAR -----------------
@app.route("/calendar")
def calendar():
    region = request.args.get("region", "all")
    season = request.args.get("season", "all")
    category = request.args.get("category", "all")

    cal_data = get_calendar_data(region, season, category)
    return render_template(
        "calendar.html",
        cal_data=cal_data,
        selected_region=region,
        selected_season=season,
        selected_category=category
    )

# ----------------- 4. HARVESTING GUIDANCE -----------------
@app.route("/harvesting")
def harvesting():
    selected_crop = request.args.get("crop", "wheat")
    crop_guide = HARVEST_GUIDES.get(selected_crop, HARVEST_GUIDES["wheat"])
    criteria = READINESS_CRITERIA.get(selected_crop, [])
    return render_template(
        "harvesting.html",
        guides=HARVEST_GUIDES,
        current_crop=selected_crop,
        guide=crop_guide,
        criteria=criteria
    )

@app.route("/api/harvesting/check", methods=["POST"])
def check_harvest_readiness():
    data = request.get_json() or {}
    crop_id = data.get("crop_id", "wheat")
    checked_ids = data.get("checked_ids", [])
    result = evaluate_readiness(crop_id, checked_ids)
    return jsonify(result)

# ----------------- 5. CROP QUALITY ASSESSMENT -----------------
QUALITY_SAMPLES = [
    {"file": "sample_carrot_bunch.jpg", "label": "Washed carrot bunch",
     "credit": "File:CarrotRoots.jpg - Jonathunder, GFDL 1.2"},
    {"file": "sample_tomato_wholesale_bin.jpg", "label": "Tomatoes in a wholesale bin",
     "credit": "File:Tomato wholesale market in Tanzania.jpg - Steadfast Gazelle, CC BY 4.0"},
    {"file": "sample_scabbed_potato.jpg", "label": "Potato with corky scab",
     "credit": "File:Common scab on potato.jpg - Clemson University/USDA, Bugwood.org, CC BY 3.0 us"},
    {"file": "sample_unsorted_sweet_potato_pile.jpg", "label": "Unsorted sweet potato pile",
     "credit": "File:Sweet Potato Harvest at Kirby Farms (20130920-OC-LSC-0731).jpg - USDA, public domain"},
    {"file": "sample_not_produce_fruit_fly.jpg", "label": "A fly, not a harvest",
     "credit": "File:Bactrocera invadens (06410592).jpg - IAEA Imagebank, CC BY-SA 2.0"},
]


@app.route("/quality")
def quality():
    return render_template(
        "quality.html",
        samples=QUALITY_SAMPLES,
        grades=GRADE_PROFILES,
        a_min=A_MIN_SCORE,
        b_min=B_MIN_SCORE,
        tested_matched=TESTED_MATCHED,
        tested_photos=TESTED_PHOTOS,
        catch_c_found=CATCH_C_FOUND,
        catch_c_true=CATCH_C_TRUE,
        refused=NON_PRODUCE_REFUSED,
        refused_tested=NON_PRODUCE_TESTED,
    )

@app.route("/api/quality/assess", methods=["POST"])
def assess_quality():
    crop_name = request.form.get("crop_name", "Produce")
    sample_file = request.form.get("sample_file", "")

    # Sample file flow
    if sample_file:
        sample_path = os.path.join(app.root_path, "static", "images", "samples", secure_filename(sample_file))
        if os.path.exists(sample_path):
            result = assess_crop_quality(sample_path, crop_name)
            result["image_url"] = f"/static/images/samples/{secure_filename(sample_file)}"
            return jsonify(result)

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No image file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        result = assess_crop_quality(filepath, crop_name)
        result["image_url"] = f"/uploads/{filename}"
        return jsonify(result)

    return jsonify({"success": False, "error": "Invalid file format."}), 400

# ----------------- 6. MARKET PRICE ESTIMATION -----------------
@app.route("/market")
def market():
    commodities = get_market_overview()
    selected_crop = request.args.get("crop", "wheat")
    selected_item = COMMODITIES_MARKET.get(selected_crop, COMMODITIES_MARKET["wheat"])
    initial_calc = calculate_sell_vs_hold(selected_crop, quantity_qtl=50, monthly_storage_cost=30)

    return render_template(
        "market.html",
        commodities=commodities,
        selected_crop=selected_crop,
        selected_item=selected_item,
        calc=initial_calc
    )

@app.route("/api/market/calculate", methods=["POST"])
def calculate_market():
    data = request.get_json() or {}
    crop_id = data.get("crop_id", "wheat")
    try:
        quantity = float(data.get("quantity", 50))
    except (ValueError, TypeError):
        quantity = 50.0
    try:
        storage_cost = float(data.get("storage_cost", 30))
    except (ValueError, TypeError):
        storage_cost = 30.0

    result = calculate_sell_vs_hold(crop_id, quantity, storage_cost)
    return jsonify(result)

# ----------------- 7. WEATHER ALERT SYSTEM -----------------
@app.route("/alerts")
def alerts():
    location = request.args.get("location", "ludhiana")
    weather_data = get_weather(location)
    alerts_list = get_active_weather_alerts(weather_data)

    # All standard disaster mitigation protocols
    all_protocols = [
        {
            "hazard": "Torrential Downpour & Flooding",
            "icon": "🌊",
            "mitigation": "Create deep drainage trenches every 15-20 rows. Siphon out standing water from paddy fields within 48h to prevent root anoxia. Hold off on nitrogen fertilizer application."
        },
        {
            "hazard": "Severe Heatwave & Drought",
            "icon": "☀️",
            "mitigation": "Shift irrigation to late evening or night to reduce evaporative loss. Apply heavy straw mulching to conserve moisture. Spray 2% potassium nitrate (KNO3) to induce stomatal resistance."
        },
        {
            "hazard": "Frost & Sub-Zero Cold Snap",
            "icon": "❄️",
            "mitigation": "Apply light night irrigation (water releases latent heat as it cools). Burn moist cowdung cakes/weed straw on windward field borders to create insulating smoke cover."
        },
        {
            "hazard": "Hailstorm & Squalls",
            "icon": "🌨️",
            "mitigation": "Install anti-hail net mesh over high-value orchards and vineyards. Post-hail: immediately spray Copper Oxychloride (3g/L) to seal bark and leaf wounds from secondary fungal canker."
        }
    ]

    return render_template(
        "alerts.html",
        weather=weather_data,
        alerts=alerts_list,
        current_loc=location,
        protocols=all_protocols
    )

# Static file server for uploaded images
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    # debug must stay off in a hosted deployment: the Werkzeug console allows code execution.
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
