"""火点选择、推演与无火情状态的回归测试。"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from app.pages.analysis import AnalysisPage
from app.simulation import SimEngine


class FireAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.engine = SimEngine()
        self.engine.timer.stop()
        self.page = AnalysisPage(self.engine)
        self.page.resize(1500, 900)
        self.page.show()
        self.app.processEvents()

    def tearDown(self):
        self.page.close()
        self.page.deleteLater()
        self.app.processEvents()

    def test_empty_and_first_fire_default(self):
        self.assertIsNone(self.page.selected_fire_id)
        self.assertEqual(self.page.fire_info.text(), "无火情")
        first = self.engine.ignite_random_fire((0.3, 0.3))
        self.engine.sim_time += 1
        second = self.engine.ignite_random_fire((0.7, 0.7))
        self.page._refresh()
        self.assertEqual(self.page.selected_fire_id, first.id)
        self.assertNotEqual(self.page.selected_fire_id, second.id)
        self.assertFalse(self.page.map._show_robots)
        self.page.map.grab()  # exercise the full heat/line paint path

    def test_click_select_extinguish_and_fallback(self):
        first = self.engine.ignite_random_fire((0.3, 0.3))
        self.engine.sim_time += 1
        second = self.engine.ignite_random_fire((0.7, 0.7))
        first.intensity, second.intensity = 80, 20
        self.page._refresh()
        first_strategy = self.page.strategy_text.text()
        pos = self.page.map.pt(second.origin).toPoint()
        QTest.mouseClick(self.page.map, Qt.MouseButton.LeftButton, pos=pos)
        self.assertEqual(self.page.selected_fire_id, second.id)
        self.assertIn(second.id, self.page.fire_info.text())
        self.assertNotEqual(first_strategy, self.page.strategy_text.text())
        self.page.map.grab()
        second.state = "extinguished"
        self.page._refresh()
        self.assertEqual(self.page.selected_fire_id, first.id)
        first.state = "extinguished"
        self.page._refresh()
        self.assertIsNone(self.page.selected_fire_id)
        self.assertEqual(self.page.strategy_pill.text(), "●  无火情")
        self.assertEqual(self.page.iso_text.text(), "暂无建议")

    def test_prediction_uses_fire_and_time(self):
        a = self.engine.ignite_random_fire((0.25, 0.3))
        b = self.engine.ignite_random_fire((0.75, 0.7))
        model = self.engine.spread_model
        p1 = model.assess(a, 30, 45, 5, 30)
        p2 = model.assess(b, 30, 45, 5, 30)
        p3 = model.assess(a, 90, 45, 5, 30)
        self.assertNotEqual(p1['line'], p2['line'])
        self.assertGreater(p3['area'], p1['area'])
        self.assertTrue(all(0 <= n <= 1 for pt in p1['line'] for n in pt))
        self.engine.wind_deg, self.engine.wind_speed, self.engine.humidity = 45, 5, 30
        self.page._select_fire(a.id)
        self.page.slider.setValue(3)
        self.assertIn(f"{p3['area']:.1f}", self.page.m_area.text_label.text())

    def test_suspicious_fire_is_tracked(self):
        fire = self.engine.trigger_suspicious_fire((0.4, 0.4))
        self.assertIn(fire, self.engine.fires)
        self.page._refresh()
        self.assertEqual(self.page.selected_fire_id, fire.id)
        self.assertIn("核实", self.page.strategy_text.text())


if __name__ == '__main__':
    unittest.main()
