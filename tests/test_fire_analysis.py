"""火点选择、推演与无火情状态的回归测试。"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from app.canvas import VideoFeed, feed_pixmap
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

    def test_all_fires_painted_and_assigned_force_icons(self):
        a = self.engine.ignite_random_fire((0.25, 0.3))
        b = self.engine.ignite_random_fire((0.75, 0.7))
        drone = next(r for r in self.engine.robots if r.assigned_fire_id == a.id and r.kind == "UAV")
        robot = next(r for r in self.engine.robots if r.assigned_fire_id == a.id and r.kind == "UGV")
        self.page._select_fire(a.id)
        self.page.map.grab()
        self.assertEqual(set(self.page.map._prediction["fires"]), {a.id, b.id})
        self.assertEqual(self.page.force_count.text(), "5 台")
        drone_row = self.page.findChild(QWidget, "force_" + drone.id)
        robot_row = self.page.findChild(QWidget, "force_" + robot.id)
        self.assertIsNotNone(drone_row.findChild(QWidget, "drone_icon"))
        self.assertIsNotNone(robot_row.findChild(QWidget, "robot_icon"))
        self.page._select_fire(b.id)
        self.assertEqual(self.page.force_count.text(), "5 台")
        b.state = "extinguished"
        self.page._refresh()
        self.page.map.grab()
        self.assertEqual(set(self.page.map._prediction["fires"]), {a.id})

    def test_automatic_dispatch_shows_equipment(self):
        fire = self.engine.ignite_random_fire((0.4, 0.4))
        self.page._refresh()
        self.app.processEvents()
        assigned = [r for r in self.engine.robots if r.assigned_fire_id == fire.id]
        self.assertEqual(self.page.force_count.text(), f"{len(assigned)} 台")
        self.assertEqual(self.page.force_text.text(), "当前火点已投入装备")
        for robot in assigned:
            row = self.page.findChild(QWidget, "force_" + robot.id)
            self.assertIsNotNone(row)
            self.assertTrue(row.isVisible())

    def test_force_strip_count_and_repeated_updates(self):
        fire = self.engine.ignite_random_fire((0.4, 0.4))
        self.page._select_fire(fire.id)
        self.app.processEvents()
        assigned = [r for r in self.engine.robots if r.assigned_fire_id == fire.id]
        self.assertEqual(self.page.force_count.text(), f"{len(assigned)} 台")
        self.assertEqual(self.page.force_rows.count(), len(assigned))
        self.assertTrue(self.page.force_strip.isVisible())
        robot = assigned[0]
        for battery in (70, 55, 30):
            robot.battery = battery
            self.engine.tick.emit()
            self.app.processEvents()
            row = self.page.findChild(QWidget, "force_" + robot.id)
            self.assertIsNotNone(row)
            self.assertIn(str(battery), row.findChild(QLabel, "force_battery").text())
            self.assertEqual(self.page.force_count.text(), f"{len(assigned)} 台")
        robot.status = "offline"
        self.engine.tick.emit()
        self.app.processEvents()
        self.assertEqual(self.page.force_count.text(), f"{len(assigned) - 1} 台")
        self.assertIsNone(self.page.findChild(QWidget, "force_" + robot.id))
        for r in assigned:
            r.assigned_fire_id = ""
        self.engine.tick.emit()
        self.app.processEvents()
        self.assertEqual(self.page.force_count.text(), "0 台")
        self.assertTrue(self.page.force_strip.isVisible())

    def test_video_feed_tracks_fire_and_channel(self):
        view = self.page.cam
        self.assertFalse(view._has_active_fire())
        eo_clear = feed_pixmap("eo", False)
        ir_clear = feed_pixmap("ir", False)
        eo_fire = feed_pixmap("eo", True)
        ir_fire = feed_pixmap("ir", True)
        for pixmap in (eo_clear, ir_clear, eo_fire, ir_fire):
            self.assertFalse(pixmap.isNull())
        self.assertNotEqual(eo_clear.cacheKey(), eo_fire.cacheKey())
        self.assertNotEqual(ir_clear.cacheKey(), ir_fire.cacheKey())
        view.set_thermal(True)
        self.assertEqual(view.mode, "ir")
        view.grab()
        first = self.engine.ignite_random_fire((0.3, 0.3))
        second = self.engine.ignite_random_fire((0.7, 0.7))
        self.assertTrue(view._has_active_fire())
        view.grab()
        first.state = "extinguished"
        self.assertTrue(view._has_active_fire())
        second.state = "extinguished"
        self.engine.tick.emit()
        self.assertFalse(view._has_active_fire())
        view.set_thermal(False)
        view.grab()
        # VideoFeed 也允许不传引擎，应使用无火情场景而不抛异常。
        standalone = VideoFeed()
        standalone.grab()
        self.assertFalse(standalone._has_active_fire())
        standalone.deleteLater()

    def test_analysis_panel_sizes_stay_stable_when_fire_changes(self):
        self.app.processEvents()
        panels = (self.page.vision_panel, self.page.spread_panel, self.page.decision_panel)
        before = [panel.size() for panel in panels]
        strip_height = self.page.force_strip.height()
        fire = self.engine.ignite_random_fire((0.4, 0.4))
        self.page._refresh()
        self.app.processEvents()
        self.assertEqual([panel.size() for panel in panels], before)
        self.assertEqual(self.page.force_strip.height(), strip_height)
        fire.state = "extinguished"
        self.page._refresh()
        self.app.processEvents()
        self.assertEqual([panel.size() for panel in panels], before)
        self.assertEqual(self.page.force_strip.height(), strip_height)

    def test_suspicious_fire_is_tracked(self):
        fire = self.engine.trigger_suspicious_fire((0.4, 0.4))
        self.assertIn(fire, self.engine.fires)
        self.page._refresh()
        self.assertEqual(self.page.selected_fire_id, fire.id)
        self.assertIn("核实", self.page.strategy_text.text())


if __name__ == '__main__':
    unittest.main()
