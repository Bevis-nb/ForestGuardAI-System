"""协作页面使用实时状态和筛选后的真实日志。"""
import os
import unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from app.pages.collaboration import CollaborationPage
from app.simulation import SimEngine


class CollaborationPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.engine = SimEngine()
        self.engine.timer.stop()
        self.page = CollaborationPage(self.engine)
        self.page.show()
        self.app.processEvents()

    def tearDown(self):
        self.page.close()
        self.page.deleteLater()
        self.app.processEvents()

    def test_multifire_filter_live_updates_and_reset(self):
        self.assertEqual(self.page.team_table.rowCount(), 0)
        self.assertEqual(self.page.log_table.rowCount(), 0)
        first = self.engine.ignite_random_fire((.3, .4))
        second = self.engine.ignite_random_fire((.7, .4))
        self.engine.tick.emit()
        self.assertEqual(self.page.team_table.rowCount(), 2)
        self.assertEqual(self.page.unit_table.rowCount(), 10)
        self.assertEqual(self.page.s_air._value.text(), '4')
        self.assertEqual(self.page.s_ground._value.text(), '6')
        self.page.fire_filter.setCurrentIndex(self.page.fire_filter.findData(first.id))
        self.assertEqual(self.page.team_table.rowCount(), 1)
        self.assertEqual(self.page.unit_table.rowCount(), 5)
        self.assertTrue(all(self.page.log_table.item(i, 1).text() == first.id
                            for i in range(self.page.log_table.rowCount())))
        self.assertEqual(self.page.unit_table.item(0, 0).text(), first.id)
        first.state = 'extinguished'
        self.engine.tick.emit()
        self.assertEqual(self.page.team_table.rowCount(), 0)
        self.assertEqual(self.page.unit_table.rowCount(), 0)
        self.assertEqual(self.page.fire_filter.currentData(), first.id)  # historical logs retained
        self.assertGreater(self.page.log_table.rowCount(), 0)
        self.engine.reset_session()
        self.assertEqual(self.page.fire_filter.currentData(), '')
        self.assertEqual(self.page.log_table.rowCount(), 0)
        self.assertEqual(self.page.s_fires._value.text(), '0')


if __name__ == '__main__':
    unittest.main()
