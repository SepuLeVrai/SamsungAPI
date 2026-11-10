"""Unit tests for Samsung REST state filtering, without HA dependencies."""

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "samsung_tv_true_power"
    / "power_logic.py"
)
spec = importlib.util.spec_from_file_location("power_logic", MODULE_PATH)
logic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logic)


class TestSamsungPowerLogic(unittest.TestCase):
    def test_first_tv_on_payload(self):
        payload = {"device": {"model": "example_tizen_device", "PowerState": "on", "name": ""}}
        self.assertEqual(logic.parse_power_state(payload), "on")

    def test_first_tv_standby_payload(self):
        payload = {"device": {"modelName": "Samsung Tizen Model A", "PowerState": "standby"}}
        self.assertEqual(logic.parse_power_state(payload), "standby")

    def test_second_tv_on_and_standby(self):
        model = "Samsung Tizen Model B"
        for state in ("on", "standby"):
            self.assertEqual(
                logic.parse_power_state({"device": {"modelName": model, "PowerState": state}}),
                state,
            )

    def test_off_aliases(self):
        self.assertEqual(logic.parse_power_state({"device": {"PowerState": "OFF"}}), "off")
        self.assertEqual(logic.parse_power_state({"device": {"PowerState": "poweroff"}}), "poweroff")

    def test_missing_or_unrecognized_power_state(self):
        self.assertEqual(logic.parse_power_state({"device": {"PowerState": "awake"}}), "unsupported")
        self.assertEqual(logic.parse_power_state({"device": {}}), "unsupported")
        self.assertEqual(logic.parse_power_state("OK"), "unsupported")
        self.assertEqual(logic.parse_power_state({"device": []}), "unsupported")

    def test_spurious_on_shorter_than_confirmation(self):
        f = logic.PowerFilter(on_confirm_seconds=15, offline_off_seconds=30)
        self.assertFalse(f.update("standby", 0))
        self.assertFalse(f.update("on", 1))
        self.assertFalse(f.update("on", 10))
        self.assertFalse(f.update("standby", 14))
        self.assertFalse(f.update("on", 20))
        self.assertFalse(f.update("on", 34))
        self.assertTrue(f.update("on", 35))

    def test_continuous_on_and_immediate_standby(self):
        f = logic.PowerFilter(on_confirm_seconds=15, offline_off_seconds=30)
        self.assertFalse(f.update("on", 0))
        self.assertTrue(f.update("on", 15))
        self.assertFalse(f.update("standby", 20))

    def test_standby_during_network_wake_stays_off(self):
        f = logic.PowerFilter(on_confirm_seconds=5, offline_off_seconds=30)
        for sec in range(0, 120, 5):
            self.assertFalse(f.update("standby", sec))

    def test_unreachable_off_after_grace(self):
        f = logic.PowerFilter(on_confirm_seconds=5, offline_off_seconds=30)
        f.update("on", 0)
        self.assertTrue(f.update("on", 5))
        self.assertTrue(f.update("unreachable", 10))
        self.assertTrue(f.update("unreachable", 39))
        self.assertFalse(f.update("unreachable", 40))

    def test_connection_recovery_resets_timeout(self):
        f = logic.PowerFilter(on_confirm_seconds=5, offline_off_seconds=30)
        f.update("on", 0)
        f.update("on", 5)
        f.update("unreachable", 10)
        f.update("on", 20)
        self.assertTrue(f.update("unreachable", 30))
        self.assertTrue(f.update("unreachable", 50))
        self.assertFalse(f.update("unreachable", 60))

    def test_unsupported_is_unknown_not_on(self):
        f = logic.PowerFilter(on_confirm_seconds=5, offline_off_seconds=30)
        f.update("on", 0)
        f.update("on", 5)
        self.assertIsNone(f.update("unsupported", 10))
        self.assertFalse(f.update("on", 20))

    def test_initially_offline_becomes_assumed_off(self):
        f = logic.PowerFilter(on_confirm_seconds=5, offline_off_seconds=30)
        self.assertIsNone(f.update("unreachable", 0))
        self.assertIsNone(f.update("unreachable", 20))
        self.assertFalse(f.update("unreachable", 30))


if __name__ == "__main__":
    unittest.main()
