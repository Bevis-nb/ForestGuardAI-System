"""多火点燃烧区合并及隔离带避让（不依赖 GUI）。"""
import unittest

from app.simulation import FireIncident, FireSpreadModel


class MultiFireSpreadTests(unittest.TestCase):
    def setUp(self):
        self.model = FireSpreadModel()
        self.a = FireIncident(id="A-01", origin=(0.3, 0.5))
        self.b = FireIncident(id="A-02", origin=(0.55, 0.5))

    def test_union_and_fire_removal(self):
        result = self.model.assess_all([self.a, self.b], 30, 0, 4, 30)
        ga = self.model.assess(self.a, 30, 0, 4, 30)["grid"]
        gb = self.model.assess(self.b, 30, 0, 4, 30)["grid"]
        for y, row in enumerate(result["grid"]):
            for x, value in enumerate(row):
                self.assertEqual(value, max(ga[y][x], gb[y][x]))
        self.assertEqual(set(result["fires"]), {self.a.id, self.b.id})
        self.assertGreaterEqual(result["area"], result["fires"][self.a.id]["area"])
        self.b.state = "extinguished"
        result = self.model.assess_all([self.a, self.b], 30, 0, 4, 30)
        self.assertEqual(set(result["fires"]), {self.a.id})
        self.assertEqual(result["grid"], ga)
        self.assertEqual(self.model.assess_all([self.b], 30, 0, 4, 30)["grid"], [])

    def test_isolation_considers_other_fire_and_wind(self):
        alone = self.model.assess_all([self.a], 30, 0, 4, 30)
        together = self.model.assess_all([self.a, self.b], 30, 0, 4, 30)
        first = alone["fires"][self.a.id]["line"]
        joint = together["fires"][self.a.id]["line"]
        self.assertNotEqual(first, joint)
        self.assertFalse(together["fires"][self.a.id]["line_conflict"])
        changed = self.model.assess_all([self.a, self.b], 60, 90, 7, 30)
        self.assertNotEqual(together["grid"], changed["grid"])
        self.assertNotEqual(joint, changed["fires"][self.a.id]["line"])


if __name__ == "__main__":
    unittest.main()
