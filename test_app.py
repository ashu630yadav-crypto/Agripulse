import unittest
import json
import os
from io import BytesIO
from app import app

class AgriPulseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_routes_status_code(self):
        routes = ["/", "/weather", "/disease", "/calendar", "/harvesting", "/quality", "/market", "/alerts"]
        for r in routes:
            response = self.client.get(r)
            self.assertEqual(response.status_code, 200, f"Route {r} failed with status {response.status_code}")
            print(f"PASS: {r} returned 200 OK")

    def test_disease_detection_measures_the_pixels(self):
        """The four real photographs are the reference behaviour; if the detector
        stops reading pixels and starts reading filenames, this test fails."""
        expected = {
            "sample_leaf_rust.jpg": ("wheat", "Rust"),
            "sample_leaf_spot.jpg": ("", "Leaf Spot"),
            "sample_powdery_mildew.jpg": ("vegetables", "Powdery Mildew"),
            "sample_healthy_leaf.jpg": ("", "Healthy"),
        }
        for filename, (hint, needle) in expected.items():
            response = self.client.post("/api/disease/detect",
                                        data={"sample_file": filename, "crop_hint": hint})
            self.assertEqual(response.status_code, 200, filename)
            data = response.get_json()
            self.assertTrue(data.get("success"), f"{filename}: {data.get('error')}")
            self.assertIn(needle, data.get("name"), filename)
            for key in ("candidates", "evidence", "image_quality", "accuracy_note", "measurements"):
                self.assertIn(key, data, f"{filename} is missing its {key}")
            # Confidence is anchored to the measured per-class accuracy, never to 100%.
            measured = data["class_accuracy_pct"] / 100.0
            self.assertLessEqual(data["confidence"], 100 * measured + 1, filename)
            self.assertGreaterEqual(data["confidence"], 100 * measured * 0.8 - 1, filename)
            self.assertGreater(len(data["organic_remedies"]), 0, filename)
        print("PASS: Disease detector reads the photograph, sample by sample")

    def test_disease_diagnosis_ignores_the_filename(self):
        from io import BytesIO

        healthy_path = os.path.join(app.root_path, "static", "images", "samples", "sample_healthy_leaf.jpg")
        with open(healthy_path, "rb") as handle:
            healthy = handle.read()
        # Uploaded under a blight filename: the answer must still come from the pixels.
        response = self.client.post(
            "/api/disease/detect",
            data={"file": (BytesIO(healthy), "early_blight_leaf.jpg"), "crop_hint": "tomato"},
            content_type="multipart/form-data",
        )
        data = response.get_json()
        self.assertTrue(data.get("success"))
        self.assertNotIn("Blight", data["name"])
        self.assertEqual(data["disease_key"], "healthy")

        # A photo with no plant tissue in it must be rejected with a reason, not diagnosed.
        from PIL import Image
        buffer = BytesIO()
        Image.new("RGB", (400, 400), (128, 128, 128)).save(buffer, format="JPEG")
        response = self.client.post(
            "/api/disease/detect",
            data={"file": (BytesIO(buffer.getvalue()), "sample_leaf_rust.jpg")},
            content_type="multipart/form-data",
        )
        data = response.get_json()
        self.assertFalse(data.get("success"))
        self.assertIn("leaf", data.get("error", "").lower())
        print("PASS: Filenames do not drive the diagnosis; unusable photos are rejected")

    def test_disease_diagram_sample_is_not_sold_as_a_photo(self):
        response = self.client.get("/disease")
        html = response.get_data(as_text=True)
        self.assertIn("(diagram)", html)
        self.assertNotIn("AI Vision", html)
        self.assertNotIn("AI Confidence", html)
        self.assertIn("Other conditions this could be", html)

    def test_quality_grades_pixels_not_filenames(self):
        """The same photograph must get the same grade whatever it is called."""
        from PIL import Image, ImageDraw

        def lot(spots):
            img = Image.new("RGB", (320, 320), (222, 220, 214))
            d = ImageDraw.Draw(img)
            d.ellipse([40, 40, 280, 280], fill=(196, 42, 34))
            for x, y in spots:
                d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=(58, 34, 22))
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=95)
            return buf.getvalue()

        def grade(blob, name):
            return self.client.post(
                "/api/quality/assess",
                data={"file": (BytesIO(blob), name), "crop_name": "Tomato"},
                content_type="multipart/form-data",
            ).get_json()

        # A clean lot saved under a Grade-C filename, and a marked-up lot saved
        # under a Grade-A filename. The names must not decide anything.
        clean = grade(lot([]), "grade_c_crop.jpg")
        marked = grade(lot([(110, 110), (210, 110), (110, 210), (210, 210), (160, 160)]),
                       "grade_a_crop.jpg")

        self.assertTrue(clean.get("success"), clean.get("error"))
        self.assertTrue(marked.get("success"), marked.get("error"))
        self.assertEqual(clean["grade"], "A")
        self.assertGreaterEqual(clean["overall_score"] - marked["overall_score"], 8,
                                "five dark marks on the same lot did not lower the score")
        self.assertGreater(marked["metrics"]["blemish_area_pct"],
                           clean["metrics"]["blemish_area_pct"])
        print("PASS: quality grade follows the pixels, not the filename")

    def test_quality_reports_what_it_measured(self):
        response = self.client.post("/api/quality/assess",
                                    data={"sample_file": "sample_scabbed_potato.jpg", "crop_name": "Potato"})
        data = response.get_json()
        self.assertTrue(data.get("success"))
        for key in ("evidence", "unmeasurable", "agreement", "accuracy_note", "sub_scores",
                    "sub_weights", "measurements", "image_quality"):
            self.assertIn(key, data)
        m = data["metrics"]
        for key in ("surface_purity_pct", "blemish_area_pct", "colour_evenness_pct",
                    "dominant_saturation_pct", "rim_not_judged_pct", "produce_in_frame_pct"):
            self.assertIn(key, m)
        # Purity and defect area are two views of one measurement, so they must agree.
        self.assertAlmostEqual(m["surface_purity_pct"] + m["blemish_area_pct"], 100.0, places=1)
        self.assertGreaterEqual(m["produce_in_frame_pct"], 15.0)
        self.assertTrue(any("measured" in line.lower() or "%" in line for line in data["evidence"]))
        self.assertTrue(len(data["unmeasurable"]) >= 4)
        self.assertNotIn("Computer Vision", json.dumps(data))
        print("PASS: quality report carries its own measurements and its limits")

    def test_quality_refuses_photos_it_cannot_measure(self):
        from PIL import Image

        for colour, label in (((128, 128, 128), "a grey field"), ((250, 250, 250), "a white page")):
            buffer = BytesIO()
            Image.new("RGB", (400, 400), colour).save(buffer, format="JPEG")
            data = self.client.post(
                "/api/quality/assess",
                data={"file": (BytesIO(buffer.getvalue()), "photo.jpg")},
                content_type="multipart/form-data",
            ).get_json()
            self.assertFalse(data.get("success"), f"{label} was graded anyway")
            self.assertTrue(data.get("error"))

        # A real photograph of an insect: no harvested crop in it, so no grade.
        data = self.client.post("/api/quality/assess",
                                data={"sample_file": "sample_not_produce_fruit_fly.jpg"}).get_json()
        self.assertFalse(data.get("success"))
        self.assertNotIn("grade", data)
        print("PASS: unusable photos are refused with a reason, not scored")

    def test_quality_page_publishes_the_real_bands(self):
        from services.quality_service import A_MIN_SCORE, B_MIN_SCORE, _grade_for

        self.assertEqual(_grade_for(A_MIN_SCORE), "A")
        self.assertEqual(_grade_for(A_MIN_SCORE - 0.1), "B")
        self.assertEqual(_grade_for(B_MIN_SCORE), "B")
        self.assertEqual(_grade_for(B_MIN_SCORE - 0.1), "C")

        html = self.client.get("/quality").get_data(as_text=True)
        self.assertIn(f"score {A_MIN_SCORE} and above", html)
        self.assertIn(f"score {B_MIN_SCORE} - {A_MIN_SCORE - 1}", html)
        self.assertIn(f"score below {B_MIN_SCORE}", html)
        self.assertNotIn("Computer Vision", html)
        self.assertNotIn("+25% Price Premium", html)
        # The published accuracy figures are the measured ones, not invented praise.
        self.assertIn("What this grade cannot see", html)
        self.assertIn("assumption", html.lower())
        print("PASS: quality page prints the thresholds and limits the code uses")

    def test_harvesting_check(self):
        response = self.client.post(
            "/api/harvesting/check",
            data=json.dumps({"crop_id": "wheat", "checked_ids": ["w1", "w2", "w3"]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreaterEqual(data.get("score_pct"), 70)
        self.assertIn("verdict", data)
        print("PASS: Harvesting readiness API verified successfully")

    def test_market_calculation(self):
        response = self.client.post(
            "/api/market/calculate",
            data=json.dumps({"crop_id": "wheat", "quantity": 100, "storage_cost": 30}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("current_revenue", data)
        self.assertIn("gross_future_revenue", data)
        self.assertIn("net_gain_loss", data)
        self.assertGreater(len(data.get("mandi_options")), 0)
        print("PASS: Market profit simulator API verified successfully")

    def test_weather_follows_location_and_never_invents_data(self):
        from services.weather_service import get_weather, NO_DATA

        ludhiana = get_weather("ludhiana")
        dehradun = get_weather("Dehradun")
        self.assertNotEqual(ludhiana["location_name"], dehradun["location_name"],
                            "Weather must change when the location changes")

        if ludhiana["degraded"]:
            self.assertEqual(ludhiana["current"]["temperature"], NO_DATA,
                            "A failed live source must blank the readings, not simulate them")
            self.assertEqual(ludhiana["agro"]["spray_status"], "Unavailable")
        else:
            self.assertIsInstance(ludhiana["current"]["temperature"], float)
            self.assertNotIn("Offline", ludhiana["source"])
            self.assertGreater(len(ludhiana["daily"]), 0)

        missing = get_weather("qqzx-not-a-real-place-9999")
        self.assertTrue(missing["degraded"] and missing["invalid_location"])
        self.assertEqual(len(missing["daily"]), 0)
        print("PASS: Weather sourcing contract verified")

if __name__ == "__main__":
    unittest.main()
