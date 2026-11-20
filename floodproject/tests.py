from django.test import TestCase
from django.urls import reverse
from unittest.mock import Mock, patch
import requests


class WaterLevelDataTests(TestCase):
    def test_uses_ehyd_fallback_when_legacy_wfs_returns_invalid_json(self):
        legacy_response = Mock()
        legacy_response.json.side_effect = ValueError("Invalid JSON")
        fallback_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [13.9, 48.2]},
                    "properties": {"hzbnr": 123, "wert": "4.2", "zp": "2026-11-19T12:30:00"},
                }
            ],
        }
        fallback_response = Mock()
        fallback_response.json.return_value = fallback_data

        with patch(
            "floodproject.views.requests.get",
            side_effect=[legacy_response, fallback_response],
        ) as get:
            response = self.client.get(reverse("water_level_data"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), fallback_data)
        self.assertEqual(get.call_count, 2)
        self.assertEqual(
            get.call_args_list[1].args[0],
            "https://ehyd.gv.at/services/PegelAktuell/json",
        )

    def test_returns_gateway_error_when_all_sources_fail(self):
        with patch(
            "floodproject.views.requests.get",
            side_effect=[requests.Timeout("legacy timed out"), requests.ConnectionError("eHYD unavailable")],
        ):
            response = self.client.get(reverse("water_level_data"))

        self.assertEqual(response.status_code, 502)
        self.assertIn("error", response.json())
