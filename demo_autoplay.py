"""全自动演示脚本：自动登录并依次演示「随机起火 → 自主协同 → 4×扑救扑灭 → 3D 遥控视角」。

用法：
    python demo_autoplay.py
启动后可直接用 Win+G / OBS 录屏，全程约 35 秒自动完成。
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

    # 1. 自动登录进入指挥总览 (1.2s)
    QTimer.singleShot(1200, lambda: win.on_login("admin"))

    # 2. 触发随机起火 + 切换 4× 倍速 (3.2s)
    def step_ignite():
        win.engine.sim_speed = 4
        f = win.engine.ignite_random_fire()
        ov = win.dashboard.pages.get("overview")
        if ov and hasattr(ov, "speed_btn"):
            ov.speed_btn.setText("4× 倍速")
            ov.map.highlight_fire()
        toast(win, f"演示：随机触发火点 {f.id}，已开启 4× 推演", "warning")

    QTimer.singleShot(3200, step_ignite)

    # 3. 切换到「多机器人协作」展示自主调度与评判标准 (7.5s)
    QTimer.singleShot(
        7500,
        lambda: (
            win.navigate_to("collaboration"),
            toast(win, "演示：查看自主协同调度与 4 维评判标准", "info"),
        ),
    )

    # 4. 回到「指挥总览」观看机器人扑救与火点扑灭 (12.5s)
    QTimer.singleShot(
        12500,
        lambda: (
            win.navigate_to("overview"),
            toast(win, "演示：空地编队正在压制火势直至完全扑灭", "info"),
        ),
    )

    # 5. 切到「装备管理」并打开 3D 第一人称遥控视角 (22.0s)
    def step_3d():
        win.navigate_to("fleet")
        robot = win.engine.robots[0]
        dlg = RemoteControlDialog(win.engine, robot, win)
        dlg.show()
        dlg.feed.spraying = True
        dlg_holder.append(dlg)
        toast(win, "演示：3D 第一人称遥控终端（自动左右巡航视角）", "success")

        # 自动左右转动 3D 视角展示
        for i in range(10):
            QTimer.singleShot(800 + i * 500, lambda idx=i: dlg.feed.pan(
                dyaw=0.14 if idx < 5 else -0.14,
                dz=0.15 if idx < 5 else -0.1,
            ))

    QTimer.singleShot(22000, step_3d)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
