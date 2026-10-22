import unittest
import json
import os
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

    def test_disease_detection_sample(self):
        response = self.client.post("/api/disease/detect", data={"sample_file": "early_blight_leaf.jpg", "crop_hint": "tomato"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("Early Blight", data.get("name"))
        self.assertGreater(data.get("confidence"), 80)
        self.assertGreater(len(data.get("organic_remedies")), 0)
        self.assertGreater(len(data.get("chemical_treatments")), 0)
        print("PASS: Disease detection API verified successfully")

    def test_quality_assessment_sample(self):
        response = self.client.post("/api/quality/assess", data={"sample_file": "grade_a_crop.jpg", "crop_name": "Tomato"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("grade"), "A")
        self.assertGreater(data.get("overall_score"), 80)
        print("PASS: Crop Quality Assessment API verified successfully")

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

if __name__ == "__main__":
    unittest.main()
