"""可复用的亮色系 UI 组件。"""
from __future__ import annotations

from typing import Iterable, Sequence

from PySide6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    QSize,
    Qt,
    QTimer,
    Property,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import icons, theme


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------
def set_prop(widget: QWidget, name: str, value) -> None:
    widget.setProperty(name, value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def soft_bg(w, color: str, radius: int = 12) -> None:
    """给容器上浅色底但不级联影响子控件。"""
    name = f"softbg{radius}"
    w.setObjectName(name)
    w.setStyleSheet(f"#{name}{{background:{color}; border-radius:{radius}px;}}")


def shadow(widget: QWidget, blur: int = 26, dy: int = 6, alpha: int = 26) -> None:
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, dy)
    effect.setColor(QColor(20, 60, 40, alpha))
    widget.setGraphicsEffect(effect)


def label(text: str = "", role: str | None = None, color: str | None = None,
          size: int | None = None, weight: int | None = None) -> QLabel:
    lb = QLabel(text)
    if role:
        lb.setProperty("role", role)
    style = []
    if color:
        style.append(f"color:{color};")
    if size:
        style.append(f"font-size:{size}px;")
    if weight:
        style.append(f"font-weight:{weight};")
    if style:
        lb.setStyleSheet("".join(style))
    return lb


def button(text: str, variant: str = "ghost", icon_name: str | None = None,
           icon_color: str | None = None, height: int = 34, size: int = 13,
           on_click=None, tooltip: str | None = None) -> QPushButton:
    btn = QPushButton(text)
    btn.setProperty("variant", variant)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if height:
        btn.setMinimumHeight(height)
    f = btn.font()
    f.setPixelSize(size)
    f.setWeight(QFont.Weight.DemiBold)
    btn.setFont(f)
    if icon_name:
        color = icon_color or {
            "primary": "#FFFFFF",
            "danger": "#FFFFFF",
            "dangerSoft": theme.RED,
            "soft": theme.ACCENT_DARK,
            "blue": theme.BLUE,
        }.get(variant, theme.TEXT_SOFT)
        btn.setIcon(icons.icon(icon_name, color, 16))
        btn.setIconSize(QSize(16, 16))
    if tooltip:
        btn.setToolTip(tooltip)
    if on_click:
        btn.clicked.connect(on_click)
    return btn


def icon_button(name: str, color: str = theme.TEXT_SOFT, size: int = 30,
                icon_size: int = 18, on_click=None, tooltip: str = "") -> QPushButton:
    btn = QPushButton()
    btn.setProperty("variant", "icon")
    btn.setFixedSize(size, size)
    btn.setIcon(icons.icon(name, color, icon_size))
    btn.setIconSize(QSize(icon_size, icon_size))
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if tooltip:
        btn.setToolTip(tooltip)
    if on_click:
        btn.clicked.connect(on_click)
    return btn


class Pill(QLabel):
    """圆角状态标签。"""

    def __init__(self, text: str, kind: str = "success", parent=None, dot: bool = True):
        super().__init__(parent)
        self._dot = dot
        self.set_kind(kind)
        self.set_text(text)

    def set_kind(self, kind: str) -> None:
        color, soft = theme.SEVERITY.get(kind, theme.SEVERITY["info"])
        self._color = color
        self.setStyleSheet(
            f"color:{color}; background:{soft}; border-radius:10px;"
            f"padding:3px 9px 3px {16 if self._dot else 9}px; font-size:11px; font-weight:700;"
        )

    def set_text(self, text: str) -> None:
        self.setText(("●  " if self._dot else "") + text)


class Divider(QFrame):
    def __init__(self, parent=None, margin: int = 0):
        super().__init__(parent)
        self.setObjectName("Divider")
        self.setFixedHeight(1)
        if margin:
            self.setContentsMargins(margin, 0, margin, 0)


class Card(QFrame):
    def __init__(self, parent=None, padding: int = 18, spacing: int = 12,
                 alt: bool = False, object_name: str | None = None):
        super().__init__(parent)
        self.setObjectName(object_name or ("CardAlt" if alt else "Card"))
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(padding, padding, padding, padding)
        self.body.setSpacing(spacing)

    def add(self, widget: QWidget, stretch: int = 0):
        self.body.addWidget(widget, stretch)
        return widget

    def add_layout(self, layout, stretch: int = 0):
        self.body.addLayout(layout, stretch)
        return layout


class SectionHeader(QWidget):
    """卡片标题行：图标 + 标题 + 副标题 + 右侧操作区。"""

    def __init__(self, title: str, subtitle: str = "", icon_name: str | None = None,
                 icon_color: str = theme.ACCENT, parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(9)

        if icon_name:
            badge = QLabel()
            badge.setFixedSize(28, 28)
            badge.setPixmap(icons.pixmap(icon_name, icon_color, 16))
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setStyleSheet(
                f"background:{theme.ACCENT_SOFT}; border-radius:9px;"
            )
            row.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(1)
        self.title = label(title, "cardTitle")
        text_col.addWidget(self.title)
        self.subtitle = label(subtitle, "caption")
        self.subtitle.setVisible(bool(subtitle))
        text_col.addWidget(self.subtitle)
        row.addLayout(text_col)
        row.addStretch(1)
        self.actions = QHBoxLayout()
        self.actions.setSpacing(6)
        self.actions.setContentsMargins(0, 0, 0, 0)
        row.addLayout(self.actions)

    def add_action(self, widget: QWidget):
        self.actions.addWidget(widget)
        return widget


class IconTile(QWidget):
    """带柔和底色的图标方块。"""

    def __init__(self, icon_name: str, color: str = theme.ACCENT, bg: str | None = None,
                 size: int = 38, icon_size: int = 19, radius: int = 11, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._icon = icons.pixmap(icon_name, color, icon_size)
        self._bg = QColor(bg or theme.ACCENT_SOFT)
        self._radius = radius

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._bg)
        p.drawRoundedRect(QRectF(self.rect()), self._radius, self._radius)
        x = (self.width() - self._icon.width()) / 2
        y = (self.height() - self._icon.height()) / 2
        p.drawPixmap(QPointF(x, y), self._icon)
        p.end()


class Sparkline(QWidget):
    """迷你趋势曲线。"""

    def __init__(self, values: Sequence[float] | None = None, color: str = theme.ACCENT,
                 height: int = 34, parent=None, fill: bool = True, line_width: float = 1.8):
        super().__init__(parent)
        self._values = list(values or [4, 6, 5, 8, 7, 10, 9, 12])
        self._color = QColor(color)
        self._fill = fill
        self._lw = line_width
        self.setMinimumHeight(height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(height)

    def set_values(self, values: Sequence[float]):
        self._values = list(values) or [0]
        self.update()

    def paintEvent(self, event):
        if not self._values:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 4, -1, -2)
        vals = self._values
        vmin, vmax = min(vals), max(vals)
        span = (vmax - vmin) or 1.0
        n = len(vals)
        pts = [
            QPointF(
                r.left() + r.width() * (i / max(1, n - 1)),
                r.bottom() - r.height() * ((v - vmin) / span) * 0.86 - r.height() * 0.07,
            )
            for i, v in enumerate(vals)
        ]
        path = QPainterPath(pts[0])
        for i in range(1, n):
            prev, cur = pts[i - 1], pts[i]
            mid = (prev.x() + cur.x()) / 2
            path.cubicTo(QPointF(mid, prev.y()), QPointF(mid, cur.y()), cur)

        if self._fill:
            area = QPainterPath(path)
            area.lineTo(QPointF(r.right(), r.bottom()))
            area.lineTo(QPointF(r.left(), r.bottom()))
            area.closeSubpath()
            grad = QLinearGradient(0, r.top(), 0, r.bottom())
            c1 = QColor(self._color)
            c1.setAlpha(70)
            c2 = QColor(self._color)
            c2.setAlpha(0)
            grad.setColorAt(0, c1)
            grad.setColorAt(1, c2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(grad)
            p.drawPath(area)

        pen = QPen(self._color, self._lw)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.end()


class StatCard(QFrame):
    """关键指标卡片。"""

    def __init__(self, title: str, value: str, unit: str = "", icon_name: str = "activity",
                 color: str = theme.ACCENT, soft: str = theme.ACCENT_SOFT,
                 delta: str = "", delta_kind: str = "up", trend: Sequence[float] | None = None,
                 parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumHeight(108)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 12)
        outer.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(IconTile(icon_name, color, soft, 32, 16, 10))
        top.addWidget(label(title, "muted"))
        top.addStretch(1)
        if delta:
            sign = "▲" if delta_kind == "up" else ("▼" if delta_kind == "down" else "•")
            dcolor = theme.ACCENT if delta_kind == "up" else (theme.RED if delta_kind == "down" else theme.MUTED)
            d = QLabel(f"{sign} {delta}")
            d.setStyleSheet(f"color:{dcolor}; font-size:11px; font-weight:700;")
            top.addWidget(d)
        outer.addLayout(top)

        row = QHBoxLayout()
        row.setSpacing(4)
        self._value = QLabel(value)
        self._value.setStyleSheet(f"font-size:25px; font-weight:700; color:{theme.TEXT};")
        row.addWidget(self._value, 0, Qt.AlignmentFlag.AlignBottom)
        if unit:
            u = QLabel(unit)
            u.setStyleSheet(f"color:{theme.MUTED}; font-size:12px; padding-bottom:3px;")
            row.addWidget(u, 0, Qt.AlignmentFlag.AlignBottom)
        row.addStretch(1)
        self._spark = Sparkline(trend or [3, 5, 4, 7, 6, 8, 7, 9], color, 26, fill=False)
        self._spark.setFixedWidth(64)
        row.addWidget(self._spark, 0, Qt.AlignmentFlag.AlignBottom)
        outer.addLayout(row)
        self.set_value(value)

    def set_value(self, value: str):
        self._value.setText(value)

    def set_trend(self, values: Sequence[float]):
        self._spark.set_values(values)


class ProgressLine(QWidget):
    """带标题与数值的细进度条。"""

    def __init__(self, title: str, value: float = 0.0, color: str = theme.ACCENT,
                 suffix: str = "%", show_head: bool = True, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._value = max(0.0, min(100.0, value))
        self._suffix = suffix
        self._show_head = show_head
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        if show_head:
            head = QHBoxLayout()
            head.setSpacing(4)
            head.addWidget(label(title, "muted"))
            head.addStretch(1)
            self.value_label = label(f"{value:.0f}{suffix}", "caption", color=theme.TEXT_SOFT, weight=700)
            head.addWidget(self.value_label)
            lay.addLayout(head)
        self._height = 6
        self.setMinimumHeight(30 if show_head else 8)
        self.setValue = self.set_value

    def set_value(self, value: float, animate: bool = False):
        value = max(0.0, min(100.0, float(value)))
        self._value = value
        if hasattr(self, "value_label"):
            self.value_label.setText(f"{value:.0f}{self._suffix}")
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        y = self.height() - 7
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(theme.BG_DEEP))
        p.drawRoundedRect(QRectF(0, y, w, 6), 3, 3)
        fw = w * self._value / 100.0
        if fw > 0.5:
            grad = QLinearGradient(0, 0, w, 0)
            grad.setColorAt(0, QColor(self._color).lighter(118))
            grad.setColorAt(1, self._color)
            p.setBrush(grad)
            p.drawRoundedRect(QRectF(0, y, fw, 6), 3, 3)
        p.end()


class ToggleSwitch(QAbstractButton):
    """轻量动画开关。"""

    def __init__(self, checked: bool = False, color: str = theme.ACCENT, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(40, 22)
        self._color = QColor(color)
        self._pos = 1.0 if checked else 0.0
        self._anim = QPropertyAnimation(self, b"knob", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.toggled.connect(self._animate)

    def _animate(self, checked: bool):
        self._anim.stop()
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def get_knob(self) -> float:
        return self._pos

    def set_knob(self, v: float):
        self._pos = v
        self.update()

    knob = Property(float, get_knob, set_knob)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        off = QColor(theme.BORDER_STRONG)
        track = QColor(self._color)
        if self._pos < 1.0:
            track = QColor(
                int(off.red() + (track.red() - off.red()) * self._pos),
                int(off.green() + (track.green() - off.green()) * self._pos),
                int(off.blue() + (track.blue() - off.blue()) * self._pos),
            )
        p.setBrush(track if self.isEnabled() else QColor("#DCE6DF"))
        p.drawRoundedRect(QRectF(0, 0, 40, 22), 11, 11)
        x = 3 + self._pos * 18
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(QRectF(x, 3, 16, 16))
        p.end()


class RingGauge(QWidget):
    """环形风险指数仪表。"""

    def __init__(self, value: float = 0, maximum: float = 100, title: str = "",
                 unit: str = "", color: str = theme.ACCENT, size: int = 150,
                 thickness: float = 12, parent=None):
        super().__init__(parent)
        self._max = maximum
        self._value = 0.0
        self._target = value
        self._title = title
        self._unit = unit
        self._color = QColor(color)
        self._thickness = thickness
        self.setMinimumSize(size, size)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._anim = QPropertyAnimation(self, b"value", self)
        self._anim.setDuration(900)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(float(value))
        self._anim.start()

    def get_value(self) -> float:
        return self._value

    def set_value(self, v: float):
        self._value = v
        self.update()

    value = Property(float, get_value, set_value)

    def set_target(self, value: float, color: str | None = None):
        if color:
            self._color = QColor(color)
        self._anim.stop()
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(float(value))
        self._anim.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height())
        m = self._thickness / 2 + 6
        rect = QRectF((self.width() - side) / 2 + m, (self.height() - side) / 2 + m,
                      side - 2 * m, side - 2 * m)
        p.setPen(QPen(QColor(theme.BG_DEEP), self._thickness))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(rect, 225 * 16, -270 * 16)

        ratio = max(0.0, min(1.0, self._value / self._max)) if self._max else 0
        if ratio > 0.004:
            c = QColor(self._color)
            light = QColor(c)
            light.setAlpha(150)
            pen = QPen(c, self._thickness)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawArc(rect, 225 * 16, int(-270 * 16 * ratio))

        center = rect.center()
        p.setPen(QColor(theme.TEXT))
        f = QFont()
        f.setPixelSize(int(side * 0.20))
        f.setWeight(QFont.Weight.Bold)
        p.setFont(f)
        text = f"{self._value:.0f}"
        p.drawText(QRectF(center.x() - side / 2, center.y() - side * 0.17, side, side * 0.3),
                   Qt.AlignmentFlag.AlignCenter, text)
        p.setPen(QColor(theme.MUTED))
        f2 = QFont()
        f2.setPixelSize(max(9, int(side * 0.075)))
        p.setFont(f2)
        p.drawText(QRectF(center.x() - side / 2, center.y() + side * 0.09, side, 20),
                   Qt.AlignmentFlag.AlignCenter, self._unit or self._title)
        if self._title and self._unit:
            p.drawText(QRectF(center.x() - side / 2, center.y() + side * 0.09 + 14, side, 20),
                       Qt.AlignmentFlag.AlignCenter, self._title)
        p.end()


class KeyValueRow(QWidget):
    def __init__(self, key: str, value: str, value_color: str | None = None,
                 icon_name: str | None = None, parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(7)
        if icon_name:
            ic = QLabel()
            ic.setPixmap(icons.pixmap(icon_name, theme.MUTED, 14))
            row.addWidget(ic)
        row.addWidget(label(key, "muted"))
        row.addStretch(1)
        self.value = label(value, None, color=value_color or theme.TEXT, size=12, weight=700)
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(self.value)

    def set_value(self, text: str, color: str | None = None):
        self.value.setText(text)
        if color:
            self.value.setStyleSheet(f"color:{color}; font-size:12px; font-weight:700;")


class SearchBox(QLineEdit):
    def __init__(self, placeholder: str = "搜索…", parent=None, width: int | None = None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setProperty("role", "search")
        self.setClearButtonEnabled(True)
        self.addAction(icons.icon("search", theme.MUTED_LIGHT, 16), QLineEdit.ActionPosition.LeadingPosition)
        self.setMinimumHeight(34)
        if width:
            self.setFixedWidth(width)


class ToggleRow(QWidget):
    """设置页开关项。"""

    toggled = Signal(bool)

    def __init__(self, title: str, desc: str = "", checked: bool = False,
                 icon_name: str | None = None, parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 6, 0, 6)
        row.setSpacing(10)
        if icon_name:
            row.addWidget(IconTile(icon_name, theme.ACCENT, theme.ACCENT_SOFT, 32, 16, 10))
        col = QVBoxLayout()
        col.setSpacing(1)
        col.addWidget(label(title, None, size=13, weight=700))
        if desc:
            col.addWidget(label(desc, "caption"))
        row.addLayout(col, 1)
        self.switch = ToggleSwitch(checked)
        self.switch.toggled.connect(self.toggled.emit)
        row.addWidget(self.switch)


# ---------------------------------------------------------------------------
# 浮动提示与对话框
# ---------------------------------------------------------------------------
class Toast(QFrame):
    """右下角悬浮提示。"""

    def __init__(self, parent: QWidget, text: str, kind: str = "success", timeout: int = 3200):
        super().__init__(parent)
        color, soft = theme.SEVERITY.get(kind, theme.SEVERITY["success"])
        self.setObjectName("Toast")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"QFrame#Toast {{ background:{theme.SURFACE}; border:1px solid {theme.BORDER};"
            f" border-radius:12px; }}"
        )
        shadow(self, 30, 8, 40)
        row = QHBoxLayout(self)
        row.setContentsMargins(14, 11, 18, 11)
        row.setSpacing(10)
        dot = QLabel()
        dot.setFixedSize(26, 26)
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dot.setPixmap(icons.pixmap(
            {"success": "check", "warning": "alert", "critical": "alert", "info": "info"}.get(kind, "check"),
            color, 15))
        dot.setStyleSheet(f"background:{soft}; border-radius:8px;")
        row.addWidget(dot)
        lb = label(text, None, size=12.5, weight=600)
        row.addWidget(lb)
        self.adjustSize()
        self.setMinimumWidth(280)
        self._timeout = timeout

    def pop(self):
        parent = self.parentWidget()
        if parent is None:
            return
        x = parent.width() - self.width() - 26
        y = parent.height() - self.height() - 26
        self.move(x, y + 12)
        self.show()
        self.raise_()
        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(240)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(self.pos())
        anim.setEndValue(self.pos() - QPointF(0, 12).toPoint())
        anim.start()
        QTimer.singleShot(self._timeout, self.close)


def toast(parent: QWidget, text: str, kind: str = "success") -> None:
    t = Toast(parent.window(), text, kind)
    t.pop()


class Dialog(QDialog):
    """与主题一致的确认对话框。"""

    def __init__(self, parent, title: str, message: str, kind: str = "info",
                 confirm_text: str = "确认", cancel_text: str = "取消",
                 on_confirm=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        color, soft = theme.SEVERITY.get(kind, theme.SEVERITY["info"])
        shadow_frame = QFrame(self)
        shadow_frame.setObjectName("Card")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(shadow_frame)
        shadow(shadow_frame, 40, 10, 60)
        body = QVBoxLayout(shadow_frame)
        body.setContentsMargins(24, 22, 24, 18)
        body.setSpacing(14)

        head = QHBoxLayout()
        head.setSpacing(12)
        tile = IconTile(
            {"warning": "alert", "critical": "alert", "success": "check"}.get(kind, "info"),
            color, soft, 38, 19)
        head.addWidget(tile)
        col = QVBoxLayout()
        col.setSpacing(3)
        col.addWidget(label(title, None, size=15, weight=700))
        msg = label(message, None, color=theme.MUTED, size=12)
        msg.setWordWrap(True)
        msg.setMinimumWidth(290)
        col.addWidget(msg)
        head.addLayout(col, 1)
        body.addLayout(head)

        btns = QHBoxLayout()
        btns.addStretch(1)
        cancel = button(cancel_text, "soft", height=34, on_click=self.reject)
        btns.addWidget(cancel)
        ok = button(confirm_text, "primary" if kind != "critical" else "danger", height=34)
        ok.clicked.connect(lambda: (self.accept(), on_confirm and on_confirm()))
        btns.addWidget(ok)
        body.addLayout(btns)
        self.setFixedWidth(430)


class Avatar(QLabel):
    def __init__(self, text: str, size: int = 34, color: str = theme.ACCENT,
                 bg: str = theme.ACCENT_SOFT, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(text[:2].upper())
        self.setStyleSheet(
            f"background:{bg}; color:{color}; border-radius:{size // 2}px;"
            f"font-size:{int(size * 0.36)}px; font-weight:700;"
        )
