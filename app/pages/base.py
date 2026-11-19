"""页面基类与通用行组件。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .. import icons, theme
from ..simulation import Robot
from ..widgets import Card, IconTile, Pill, ProgressLine, SectionHeader, label


class Page(QWidget):
    """标准内容页：标题区 + 内容区。"""

    def __init__(self, engine, title: str, subtitle: str = "", parent=None,
                 padding: tuple[int, int, int, int] = (22, 18, 22, 18)):
        super().__init__(parent)
        self.engine = engine
        self.setObjectName("Page")
        root = QVBoxLayout(self)
        root.setContentsMargins(*padding)
        root.setSpacing(14)

        header = QHBoxLayout()
        header.setSpacing(10)
        col = QVBoxLayout()
        col.setSpacing(2)
        self.title_label = label(title, "h1")
        self.subtitle_label = label(subtitle, "muted")
        col.addWidget(self.title_label)
        if subtitle:
            col.addWidget(self.subtitle_label)
        header.addLayout(col)
        header.addStretch(1)
        self.actions = QHBoxLayout()
        self.actions.setSpacing(8)
        header.addLayout(self.actions)
        root.addLayout(header)
        self.root = root

    def add_action(self, widget):
        self.actions.addWidget(widget)
        return widget


class ScrollPage(Page):
    """可滚动内容页（内容高度较大时使用）。"""

    def __init__(self, engine, title: str, subtitle: str = "", parent=None,
                 padding: tuple[int, int, int, int] = (22, 18, 12, 16)):
        super().__init__(engine, title, subtitle, parent, padding)
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.Shape.NoFrame)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inner = QWidget()
        inner.setObjectName("PageInner")
        self.content = QVBoxLayout(inner)
        self.content.setContentsMargins(0, 2, 10, 8)
        self.content.setSpacing(14)
        area.setWidget(inner)
        self.root.addWidget(area, 1)
        self.scroll_area = area
        # 页面内容统一添加到滚动区内（保持 self.root.addLayout 写法一致）
        self.root = self.content

    # 兼容 Page 的接口
    @property
    def body(self):
        return self.content


class Panel(Card):
    """带标题栏的卡片。"""

    def __init__(self, title: str, subtitle: str = "", icon_name: str | None = None,
                 padding: int = 18, spacing: int = 12, parent=None):
        super().__init__(parent, padding=padding, spacing=spacing)
        self.header = SectionHeader(title, subtitle, icon_name)
        self.body.addWidget(self.header)
        self.content = QVBoxLayout()
        self.content.setSpacing(9)
        self.content.setContentsMargins(0, 0, 0, 0)
        self.body.addLayout(self.content, 1)

    def add(self, widget: QWidget, stretch: int = 0):
        self.content.addWidget(widget, stretch)
        return widget

    def addLayout(self, layout, stretch: int = 0):
        self.content.addLayout(layout, stretch)
        return layout

    def addWidget(self, widget: QWidget, stretch: int = 0):
        self.content.addWidget(widget, stretch)
        return widget

    def addStretch(self, stretch: int = 0):
        self.content.addStretch(stretch)

    def addSpacing(self, px: int):
        self.content.addSpacing(px)

    def add_action(self, widget: QWidget):
        return self.header.add_action(widget)


def hline() -> QFrame:
    line = QFrame()
    line.setObjectName("Divider")
    line.setFixedHeight(1)
    return line


def alert_row(alert: dict, compact: bool = False) -> QWidget:
    color, soft = theme.SEVERITY.get(alert.get("level", "info"), theme.SEVERITY["info"])
    row = QWidget()
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 4, 0, 4)
    lay.setSpacing(10)

    dot = QLabel()
    dot.setFixedSize(30, 30)
    dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ic = {"critical": "flame", "warning": "alert", "info": "info"}.get(alert["level"], "info")
    dot.setPixmap(icons.pixmap(ic, color, 15))
    dot.setStyleSheet(f"background:{soft}; border-radius:9px;")
    lay.addWidget(dot, 0, Qt.AlignmentFlag.AlignTop)

    col = QVBoxLayout()
    col.setSpacing(1)
    top = QHBoxLayout()
    top.setSpacing(6)
    top.addWidget(label(alert["title"], None, size=12.5, weight=700))
    if not compact:
        top.addStretch(1)
        top.addWidget(label(alert["time"], "caption"))
    col.addLayout(top)
    detail = label(alert.get("detail", ""), "caption")
    detail.setWordWrap(True)
    col.addWidget(detail)
    if not compact:
        col.addWidget(label(alert.get("source", ""), "caption", color=theme.MUTED_LIGHT))
    lay.addLayout(col, 1)
    return row


def robot_row(robot: Robot, compact: bool = False) -> QWidget:
    row = QWidget()
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 5, 0, 5)
    lay.setSpacing(10)

    color = theme.BLUE if robot.kind == "UAV" else theme.ACCENT
    soft = theme.BLUE_SOFT if robot.kind == "UAV" else theme.ACCENT_SOFT
    lay.addWidget(IconTile("drone" if robot.kind == "UAV" else "robot", color, soft, 32, 16, 10))

    col = QVBoxLayout()
    col.setSpacing(1)
    name_row = QHBoxLayout()
    name_row.setSpacing(6)
    name_row.addWidget(label(robot.id, None, size=12, weight=700))
    name_row.addWidget(label(robot.name, "caption"))
    name_row.addStretch(1)
    col.addLayout(name_row)
    bar = ProgressLine("", robot.battery, theme.ACCENT if robot.battery > 40 else theme.RED,
                       suffix="%", show_head=False)
    bar.setFixedHeight(5)
    col.addWidget(bar)
    lay.addLayout(col, 1)

    if not compact:
        col2 = QVBoxLayout()
        col2.setSpacing(2)
        col2.addWidget(label(f"电量 {robot.battery:.0f}%", "caption"),
                       0, Qt.AlignmentFlag.AlignRight)
        col2.addWidget(label(robot.task, "caption", color=theme.MUTED_LIGHT),
                       0, Qt.AlignmentFlag.AlignRight)
        lay.addLayout(col2)
    status = Pill(robot.status_text, robot.status_kind)
    lay.addWidget(status, 0, Qt.AlignmentFlag.AlignVCenter)
    return row


class KvChip(QWidget):
    """图标 + 文本的小胶囊。"""

    def __init__(self, icon_name: str, text: str, color: str = theme.TEXT_SOFT,
                 bg: str | None = None, parent=None, padding: tuple = (9, 5, 10, 5)):
        super().__init__(parent)
        self.setStyleSheet(f"background:{bg or theme.SURFACE_ALT}; border-radius:9px;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(*padding)
        lay.setSpacing(6)
        ic = QLabel()
        ic.setPixmap(icons.pixmap(icon_name, color if color != theme.TEXT_SOFT else theme.MUTED, 13))
        lay.addWidget(ic)
        self.text_label = label(text, None, color=color, size=11.5, weight=600)
        lay.addWidget(self.text_label)
        self._color = color

    def set_text(self, text: str, color: str | None = None):
        self.text_label.setText(text)
        if color:
            self._color = color
            self.text_label.setStyleSheet(f"color:{color}; font-size:11.5px; font-weight:600;")


def kv_chip(icon_name: str, text: str, color: str = theme.TEXT_SOFT,
            bg: str = theme.SURFACE_ALT) -> KvChip:
    return KvChip(icon_name, text, color, bg)


class EventList(QWidget):
    """事件／日志流（按更新重建，条目数很少，开销可忽略）。"""

    def __init__(self, events: list[dict] | None = None, limit: int = 5,
                 compact: bool = True, show_time: bool = True, parent=None):
        super().__init__(parent)
        self._events = list(events or [])
        self._limit = limit
        self._compact = compact
        self._show_time = show_time
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(2)
        self.refresh()

    def set_events(self, events: list[dict]):
        self._events = list(events)
        self.refresh()

    def refresh(self):
        while self._lay.count():
            item = self._lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for ev in self._events[: self._limit]:
            color, soft = theme.SEVERITY.get(ev.get("level", "info"), theme.SEVERITY["info"])
            row = QWidget()
            lay = QHBoxLayout(row)
            lay.setContentsMargins(0, 3, 0, 3)
            lay.setSpacing(8)
            dot = QLabel()
            dot.setFixedSize(7, 7)
            dot.setStyleSheet(f"background:{color}; border-radius:3px;")
            lay.addWidget(dot, 0, Qt.AlignmentFlag.AlignTop if self._compact else Qt.AlignmentFlag.AlignVCenter)
            lay.addWidget(label(ev.get("text", ""), "caption", color=theme.TEXT_SOFT), 1)
            if self._show_time:
                lay.addWidget(label(ev.get("time", ""), "caption", color=theme.MUTED_LIGHT))
            self._lay.addWidget(row)
        if not self._events:
            self._lay.addWidget(label("暂无事件", "caption"))
