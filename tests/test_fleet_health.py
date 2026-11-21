"""装备卡片风险排序、颜色和基地筛选的界面回归。"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from app import theme
from app.pages.fleet import FleetPage
from app.simulation import SimEngine


class FleetHealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.engine = SimEngine()
        self.engine.timer.stop()
        for r in self.engine.robots:
            r.battery, r.temp = 80, 30
        self.page = FleetPage(self.engine)
        self.page.show()
        self.app.processEvents()

    def tearDown(self):
        self.page.close()
        self.page.deleteLater()
        self.app.processEvents()

    def test_live_sort_colours_filter_and_selection(self):
        low, hot, warning = self.engine.robots[0], self.engine.robots[8], self.engine.robots[1]
        low.battery = 10
        hot.temp = 55
        warning.battery = 30
        self.page._select(low.id)
        self.engine.tick.emit()
        self.assertEqual(self.page._visible_order[:3], (low.id, hot.id, warning.id))
        self.assertEqual(self.page.grid.itemAtPosition(0, 0).widget(), self.page.cards[low.id])
        self.assertIn(theme.RED_SOFT, self.page.cards[low.id].styleSheet())
        self.assertIn(theme.RED_SOFT, self.page.cards[hot.id].styleSheet())
        self.assertIn(theme.AMBER_SOFT, self.page.cards[warning.id].styleSheet())
        self.assertEqual(self.page.selected, low.id)
        low.battery = 80
        hot.temp = 30
        self.engine.tick.emit()
        self.assertEqual(self.page._visible_order[0], warning.id)
        self.assertNotIn(theme.RED_SOFT, self.page.cards[low.id].styleSheet())
        self.assertEqual(self.page.selected, low.id)
        self.page.base_filter.setCurrentIndex(1)
        self.assertEqual(self.page._visible_order[0], warning.id)
        self.assertTrue(self.page.cards[hot.id].isHidden())
        self.assertEqual(self.page.grid.itemAtPosition(0, 0).widget(), self.page.cards[warning.id])
        self.page.base_filter.setCurrentIndex(0)
        self.assertFalse(self.page.cards[hot.id].isHidden())


if __name__ == "__main__":
    unittest.main()
