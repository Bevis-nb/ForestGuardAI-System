"""导航页每设备设置及地图共用路线的界面测试。"""
import os
import unittest
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
