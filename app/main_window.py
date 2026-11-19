"""亮色系主窗口：登录 → 指挥控制台（侧边导航 + 多页面）。"""
from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from . import icons, theme
from .pages.analysis import AnalysisPage
from .pages.collaboration import CollaborationPage
from .pages.fleet import FleetPage
from .pages.interaction import InteractionPage
from .pages.login import LoginPage
from .pages.map_page import MapPage
from .pages.navigation import NavPage
from .pages.overview import OverviewPage
from .pages.settings import SettingsPage
from .simulation import SimEngine
from .widgets import Avatar, IconTile, Pill, icon_button, label, set_prop, toast

APP_NAME = "智护森林 · ForestGuard AI"
NAV_GROUPS = [
    ("指挥中心", [("overview", "指挥总览", "overview"),
                  ("map", "火情地图", "map")]),
    ("智能决策", [("navigation", "自主导航", "route"),
                  ("collaboration", "多机协作", "users"),
                  ("analysis", "火情分析", "flame"),
                  ("interaction", "人机交互", "chat")]),
    ("系统", [("fleet", "装备管理", "robot"),
              ("settings", "系统设置", "settings")]),
]
TITLES = {key: title for _, items in NAV_GROUPS for key, title, _ in items}


class NavButton(QPushButton):
    def __init__(self, key: str, text: str, icon_name: str, parent=None):
        super().__init__(text, parent)
        self.key = key
        self.setProperty("variant", "nav")
        self.setProperty("active", "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setIcon(icons.icon(icon_name, theme.MUTED, 18))
        self.setIconSize(QSize(18, 18))
        self._icon_name = icon_name

    def set_active(self, active: bool):
        set_prop(self, "active", "true" if active else "false")
        color = theme.ACCENT_DARK if active else theme.MUTED
        self.setIcon(icons.icon(self._icon_name, color, 18))


class TitleBar(QFrame):
    def __init__(self, window: "MainWindow", engine: SimEngine, parent=None):
        super().__init__(parent)
        self.window_ref = window
        self.setObjectName("TitleBar")
        self.setFixedHeight(58)
        self.setStyleSheet(
            f"#TitleBar {{ background:{theme.SURFACE}; border-bottom:1px solid {theme.BORDER};"
            f" border-top-left-radius:14px; border-top-right-radius:14px; }}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 10, 0)
        lay.setSpacing(10)

        mark = QLabel()
        mark.setFixedSize(32, 32)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setPixmap(icons.pixmap("leaf", "#FFFFFF", 18))
        mark.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1CBB7C, stop:1 #0B8455);"
            "border-radius:10px;"
        )
        lay.addWidget(mark)
        brand = QVBoxLayout()
        brand.setSpacing(0)
        brand.addWidget(label("智护森林", None, size=14, weight=700))
        brand.addWidget(label("ForestGuard AI 指挥控制台", "caption"))
        lay.addLayout(brand)

        lay.addSpacing(18)
        self.crumb = label("指挥中心 / 指挥总览", "caption", color=theme.MUTED)
        lay.addWidget(self.crumb)
        lay.addStretch(1)

        self.chip_link = Pill("全链路在线", "success")
        lay.addWidget(self.chip_link)
        self.chip_risk = Pill("火险 82", "warning")
        lay.addWidget(self.chip_risk)

        clock_col = QVBoxLayout()
        clock_col.setSpacing(0)
        self.time_label = label("--:--:--", None, size=13, weight=700)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.date_label = label("", "caption", color=theme.MUTED)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        clock_col.addWidget(self.time_label)
        clock_col.addWidget(self.date_label)
        lay.addSpacing(8)
        lay.addLayout(clock_col)

        lay.addSpacing(6)
        self.bell = QPushButton()
        self.bell.setProperty("variant", "icon")
        self.bell.setFixedSize(34, 34)
        self.bell.setIcon(icons.icon("bell", theme.TEXT_SOFT, 18))
        self.bell.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bell.clicked.connect(self._show_alerts)
        lay.addWidget(self.bell)

        self.avatar = Avatar("指", 32)
        lay.addWidget(self.avatar)
        self.user_label = label("指挥员", None, size=12, weight=700)
        lay.addWidget(self.user_label)

        lay.addSpacing(4)
        self.btn_min = icon_button("minimize", theme.MUTED, 30, 16, self.window_ref.showMinimized)
        self.btn_max = icon_button("maximize", theme.MUTED, 30, 16, self.window_ref.toggle_max)
        self.btn_close = icon_button("close", theme.MUTED, 30, 16, self.window_ref.close)
        self.btn_close.setProperty("variant", "winClose")
        self.btn_close.setIcon(icons.icon("close", theme.MUTED, 16))
        for b in (self.btn_min, self.btn_max, self.btn_close):
            b.setProperty("variant", "win")
            lay.addWidget(b)

        self._drag = None

    def set_user(self, user: str):
        self.user_label.setText(user)
        self.avatar.setText(user[:1].upper() or "指")

    def _show_alerts(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            f"QMenu {{ background:{theme.SURFACE}; border:1px solid {theme.BORDER};"
            f" border-radius:12px; padding:8px; }}"
            f"QMenu::item {{ padding:8px 18px; border-radius:6px; color:{theme.TEXT_SOFT}; }}"
            f"QMenu::item:selected {{ background:{theme.ACCENT_SOFT}; color:{theme.ACCENT_DARK}; }}"
        )
        engine = self.window_ref.engine
        for alert in engine.alerts[:4]:
            menu.addAction(f"●  {alert['title']}  ·  {alert['time']}")
        menu.addSeparator()
        menu.addAction("查看全部告警中心")
        menu.exec(self.bell.mapToGlobal(QPoint(0, self.bell.height() + 6)))

    # 拖动窗口
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag = event.globalPosition().toPoint() - self.window_ref.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.window_ref.move(event.globalPosition().toPoint() - self._drag)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.window_ref.toggle_max()


class Sidebar(QFrame):
    def __init__(self, window: "MainWindow", engine: SimEngine, parent=None):
        super().__init__(parent)
        self.window_ref = window
        self.setObjectName("Sidebar")
        self.setFixedWidth(212)
        self.setStyleSheet(
            f"#Sidebar {{ background:{theme.SURFACE}; border-right:1px solid {theme.BORDER};"
            f" border-bottom-left-radius:14px; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 14, 10, 12)
        lay.setSpacing(2)

        self.buttons: dict[str, NavButton] = {}
        for name, items in NAV_GROUPS:
            section = label(name, "caption", color=theme.MUTED_LIGHT)
            section.setStyleSheet(
                f"color:{theme.MUTED_LIGHT}; font-size:10.5px; font-weight:700; letter-spacing:1px;"
                f" padding:10px 0 4px 12px;"
            )
            lay.addWidget(section)
            for key, title, icon_name in items:
                btn = NavButton(key, "  " + title, icon_name)
                btn.clicked.connect(lambda _=False, k=key: window.navigate_to(k))
                lay.addWidget(btn)
                self.buttons[key] = btn

        lay.addStretch(1)

        engine_card = QFrame()
        engine_card.setObjectName("EngineCard")
        engine_card.setStyleSheet(
            f"#EngineCard {{ background:{theme.SURFACE_ALT}; border:1px solid {theme.BORDER};"
            f" border-radius:12px; }}"
        )
        ec = QVBoxLayout(engine_card)
        ec.setContentsMargins(11, 9, 11, 10)
        ec.setSpacing(4)
        head = QHBoxLayout()
        head.setSpacing(6)
        head.addWidget(label("AI 推理引擎", None, size=11.5, weight=700))
        head.addStretch(1)
        dot = label("●", None, color=theme.ACCENT, size=9)
        head.addWidget(dot)
        ec.addLayout(head)
        ec.addWidget(label("YOLO-Fire v3 · 38 ms", "caption"))
        self.engine_line = label("GPU 62% · 显存 2.1G", "caption", color=theme.MUTED_LIGHT)
        ec.addWidget(self.engine_line)
        lay.addWidget(engine_card)

        self.user_row = QWidget()
        ur = QHBoxLayout(self.user_row)
        ur.setContentsMargins(2, 8, 2, 0)
        ur.setSpacing(8)
        self.avatar = Avatar("A", 30)
        ur.addWidget(self.avatar)
        ucol = QVBoxLayout()
        ucol.setSpacing(0)
        self.name_label = label("admin", None, size=12, weight=700)
        ucol.addWidget(self.name_label)
        ucol.addWidget(label("指挥员 · 三级权限", "caption"))
        ur.addLayout(ucol)
        ur.addStretch(1)
        logout = icon_button("logout", theme.MUTED, 28, 15, window.logout,
                             tooltip="退出登录")
        ur.addWidget(logout)
        lay.addWidget(self.user_row)

    def set_active(self, key: str):
        for k, btn in self.buttons.items():
            btn.set_active(k == key)

    def set_user(self, user: str):
        self.name_label.setText(user)
        self.avatar.setText(user[:1].upper() or "A")


class Dashboard(QWidget):
    def __init__(self, window: "MainWindow", engine: SimEngine, parent=None):
        super().__init__(parent)
        self.window_ref = window
        self.engine = engine
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.titlebar = TitleBar(window, engine)
        lay.addWidget(self.titlebar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        self.sidebar = Sidebar(window, engine)
        body.addWidget(self.sidebar)

        content = QWidget()
        content.setObjectName("Content")
        content.setStyleSheet(f"#Content {{ background:{theme.BG}; }}")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        cl.addWidget(self.stack)
        body.addWidget(content, 1)
        lay.addLayout(body, 1)

        self.pages: dict[str, QWidget] = {}
        for key, page_cls in (
            ("overview", OverviewPage),
            ("map", MapPage),
            ("navigation", NavPage),
            ("collaboration", CollaborationPage),
            ("analysis", AnalysisPage),
            ("interaction", InteractionPage),
            ("fleet", FleetPage),
        ):
            page = page_cls(engine)
            self.pages[key] = page
            self.stack.addWidget(page)
        self.settings = SettingsPage(engine)
        self.settings.logout_requested.connect(self.window_ref.logout)
        self.pages["settings"] = self.settings
        self.stack.addWidget(self.settings)

        self._clock = QTimer(self)
        self._clock.setInterval(1000)
        self._clock.timeout.connect(self._tick_clock)
        self._clock.start()
        self._tick_clock()
        engine.tick.connect(self._tick_status)

    def set_user(self, user: str):
        self.titlebar.set_user(user)
        self.sidebar.set_user(user)

    def show_page(self, key: str):
        page = self.pages.get(key)
        if page is None:
            return
        self.stack.setCurrentWidget(page)
        self.sidebar.set_active(key)
        self.titlebar.crumb.setText(f"指挥中心 / {TITLES.get(key, '')}")
        self.window_ref.current_page = key

    def _tick_clock(self):
        now = datetime.now()
        self.titlebar.time_label.setText(now.strftime("%H:%M:%S"))
        weekday = "一二三四五六日"[now.weekday()]
        self.titlebar.date_label.setText(f"{now.strftime('%Y-%m-%d')} 周{weekday}")

    def _tick_status(self):
        level, kind = self.engine.risk_level()
        self.titlebar.chip_risk.set_text(f"火险 {self.engine.risk:.0f} · {level}")
        self.titlebar.chip_risk.set_kind(kind)
        count = len(self.engine.alerts)
        self.titlebar.bell.setToolTip(f"{count} 条告警")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon("logo.ico"))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(1440, 900)
        self.setMinimumSize(1240, 780)

        self.engine = SimEngine()

        root = QWidget()
        root.setObjectName("Root")
        root.setStyleSheet("#Root { background: transparent; }")
        self.setCentralWidget(root)
        root_lay = QVBoxLayout(root)
        root_lay.setContentsMargins(10, 10, 10, 10)
        root_lay.setSpacing(0)

        self.shell = QFrame()
        self.shell.setObjectName("AppShell")
        self.shell.setStyleSheet(
            f"#AppShell {{ background:{theme.BG}; border:1px solid {theme.BORDER_STRONG};"
            f" border-radius:14px; }}"
        )
        root_lay.addWidget(self.shell)
        shell_lay = QVBoxLayout(self.shell)
        shell_lay.setContentsMargins(0, 0, 0, 0)
        shell_lay.setSpacing(0)

        self.stack = QStackedWidget()
        shell_lay.addWidget(self.stack)

        self.login = LoginPage()
        self.login.logged_in.connect(self.on_login)
        self.stack.addWidget(self.login)

        self.dashboard = Dashboard(self, self.engine)
        self.stack.addWidget(self.dashboard)

        self.current_page = "overview"
        self.user = "admin"
        self._maximized = False
        self.center_on_screen()

    # ------------------------------------------------------------------
    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.center() - self.rect().center())

    def on_login(self, user: str):
        self.user = user
        self.dashboard.set_user(user)
        self.stack.setCurrentWidget(self.dashboard)
        self.navigate_to("overview")
        self.engine.push_event(f"操作员 {user} 登录指挥终端，链路已建立", "success")
        toast(self, f"欢迎回来，{user}！指挥链路已就绪")

    def logout(self):
        self.stack.setCurrentWidget(self.login)
        self.login.login_btn.setText("进入指挥中心")
        self.login.login_btn.setEnabled(True)
        if self._maximized:
            self.toggle_max()
        toast(self, "已退出登录", "info")

    def navigate_to(self, key: str):
        if self.stack.currentWidget() is not self.dashboard:
            return
        self.dashboard.show_page(key)

    def toggle_max(self):
        if self._maximized:
            self.showNormal()
            self.shell.setStyleSheet(
                f"#AppShell {{ background:{theme.BG}; border:1px solid {theme.BORDER_STRONG};"
                f" border-radius:14px; }}"
            )
            self.dashboard.titlebar.btn_max.setIcon(icons.icon("maximize", theme.MUTED, 16))
        else:
            self.showMaximized()
            self.shell.setStyleSheet(
                f"#AppShell {{ background:{theme.BG}; border:none; border-radius:0px; }}"
            )
            self.dashboard.titlebar.btn_max.setIcon(icons.icon("restore", theme.MUTED, 16))
        self._maximized = not self._maximized

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            self.toggle_max()
        elif event.key() == Qt.Key.Key_Escape and self._maximized:
            self.toggle_max()
        super().keyPressEvent(event)
