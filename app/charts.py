"""轻量自绘图表：折线、柱状、环形、雷达。"""
from __future__ import annotations

import math
from typing import Sequence

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QSizePolicy, QWidget

from . import theme


def fnt(size: float, weight: int = 500) -> QFont:
    f = QFont(theme.FONT_FAMILY)
    f.setPixelSize(max(8, int(size)))
    f.setWeight(QFont.Weight(weight))
    return f


class LineChart(QWidget):
    """多序列平滑折线图。"""

    def __init__(self, series: dict[str, list[float]] | None = None,
                 labels: Sequence[str] | None = None,
                 colors: Sequence[str] = (theme.ACCENT, theme.BLUE, theme.AMBER),
                 height: int = 180, y_max: float | None = None,
                 y_min: float = 0.0, unit: str = "", fill: bool = True, parent=None):
        super().__init__(parent)
        self.series = series or {"系列 A": [3, 5, 4, 7, 6, 9]}
        self.labels = list(labels or [])
        self.colors = list(colors)
        self.y_max = y_max
        self.y_min = y_min
        self.unit = unit
        self.fill = fill
        self.setMinimumHeight(height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_series(self, series: dict[str, list[float]]):
        self.series = series
        self.update()

    def paintEvent(self, event):
        if not self.series:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        legend_h = 16
        r = QRectF(38, 8, self.width() - 48, self.height() - 26 - legend_h)
        values = [v for vals in self.series.values() for v in vals] or [0]
        vmax = self.y_max if self.y_max is not None else max(values) * 1.15
        vmin = self.y_min
        span = (vmax - vmin) or 1

        # 网格 + y 轴标签
        p.setFont(fnt(8.5))
        for i in range(5):
            y = r.bottom() - r.height() * i / 4
            p.setPen(QPen(QColor(theme.BORDER), 1, Qt.PenStyle.DotLine))
            p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
            p.setPen(QColor(theme.MUTED_LIGHT))
            val = vmin + span * i / 4
            p.drawText(QRectF(0, y - 8, 32, 16),
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                       f"{val:.0f}")

        # 曲线
        for si, (name, vals) in enumerate(self.series.items()):
            if not vals:
                continue
            color = QColor(self.colors[si % len(self.colors)])
            pts = []
            n = len(vals)
            for i, v in enumerate(vals):
                x = r.left() + r.width() * (i / max(1, n - 1))
                y = r.bottom() - r.height() * ((v - vmin) / span)
                pts.append(QPointF(x, max(r.top(), min(r.bottom(), y))))
            path = QPainterPath(pts[0])
            for i in range(1, n):
                a, b = pts[i - 1], pts[i]
                mid = (a.x() + b.x()) / 2
                path.cubicTo(QPointF(mid, a.y()), QPointF(mid, b.y()), b)
            if si == 0 and self.fill:
                area = QPainterPath(path)
                area.lineTo(QPointF(r.right(), r.bottom()))
                area.lineTo(QPointF(r.left(), r.bottom()))
                area.closeSubpath()
                grad = QLinearGradient(0, r.top(), 0, r.bottom())
                c1 = QColor(color)
                c1.setAlpha(52)
                c2 = QColor(color)
                c2.setAlpha(2)
                grad.setColorAt(0, c1)
                grad.setColorAt(1, c2)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(grad)
                p.drawPath(area)
            pen = QPen(color, 2.2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)
            p.setBrush(QColor("#FFFFFF"))
            p.setPen(QPen(color, 2))
            p.drawEllipse(pts[-1], 3.4, 3.4)

        # x 轴标签
        if self.labels:
            p.setFont(fnt(8))
            p.setPen(QColor(theme.MUTED_LIGHT))
            step = max(1, len(self.labels) // 6)
            for i, text in enumerate(self.labels):
                if i % step and i != len(self.labels) - 1:
                    continue
                x = r.left() + r.width() * (i / max(1, len(self.labels) - 1))
                p.drawText(QRectF(x - 26, r.bottom() + 4, 52, 14),
                           Qt.AlignmentFlag.AlignCenter, text)

        # 图例
        p.setFont(fnt(8.5, 600))
        x = r.left()
        y = self.height() - 9
        for si, name in enumerate(self.series.keys()):
            color = QColor(self.colors[si % len(self.colors)])
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(color)
            p.drawEllipse(QPointF(x + 4, y), 3, 3)
            p.setPen(QColor(theme.MUTED))
            p.drawText(QPointF(x + 11, y + 4), name)
            x += 20 + p.fontMetrics().horizontalAdvance(name)
        p.end()


class BarChart(QWidget):
    def __init__(self, values: Sequence[float] = (32, 48, 26, 62, 40, 54),
                 labels: Sequence[str] = (), colors: Sequence[str] = (theme.ACCENT,),
                 height: int = 150, unit: str = "", rounded: int = 6, parent=None):
        super().__init__(parent)
        self.values = list(values)
        self.labels = list(labels)
        self.colors = list(colors) or [theme.ACCENT]
        self.unit = unit
        self.rounded = rounded
        self.setMinimumHeight(height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_values(self, values: Sequence[float], labels: Sequence[str] | None = None):
        self.values = list(values)
        if labels is not None:
            self.labels = list(labels)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(0, 6, self.width(), self.height() - 22)
        n = max(1, len(self.values))
        vmax = max(self.values) * 1.15 if self.values else 1
        gap = min(18, r.width() / n * 0.42)
        bw = (r.width() - gap * (n - 1)) / n
        for i, v in enumerate(self.values):
            h = r.height() * (v / vmax)
            x = r.left() + i * (bw + gap)
            rect = QRectF(x, r.bottom() - h, bw, h)
            color = QColor(self.colors[i % len(self.colors)])
            grad = QLinearGradient(0, rect.top(), 0, rect.bottom())
            grad.setColorAt(0, color.lighter(112))
            grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 150))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(grad)
            p.drawRoundedRect(rect, min(self.rounded, bw / 2), min(self.rounded, bw / 2))
            p.setFont(fnt(8.5, 600))
            p.setPen(QColor(theme.TEXT_SOFT))
            p.drawText(QRectF(x - 8, rect.top() - 16, bw + 16, 14),
                       Qt.AlignmentFlag.AlignCenter, f"{v:.0f}{self.unit}")
            if i < len(self.labels):
                p.setFont(fnt(8))
                p.setPen(QColor(theme.MUTED_LIGHT))
                p.drawText(QRectF(x - 8, r.bottom() + 4, bw + 16, 14),
                           Qt.AlignmentFlag.AlignCenter, self.labels[i])
        p.end()


class DonutChart(QWidget):
    def __init__(self, segments: Sequence[tuple[str, float, str]] | None = None,
                 center_title: str = "", center_value: str = "", thickness: int = 18,
                 parent=None):
        super().__init__(parent)
        self.segments = list(segments or [("A", 40, theme.ACCENT), ("B", 30, theme.BLUE),
                                          ("C", 30, theme.AMBER)])
        self.center_title = center_title
        self.center_value = center_value
        self.thickness = thickness
        self.setMinimumSize(140, 140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_segments(self, segments, center_value: str | None = None):
        self.segments = list(segments)
        if center_value is not None:
            self.center_value = center_value
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height()) - 8
        rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
        pen_w = self.thickness
        rect = rect.adjusted(pen_w / 2 + 2, pen_w / 2 + 2, -pen_w / 2 - 2, -pen_w / 2 - 2)
        total = sum(max(0.0, s[1]) for s in self.segments) or 1
        start = 90 * 16
        p.setPen(QPen(QColor(theme.BG_DEEP), pen_w))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(rect)
        for name, value, color in self.segments:
            span = -int(360 * 16 * value / total)
            pen = QPen(QColor(color), pen_w)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawArc(rect, start, span)
            start += span

        if self.center_value:
            p.setPen(QColor(theme.TEXT))
            p.setFont(fnt(side * 0.20, 700))
            p.drawText(rect.adjusted(0, -side * 0.06, 0, -side * 0.06),
                       Qt.AlignmentFlag.AlignCenter, self.center_value)
            p.setPen(QColor(theme.MUTED))
            p.setFont(fnt(max(8, side * 0.075)))
            p.drawText(rect.adjusted(0, side * 0.16, 0, side * 0.16),
                       Qt.AlignmentFlag.AlignCenter, self.center_title)
        p.end()


class RadarChart(QWidget):
    def __init__(self, axes: Sequence[str] | None = None,
                 values: Sequence[float] | None = None,
                 color: str = theme.ACCENT, parent=None):
        super().__init__(parent)
        self.axes = list(axes or ["侦察", "导航", "协作", "决策", "交互", "续航"])
        self.values = list(values or [0.82, 0.76, 0.88, 0.7, 0.9, 0.64])
        self.color = color
        self.setMinimumSize(160, 150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height()) - 34
        cx, cy = self.width() / 2, self.height() / 2 + 4
        n = len(self.axes)
        radius = side / 2

        def point(i, ratio):
            a = -math.pi / 2 + 2 * math.pi * i / n
            return QPointF(cx + math.cos(a) * radius * ratio, cy + math.sin(a) * radius * ratio)

        for ring in (0.25, 0.5, 0.75, 1.0):
            path = QPainterPath()
            for i in range(n):
                pt = point(i, ring)
                if i == 0:
                    path.moveTo(pt)
                else:
                    path.lineTo(pt)
            path.closeSubpath()
            p.setPen(QPen(QColor(theme.BORDER), 1))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)

        for i in range(n):
            p.setPen(QPen(QColor(theme.BORDER), 1))
            p.drawLine(QPointF(cx, cy), point(i, 1.0))

        poly = QPainterPath()
        for i in range(n):
            pt = point(i, max(0.05, min(1.0, self.values[i % len(self.values)])))
            if i == 0:
                poly.moveTo(pt)
            else:
                poly.lineTo(pt)
        poly.closeSubpath()
        fill = QColor(self.color)
        fill.setAlpha(58)
        p.setBrush(fill)
        p.setPen(QPen(QColor(self.color), 1.8))
        p.drawPath(poly)
        p.setBrush(QColor(self.color))
        for i in range(n):
            p.drawEllipse(point(i, max(0.05, min(1.0, self.values[i % len(self.values)]))), 2.4, 2.4)

        p.setFont(fnt(8.5))
        for i, name in enumerate(self.axes):
            pt = point(i, 1.18)
            p.setPen(QColor(theme.MUTED))
            p.drawText(QRectF(pt.x() - 32, pt.y() - 8, 64, 16),
                       Qt.AlignmentFlag.AlignCenter, name)
        p.end()
