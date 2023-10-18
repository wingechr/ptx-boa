# coding: utf-8
import unittest

from ptxboa.api import PtxboaAPI


class TestTemplate(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        cls.api = PtxboaAPI()

    @classmethod
    def tearDownClass(cls):
        pass

    def _test_api_call(self, settings):
        res = self.api.calculate(**settings)
        # test that settings are in results
        for k, v in settings.items():
            if k in ["ship_own_fuel"]:  # skip some
                continue
            self.assertEqual(
                set(res[k].unique()), set([v]), f"wrong data in dimension column: {k}"
            )
        # test expected output columns
        for k in ["values"]:
            self.assertTrue(k in res.columns)

    def test_example_api_call(self):
        settings = {
            "region": "Argentina",
            "country": "China",
            "chain": "Ammonia (AEL)",
            "res_gen": "PV tilted",
            "scenario": "2040 (medium)",
            "secproc_co2": "Direct Air Capture",
            "secproc_water": "Sea Water desalination",
            "transport": "Ship",
            "ship_own_fuel": False,
        }
        self._test_api_call(settings)
