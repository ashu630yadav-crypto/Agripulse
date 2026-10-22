import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

from services.weather_service import fetch_weather, get_active_weather_alerts, AGRI_LOCATIONS
from services.disease_service import analyze_plant_image, DISEASE_DATABASE
from services.calendar_service import get_calendar_data
from services.harvesting_service import HARVEST_GUIDES, READINESS_CRITERIA, evaluate_readiness
from services.quality_service import assess_crop_quality
from services.market_service import get_market_overview, calculate_sell_vs_hold, COMMODITIES_MARKET

app = Flask(__name__)
app.config["SECRET_KEY"] = "agripulse-krishi-secret-2026"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Context processor for global navbar alerts & locations
@app.context_processor
def inject_globals():
    # Use ludhiana as primary default
    default_weather = fetch_weather("ludhiana")
    active_alerts = get_active_weather_alerts(default_weather)
    return {
        "global_locations": AGRI_LOCATIONS,
        "global_alert_count": len(active_alerts),
        "global_alerts": active_alerts
    }

# ----------------- HOME / DASHBOARD -----------------
@app.route("/")
def index():
    location = request.args.get("location", "ludhiana")
    weather_data = fetch_weather(location)
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
    weather_data = fetch_weather(location)
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
    sample_images = [
        {"file": "early_blight_leaf.jpg", "label": "Early Blight (Tomato/Potato)", "hint": "tomato"},
        {"file": "leaf_rust.jpg", "label": "Leaf Rust (Wheat/Corn)", "hint": "wheat"},
        {"file": "powdery_mildew.jpg", "label": "Powdery Mildew (Vegetables)", "hint": "vegetables"},
        {"file": "healthy_leaf.jpg", "label": "Healthy Leaf (Clean foliage)", "hint": "healthy"}
    ]
    return render_template("disease.html", samples=sample_images, diseases=DISEASE_DATABASE)

@app.route("/api/disease/detect", methods=["POST"])
def detect_disease():
    crop_hint = request.form.get("crop_hint", "")
    sample_file = request.form.get("sample_file", "")

    # Check if a sample image was clicked
    if sample_file:
        sample_path = os.path.join(app.root_path, "static", "images", "samples", secure_filename(sample_file))
        if os.path.exists(sample_path):
            result = analyze_plant_image(sample_path, crop_hint)
            result["image_url"] = f"/static/images/samples/{secure_filename(sample_file)}"
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
@app.route("/quality")
def quality():
    sample_images = [
        {"file": "grade_a_crop.jpg", "label": "Grade A Sample (Export Quality)", "name": "Tomato / Fresh Fruit"},
        {"file": "grade_b_crop.jpg", "label": "Grade B Sample (Standard Mandi)", "name": "Tomato / Fresh Fruit"},
        {"file": "grade_c_crop.jpg", "label": "Grade C Sample (Processing)", "name": "Tomato / Fresh Fruit"}
    ]
    return render_template("quality.html", samples=sample_images)

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
    weather_data = fetch_weather(location)
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
    app.run(host="127.0.0.1", port=5000, debug=True)
