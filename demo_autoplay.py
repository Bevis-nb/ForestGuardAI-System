"""ForestGuard AI 慢速自动演示（仅仿真，不适用于实战）。

运行：python demo_autoplay.py
演示自动登录并依次展示巡逻、自动起火、路径、协作、火情与装备管理。
所有设备均使用真实的仿真状态机，不强制瞬移、喷洒或扑灭。
"""
from __future__ import annotations

import sys

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QApplication

from app import config, theme
from app.main_window import MainWindow
from app.widgets import toast


class DemoController(QObject):
    """使用窗口持有的单次定时器切换页面，退出或关闭时不再推进。"""

    def __init__(self, window: MainWindow):
        super().__init__(window)
        self.window = window
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._next)
        self.stage = -1
        self.fire_id: str | None = None
        self._wait_elapsed = 0
        self.finished = False
        self.steps = (
            (self._login, 10_000),
            (self._overview, 12_000),
            (self._wait_for_fire, 0),
            (self._navigation, 20_000),
            (self._collaboration, 20_000),
            (self._analysis, 25_000),
            (self._fleet, 20_000),
            (self._return_overview, 15_000),
            (self._finish, 0),
        )

    def start(self) -> None:
        if self.stage != -1 or self.finished:
            return
        self.timer.start(3_000)  # 先展示登录界面

    def stop(self) -> None:
        self.timer.stop()
        self.finished = True

    def _next(self) -> None:
        if self.finished or not self.window.isVisible():
            self.stop()
            return
        # 用户退出登录时，不再自动切换或重新登录。
        if self.stage >= 0 and self.window.stack.currentWidget() is not self.window.dashboard:
            self.stop()
            return
        self.stage += 1
        if self.stage >= len(self.steps):
            self.stop()
            return
        action, delay = self.steps[self.stage]
        action()
        if delay and not self.finished:
            self.timer.start(delay)

    def _login(self) -> None:
        self.window.on_login("admin")
        # 演示保持慢速，不修改保存的用户配置。
        self.window.engine.sim_speed = 1
        self.window.engine.timer.setInterval(1000)
        self.window.dashboard.pages["overview"].speed_btn.setText("1× 倍速")

    def _overview(self) -> None:
        self.window.navigate_to("overview")
        toast(self.window, "自动演示：观察基地出发与巡逻轮岗", "info")

    def _wait_for_fire(self) -> None:
        """等待正常自动起火，超过等待时间也继续演示，不制造假火情。"""
        e = self.window.engine
        active = sorted((f for f in e.fires if f.state != "extinguished"), key=lambda f: f.ignited_at)
        if active:
            self.fire_id = active[0].id
        if active or self._wait_elapsed >= 40:
            toast(self.window, "自动演示：展示实时任务和协作" if active else "暂未发现活跃火点，继续展示界面", "info")
            self.timer.start(8_000)
        else:
            self._wait_elapsed += 1
            self.stage -= 1
            self.timer.start(1_000)

    def _navigation(self) -> None:
        self.window.navigate_to("navigation")
        page = self.window.dashboard.pages["navigation"]
        units = self.window.engine.active_fire_robots(self.fire_id) if self.fire_id else []
        moving = next((r for r in units if r.mission in ("en_route", "recon") and not r.route_failed), None)
        if moving:
            page._on_robot_selected(moving.id)
        toast(self.window, "自主导航：每台装备使用自己的规划路线", "info")

    def _collaboration(self) -> None:
        self.window.navigate_to("collaboration")
        page = self.window.dashboard.pages["collaboration"]
        if self.fire_id:
            index = page.fire_filter.findData(self.fire_id)
            if index >= 0:
                page.fire_filter.setCurrentIndex(index)
        toast(self.window, "多机协作：查看实际编组、任务与协作日志", "info")

    def _analysis(self) -> None:
        self.window.navigate_to("analysis")
        page = self.window.dashboard.pages["analysis"]
        if self.fire_id:
            page._select_fire(self.fire_id)
        toast(self.window, "火情分析：查看预测、隔离带及投入力量", "info")

    def _fleet(self) -> None:
        self.window.navigate_to("fleet")
        page = self.window.dashboard.pages["fleet"]
        units = self.window.engine.active_fire_robots(self.fire_id) if self.fire_id else []
        if units:
            page._select(units[0].id)
        toast(self.window, "装备管理：查看任务、电量与温度", "info")

    def _return_overview(self) -> None:
        self.window.navigate_to("overview")
        toast(self.window, "返回总览：火情和装备将继续自动演练", "info")

    def _finish(self) -> None:
        toast(self.window, "自动演示结束，可继续手动查看；仿真仍在运行", "success")
        self.stop()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("ForestGuard AI")
    app.setStyle("Fusion")
    cfg = config.load()
    theme.set_accent(cfg.get("accent", "森林绿"))
    theme.set_density(bool(cfg.get("compact")))
    theme.ANIMATIONS = bool(cfg.get("animations", True))
    theme.apply_theme(app)
    win = MainWindow()
    controller = DemoController(win)
    win.show()
    controller.start()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
