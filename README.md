# 🌾 AgriPulse - Smart Agricultural Intelligence Platform

**AgriPulse** is a comprehensive, open-source web platform engineered to empower farmers, agronomists, and agricultural extension workers with real-time decision-support tools. Built using Python, Flask, Computer Vision, and Open-Meteo satellite feeds, the system combines precision agro-meteorology, visual plant diagnostics, and commodity market intelligence into a single accessible interface.

---

## 🌟 The 7 Core Agricultural Modules

### 1. 🌦️ Weather Information & Agro-Forecast
- **Real-Time Meteorological Data:** Live temperature, apparent temperature, relative humidity, barometric pressure, wind gusts, and UV radiation index powered by Open-Meteo satellite feeds.
- **7-Day Agricultural Forecast:** Min/Max temperatures, rain sum (mm), and precipitation probability per day.
- **Hourly Operation Windows:** 24-hour hour-by-hour forecast with agricultural metrics:
  - **Spraying Suitability Index:** Evaluates wind drift (<15 km/h), wash-off rain risk, and evaporation to flag spraying as *Ideal*, *Marginal*, or *Unsuitable*.
  - **Fungal Pathogen Risk Index:** Detects temperature/humidity windows conducive to spore germination.
  - **Evapotranspiration ($ET_0$):** Real-time daily crop water consumption estimates to calibrate irrigation.

### 2. 🔬 Crop Disease Detection & AI Treatment Engine
- **Visual Leaf Diagnosis:** Upload or take a leaf photo with a smartphone camera or select built-in crop samples.
- **Computer Vision Extraction:** Computes healthy chlorophyll vs. yellow chlorotic halos, dark necrotic lesions, and mildew fungal coatings.
- **Comprehensive Disease Database:** Detects Early Blight (*Alternaria solani*), Late Blight (*Phytophthora infestans*), Leaf Rust (*Puccinia*), Powdery Mildew, Bacterial Leaf Blight, and Nutrient Deficiencies.
- **Bilingual Actionable Prescriptions:** Provides biological/organic remedies, synthetic chemical treatments with exact dosages, and preventive cultural practices.
- **Audio Voice Readout:** Farmers can click "🔊 Listen to Treatment Plan" to hear prescriptions read aloud via browser speech synthesis.

### 3. 📅 Crop Planting & Agro-Calendar
- **Climatic Zone Recommendations:** Filterable by regions (Northern Plains, Central/Western, Southern Peninsula, Eastern, Arid/Semi-Arid).
- **Cropping Seasons:** Full schedules for **Kharif** (monsoon), **Rabi** (winter), **Zaid** (summer), and perennial cash crops.
- **Visual 12-Month Gantt Calendar:** Color-coded timelines showing *Sowing*, *Vegetative Growth*, and *Harvesting* months.
- **Agronomic Profiles:** Days to maturity, soil pH, seed rates per acre, water requirements, and practical yield pro-tips.

### 4. 🚜 Harvesting Guidance & Readiness Checker
- **Maturity Indicators:** Moisture content targets (e.g. 12-14% for wheat, 20-22% for paddy harvest, 13% for storage), color transformations, and grain hardness.
- **Machinery Calibration:** Combine harvester cylinder RPM settings and cutting bar heights to prevent shattered ear loss.
- **Post-Harvest Handling:** Curing, sun-drying on tarpaulin sheets, and hermetic storage protocols.
- **Interactive "Ready to Harvest?" Checklist:** Farmers check off observable field traits to compute a 0-100% maturity score with clear directives (*"Ready for Immediate Harvest"*, *"Wait 3-5 days"*, etc.).

### 5. ⭐ Crop Quality Assessment & Commercial Grading
- **Produce Visual Inspection:** Uploads of harvested vegetables, fruits, or grains are evaluated for surface blemishes, color vibrancy, and symmetry.
- **Commercial Grading:**
  - **Grade A (Premium / Export Quality):** Score $\ge 85\%$, commands +20% to +30% price premium. Recommended for supermarket chains and export houses.
  - **Grade B (Fair Average Quality - FAQ):** Score $65\% - 84\%$, standard APMC Mandi benchmark.
  - **Grade C (Processing / Industrial Grade):** Score $< 65\%$, redirected to juice, puree, sauce, or starch mills.
- **Value-Add Tips:** Storage longevity estimates and post-harvest sorting instructions.

### 6. 📈 Market Price Estimation & Mandi Intelligence
- **Live Mandi Rates:** Real-time modal prices, minimum/maximum ranges, and per-kg prices across major agricultural commodities (Wheat, Basmati Paddy, Soybean, Mustard, Cotton, Tomato, Onion, Potato, etc.).
- **7-Day Price Trends:** Interactive SVG sparklines and price trajectory indicators (Rising ↗, Falling ↘, Steady →).
- **"Sell Now vs Hold" Decision Simulator:** Farmers input lot quantity (quintals) and monthly storage cost to calculate immediate cash vs projected 30-day net gain after storage expenses.
- **Nearby Mandi Price Arbitrage:** Compares local mandis against regional wholesale hubs factoring in transportation freight costs.

### 7. 🔔 Weather Alert System & Hazard Response
- **Severe Weather Warnings:** Auto-detects torrential downpours (>30mm), blistering heatwaves (>38°C), sub-zero frost hazards, and damaging windstorms.
- **Emergency Action Plans:** Immediate step-by-step mitigation (e.g., digging perimeter drainage trenches, applying night irrigation against frost, staking tall banana/sugarcane).
- **Alert Simulator:** Allows instant simulation of floods, heatwaves, or freeze alerts to demonstrate emergency responses.
- **Persistent Emergency Top Banner:** Active severe alerts remain pinned to the top of the interface.

---

## 🛠️ Technology Stack

- **Backend:** Python 3, Flask, Jinja2, Werkzeug
- **Computer Vision & Image Processing:** Pillow (PIL)
- **APIs & Data:** Open-Meteo Satellite & Meteorological API (Keyless, with graceful offline fallbacks)
- **Frontend:** Semantic HTML5, Custom Responsive Agriculture CSS, JavaScript (ES6+)
- **Audio / Accessibility:** Native Web Speech API for voice text-to-speech advisories

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### 3. Run Automated Tests
```bash
python test_app.py
```
