"""自动起火必须等登录后的真实时间计时结束。"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow


class LoginFireDelayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.window.engine.timer.stop()

    def tearDown(self):
        self.window._auto_ignite_delay.stop()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_no_auto_ignition_before_login_or_delay(self):
        engine = self.window.engine
        engine.sim_speed = 4
        for _ in range(10):
            engine._on_tick()
        self.assertEqual(engine.fires, [])
        self.window.on_login("admin")
        self.assertTrue(self.window._auto_ignite_delay.isActive())
        self.assertEqual(self.window._auto_ignite_delay.interval(), 10_000)
        for _ in range(10):
            engine._on_tick()
        self.assertEqual(engine.fires, [])
        self.window._auto_ignite_delay.stop()
        self.window._enable_auto_ignite()
        engine._on_tick()
        self.assertTrue(engine.fires)

    def test_logout_cancels_and_login_restarts_delay(self):
        self.window.on_login("admin")
        self.window.logout()
        self.assertFalse(self.window._auto_ignite_delay.isActive())
        self.assertFalse(self.window.engine.auto_ignite_enabled)
        self.window.on_login("admin")
        self.assertTrue(self.window._auto_ignite_delay.isActive())
        self.assertFalse(self.window.engine.auto_ignite_enabled)


if __name__ == "__main__":
    unittest.main()
