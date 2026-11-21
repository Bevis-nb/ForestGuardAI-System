"""慢速自动演示的状态切换与安全停止。"""
import os
import unittest
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow
from demo_autoplay import DemoController


class DemoAutoplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        self.controller = DemoController(self.window)
        self.app.processEvents()

    def tearDown(self):
        self.controller.stop()
        self.window._auto_ignite_delay.stop()
        self.window.engine.timer.stop()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def advance(self):
        self.controller.timer.stop()
        self.controller._next()
        self.app.processEvents()

    def test_script_shows_actual_fire_and_stops_without_forcing_spray(self):
        c, w = self.controller, self.window
        self.advance()  # login
        w.engine.timer.stop()
        self.assertEqual(w.engine.sim_speed, 1)
        self.assertTrue(w._auto_ignite_delay.isActive())
        self.advance()  # patrol overview
        self.advance()  # wait for normal ignition
        self.assertEqual(c.stage, 1)
        self.assertFalse(w.engine.fires)
        w._auto_ignite_delay.stop()
        w._enable_auto_ignite()
        w.engine._on_tick()
        self.advance()  # detect fire
        self.assertEqual(c.fire_id, w.engine.fires[0].id)
        previous = {r.id: r.spraying for r in w.engine.robots}
        for key in ('navigation', 'collaboration', 'analysis', 'fleet', 'overview'):
            self.advance()
            self.assertEqual(w.dashboard.stack.currentWidget(), w.dashboard.pages[key])
            self.assertEqual({r.id: r.spraying for r in w.engine.robots}, previous)
        self.advance()
        self.assertTrue(c.finished)
        self.assertFalse(c.timer.isActive())

    def test_logout_stops_demo(self):
        self.advance()
        self.window.engine.timer.stop()
        self.window.logout()
        self.advance()
        self.assertTrue(self.controller.finished)
        self.assertIs(self.window.stack.currentWidget(), self.window.login)

    def test_fire_timeout_continues_without_creating_one(self):
        self.advance()
        self.window.engine.timer.stop()
        self.window._auto_ignite_delay.stop()
        self.advance()
        self.controller._wait_elapsed = 40
        self.advance()
        self.assertIsNone(self.controller.fire_id)
        self.assertFalse(self.window.engine.fires)
        self.advance()
        self.assertIs(self.window.dashboard.stack.currentWidget(), self.window.dashboard.pages['navigation'])


if __name__ == '__main__':
    unittest.main()
