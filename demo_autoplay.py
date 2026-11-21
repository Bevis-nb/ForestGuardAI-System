"""全自动演示脚本（慢速清晰版）：依次演示「预警勘察流程」与「突发扑救扑灭流程 + 3D 遥控」。

用法：
    python demo_autoplay.py
"""
from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app import theme
from app.main_window import MainWindow
from app.pages.fleet import RemoteControlDialog
from app.widgets import toast


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    theme.apply_theme(app)

    win = MainWindow()
    win.show()
    dlg_holder: list[RemoteControlDialog] = []

    # 1. 管理员登录 (2.0s)
    QTimer.singleShot(2000, lambda: win.on_login("admin"))

    # 2. 流程一：火灾预警（可疑火点）→ 派无人机前往勘察 (5.0s)
    def step_suspicious():
        win.engine.sim_speed = 2
        ov = win.dashboard.pages.get("overview")
        if ov and hasattr(ov, "speed_btn"):
            ov.speed_btn.setText("2× 倍速")
        f = win.engine.trigger_suspicious_fire()
        if ov:
            ov.map.highlight_fire()
        toast(win, f"流程一：发现可疑火点 {f.id}，已派无人机前往勘察", "warning")

    QTimer.singleShot(5000, step_suspicious)

    # 3. 展示自主调度推荐与评判标准 (13.0s)
    QTimer.singleShot(
        13000,
        lambda: (
            win.navigate_to("collaboration"),
            toast(win, "查看设备调度推荐算法与 4 维评判标准", "info"),
        ),
    )

    # 4. 流程二：突发随机起火 → 自动调度 → 2× 扑救扑灭 (19.0s)
    def step_ignite():
        win.navigate_to("overview")
        f = win.engine.ignite_random_fire()
        ov = win.dashboard.pages.get("overview")
        if ov:
            ov.map.highlight_fire()
        toast(win, f"流程二：突发火点 {f.id}，已按调度方案派出空地编队 2× 扑救", "error")

    QTimer.singleShot(19000, step_ignite)

    # 5. 打开 3D 遥控视角演示现场扑火 (36.0s)
    def step_3d():
        win.navigate_to("fleet")
        robot = win.engine.robots[0]
        dlg = RemoteControlDialog(win.engine, robot, win)
        dlg.show()
        dlg.feed.spraying = True
        dlg_holder.append(dlg)
        toast(win, "3D 第一人称遥控视角：正在喷水扑救", "success")
        for i in range(12):
            QTimer.singleShot(1000 + i * 700, lambda idx=i: dlg.feed.pan(
                dyaw=0.12 if idx < 6 else -0.12,
                dz=0.12 if idx < 6 else -0.08,
            ))

    QTimer.singleShot(36000, step_3d)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
