"""导航页每设备设置及地图共用路线的界面测试。"""
import os
import unittest
from unittest.mock import patch
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from app.canvas import TerrainMap
from app.pages.navigation import NavPage
from app.simulation import SimEngine


class NavigationPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.engine = SimEngine()
        self.engine.timer.stop()
        self.page = NavPage(self.engine)
        self.page.show()
        self.app.processEvents()

    def tearDown(self):
        self.page.close()
        self.page.deleteLater()
        self.app.processEvents()

    def test_overview_does_not_draw_routes(self):
        overview = TerrainMap(self.engine, "overview")
        overview.resize(600, 400)
        overview.show()
        self.app.processEvents()
        with patch.object(overview, "_paint_path") as paint_path:
            overview.grab()
            paint_path.assert_not_called()
        overview.close()
        overview.deleteLater()

    def test_overview_shows_only_valid_spray_without_routes(self):
        fire = self.engine.ignite_random_fire((.5, .5))
        robot = self.engine.active_fire_robots(fire.id)[0]
        robot.x, robot.y = fire.origin
        robot.mission, robot.spraying = "spraying", True
        overview = TerrainMap(self.engine, "overview")
        overview.resize(600, 400)
        overview.show()
        self.app.processEvents()
        with patch.object(overview, "_paint_path") as path, \
             patch.object(overview, "_paint_spray", wraps=overview._paint_spray) as spray, \
             patch.object(self.engine, "spray_target", wraps=self.engine.spray_target) as target:
            overview.grab()
            path.assert_not_called()
            spray.assert_called()
            self.assertTrue(any(call.args[0] is robot for call in target.call_args_list))
        self.assertIs(self.engine.spray_target(robot), fire)
        robot.x, robot.y = .1, .1
        self.assertIsNone(self.engine.spray_target(robot))
        overview.close()
        overview.deleteLater()

    def test_selected_route_displays_finish_flag(self):
        fire = self.engine.ignite_random_fire((.5, .5))
        robot = self.engine.active_fire_robots(fire.id)[0]
        self.page._on_robot_selected(robot.id)
        expected = self.page.map.pt(self.engine.remaining_route(robot)[-1])
        with patch.object(self.page.map, "_draw_route_finish", wraps=self.page.map._draw_route_finish) as flag:
            self.page.map.grab()
            flag.assert_called_once()
            self.assertEqual(flag.call_args.args[1], expected)
        robot.mission = "idle"
        with patch.object(self.page.map, "_draw_route_finish") as flag:
            self.page.map.grab()
            flag.assert_not_called()

    def test_independent_selection_and_shared_maps(self):
        a, b = self.engine.robots[:2]
        fire = self.engine.ignite_random_fire((.5, .5))
        self.page.robot_picker.setCurrentIndex(self.page.robot_picker.findData(a.id))
        self.page.algo.setCurrentIndex(2)
        self.assertEqual(a.route_algo, "Dijkstra")
        self.page.robot_picker.setCurrentIndex(self.page.robot_picker.findData(b.id))
        self.page.algo.setCurrentIndex(1)
        self.assertEqual(b.route_algo, "A*")
        self.page.robot_picker.setCurrentIndex(self.page.robot_picker.findData(a.id))
        self.assertEqual(self.page.algo.currentIndex(), 2)
        self.assertEqual(self.page.map.selected_robot, a.id)
        map2 = TerrainMap(self.engine, "overview")
        self.assertIs(map2.engine, self.page.map.engine)
        self.assertEqual(map2.engine.remaining_route(a), self.page.map.engine.remaining_route(a))
        self.page.map.grab()
        map2.grab()
        map2.deleteLater()


if __name__ == "__main__":
    unittest.main()
