"""ForestGuard AI 智护森林 —— 程序入口。

运行：
    python main.py
依赖：
    pip install -r requirements.txt
"""
from __future__ import annotations

import os
import sys

# 在创建 QApplication 之前抑制 WebEngine 的底层网络日志
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-webrtc --disable-logging --log-level=3")

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app import config, theme
from app.theme import apply_theme
from app.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("ForestGuard AI")
    app.setOrganizationName("ForestGuard")
    app.setWindowIcon(QIcon("logo.ico"))

    # Fusion 风格可保证 QSS 在各平台表现一致
    app.setStyle("Fusion")

    # 读取用户偏好（主题色 / 信息密度 / 动效）
    cfg = config.load()
    theme.set_accent(cfg.get("accent", "森林绿"))
    theme.set_density(bool(cfg.get("compact")))
    theme.ANIMATIONS = bool(cfg.get("animations", True))
    apply_theme(app)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
