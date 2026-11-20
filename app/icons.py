"""纯矢量图标：用 QPainter 现场绘制，无需外部图片资源。

所有图标使用 24x24 的设计网格，按倍率渲染，保证高分屏清晰。
"""
from __future__ import annotations

from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)

_M = 24.0001


def _pen(color: QColor, width: float = 1.7) -> QPen:
    pen = QPen(color)
    pen.setWidthF(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def _rounded(p: QPainter, x, y, w, h, r=2.5):
    p.drawRoundedRect(QRectF(x, y, w, h), r, r)


def _draw(p: QPainter, name: str, color: QColor) -> None:
    p.setPen(_pen(color))
    p.setBrush(Qt.BrushStyle.NoBrush)
    c = color

    if name == "dashboard":
        for x, y in ((3.5, 3.5), (13.5, 3.5), (3.5, 13.5), (13.5, 13.5)):
            _rounded(p, x, y, 7, 7, 2.2)
    elif name == "overview":
        _rounded(p, 3.5, 3.5, 7, 17, 2.2)
        _rounded(p, 13.5, 3.5, 7, 8, 2.2)
        _rounded(p, 13.5, 14.5, 7, 6, 2.2)
    elif name == "map":
        path = QPainterPath(QPointF(3.5, 6))
        path.lineTo(9, 3.5)
        path.lineTo(15, 6)
        path.lineTo(20.5, 3.5)
        path.lineTo(20.5, 18)
        path.lineTo(15, 20.5)
        path.lineTo(9, 18)
        path.lineTo(3.5, 20.5)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QPointF(9, 3.5), QPointF(9, 18))
        p.drawLine(QPointF(15, 6), QPointF(15, 20.5))
    elif name == "route":
        path = QPainterPath(QPointF(5, 19))
        path.cubicTo(9, 19, 8, 10, 12, 9)
        path.cubicTo(16, 8, 15, 5, 19, 5)
        pen = _pen(c)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([2.4, 2.2])
        p.setPen(pen)
        p.drawPath(path)
        p.setPen(_pen(c))
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(QPointF(5, 19), 2.0, 2.0)
        p.setBrush(c)
        p.drawEllipse(QPointF(19, 5), 2.4, 2.4)
    elif name == "robot":
        _rounded(p, 5, 8, 14, 10, 3)
        p.drawLine(QPointF(12, 8), QPointF(12, 4.5))
        p.setBrush(c)
        p.drawEllipse(QPointF(12, 3.6), 1.4, 1.4)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(QPointF(5, 13), QPointF(2.5, 13))
        p.drawLine(QPointF(21.5, 13), QPointF(19, 13))
        p.setBrush(c)
        p.drawEllipse(QPointF(9, 13), 1.1, 1.1)
        p.drawEllipse(QPointF(15, 13), 1.1, 1.1)
    elif name == "drone":
        p.setPen(_pen(c, 2.0))
        for x1, y1, x2, y2 in ((9, 10, 4.6, 5.8), (15, 10, 19.4, 5.8), (9, 14, 4.6, 18.2), (15, 14, 19.4, 18.2)):
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        _rounded(p, 8, 8.6, 8, 6.8, 2.6)
        p.setPen(_pen(c, 1.5))
        for cx, cy in ((3.8, 5.2), (20.2, 5.2), (3.8, 18.8), (20.2, 18.8)):
            p.drawEllipse(QPointF(cx, cy), 2.5, 1.5)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        p.drawEllipse(QPointF(12, 12), 1.9, 1.9)
    elif name == "flame":
        path = QPainterPath(QPointF(12, 2.5))
        path.cubicTo(15.5, 6.5, 18.5, 8.5, 18.5, 13.5)
        path.cubicTo(18.5, 17.8, 15.6, 21, 12, 21)
        path.cubicTo(8.4, 21, 5.5, 17.8, 5.5, 13.5)
        path.cubicTo(5.5, 10.5, 7.2, 8.6, 8.6, 6.8)
        path.cubicTo(9.2, 9.4, 10.4, 10.6, 11.6, 11.2)
        path.cubicTo(12.6, 8.4, 11.6, 5.2, 12, 2.5)
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(path)
    elif name == "chat":
        path = QPainterPath()
        path.addRoundedRect(QRectF(3, 4.5, 18, 13), 3.5, 3.5)
        p.drawPath(path)
        p.drawLine(QPointF(8, 17.5), QPointF(7, 21))
        p.drawLine(QPointF(8, 17.5), QPointF(12.5, 17.5))
        p.setBrush(c)
        p.drawEllipse(QPointF(8, 11), 1.15, 1.15)
        p.drawEllipse(QPointF(12, 11), 1.15, 1.15)
        p.drawEllipse(QPointF(16, 11), 1.15, 1.15)
    elif name == "settings":
        p.drawEllipse(QPointF(12, 12), 3, 3)
        import math

        for i in range(8):
            a = math.radians(i * 45 + 22.5)
            p.drawLine(
                QPointF(12 + 5.4 * math.cos(a), 12 + 5.4 * math.sin(a)),
                QPointF(12 + 8.0 * math.cos(a), 12 + 8.0 * math.sin(a)),
            )
        p.drawEllipse(QPointF(12, 12), 6.6, 6.6)
    elif name == "bell":
        path = QPainterPath()
        path.moveTo(6, 16.5)
        path.lineTo(6, 11)
        path.cubicTo(6, 7.4, 8.6, 5, 12, 5)
        path.cubicTo(15.4, 5, 18, 7.4, 18, 11)
        path.lineTo(18, 16.5)
        p.drawPath(path)
        p.drawLine(QPointF(4.5, 16.5), QPointF(19.5, 16.5))
        p.drawArc(QRectF(9.5, 17.6, 5, 4), 200 * 16, 140 * 16)
    elif name == "search":
        p.drawEllipse(QPointF(10.5, 10.5), 6, 6)
        p.drawLine(QPointF(15, 15), QPointF(20.5, 20.5))
    elif name == "leaf":
        path = QPainterPath(QPointF(20, 4))
        path.cubicTo(9, 4.5, 4, 9.5, 4, 16)
        path.cubicTo(4, 18, 5, 20, 5, 20)
        path.cubicTo(10, 20, 20, 17, 20, 4)
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(path)
        p.setPen(_pen(QColor("#FFFFFF"), 1.2))
        p.drawLine(QPointF(6.5, 17.5), QPointF(15, 9))
    elif name == "wind":
        for y, ln in ((7, 13), (12, 17), (17, 11)):
            p.drawLine(QPointF(3.5, y), QPointF(3.5 + ln, y))
        p.drawArc(QRectF(14, 4.5, 6.5, 5), 270 * 16, 200 * 16)
        p.drawArc(QRectF(12, 14.5, 6, 5), 90 * 16, 200 * 16)
    elif name == "thermo":
        p.drawLine(QPointF(12, 5), QPointF(12, 14))
        p.drawArc(QRectF(9.5, 2.5, 5, 5), 0, 180 * 16)
        p.drawEllipse(QPointF(12, 17.5), 2.6, 2.6)
    elif name == "drop":
        path = QPainterPath(QPointF(12, 3.5))
        path.cubicTo(16, 9, 18, 11.5, 18, 14.2)
        path.cubicTo(18, 17.4, 15.3, 20, 12, 20)
        path.cubicTo(8.7, 20, 6, 17.4, 6, 14.2)
        path.cubicTo(6, 11.5, 8, 9, 12, 3.5)
        p.drawPath(path)
    elif name == "rain":
        path = QPainterPath()
        path.moveTo(6.5, 14)
        path.cubicTo(3.5, 14, 3, 10.5, 5.7, 9.4)
        path.cubicTo(6, 5.7, 11.5, 4.5, 13.6, 7.6)
        path.cubicTo(18.5, 6.6, 21, 11.2, 18.7, 14)
        p.drawPath(path)
        for x in (8, 12, 16):
            p.drawLine(QPointF(x, 17), QPointF(x - 1, 20.5))
    elif name == "play":
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath(QPointF(7.5, 4.5))
        path.lineTo(19, 12)
        path.lineTo(7.5, 19.5)
        path.closeSubpath()
        p.drawPath(path)
    elif name == "pause":
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(7, 5, 3.6, 14), 1.4, 1.4)
        p.drawRoundedRect(QRectF(13.4, 5, 3.6, 14), 1.4, 1.4)
    elif name == "stop":
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(6, 6, 12, 12), 3, 3)
    elif name == "refresh":
        p.drawArc(QRectF(4.5, 4.5, 15, 15), 40 * 16, 290 * 16)
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath(QPointF(17.2, 3.4))
        path.lineTo(20.4, 8.2)
        path.lineTo(15.2, 8.6)
        path.closeSubpath()
        p.drawPath(path)
    elif name == "close":
        p.drawLine(QPointF(6, 6), QPointF(18, 18))
        p.drawLine(QPointF(18, 6), QPointF(6, 18))
    elif name == "minimize":
        p.drawLine(QPointF(5, 12), QPointF(19, 12))
    elif name == "maximize":
        _rounded(p, 5.5, 5.5, 13, 13, 2)
    elif name == "restore":
        _rounded(p, 5, 8, 11, 11, 2)
        p.drawLine(QPointF(8, 8), QPointF(8, 5))
        p.drawLine(QPointF(8, 5), QPointF(19, 5))
        p.drawLine(QPointF(19, 5), QPointF(19, 16))
        p.drawLine(QPointF(16, 16), QPointF(16, 19))
    elif name == "chevron-down":
        p.drawLine(QPointF(6, 9.5), QPointF(12, 15.5))
        p.drawLine(QPointF(12, 15.5), QPointF(18, 9.5))
    elif name == "chevron-right":
        p.drawLine(QPointF(9.5, 6), QPointF(15.5, 12))
        p.drawLine(QPointF(15.5, 12), QPointF(9.5, 18))
    elif name == "chevron-left":
        p.drawLine(QPointF(14.5, 6), QPointF(8.5, 12))
        p.drawLine(QPointF(8.5, 12), QPointF(14.5, 18))
    elif name == "arrow-right":
        p.drawLine(QPointF(4, 12), QPointF(19, 12))
        p.drawLine(QPointF(13.5, 6.5), QPointF(19, 12))
        p.drawLine(QPointF(19, 12), QPointF(13.5, 17.5))
    elif name == "shield":
        path = QPainterPath(QPointF(12, 3))
        path.lineTo(19.5, 6)
        path.lineTo(19.5, 12)
        path.cubicTo(19.5, 17, 16, 20, 12, 21.2)
        path.cubicTo(8, 20, 4.5, 17, 4.5, 12)
        path.lineTo(4.5, 6)
        path.closeSubpath()
        p.drawPath(path)
    elif name == "radar":
        p.drawEllipse(QPointF(12, 12), 8, 8)
        p.drawEllipse(QPointF(12, 12), 4.6, 4.6)
        p.drawLine(QPointF(12, 12), QPointF(18, 6.5))
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(16.4, 8.2), 1.5, 1.5)
    elif name == "target":
        p.drawEllipse(QPointF(12, 12), 8, 8)
        p.drawEllipse(QPointF(12, 12), 3.4, 3.4)
        p.setBrush(c)
        p.drawEllipse(QPointF(12, 12), 1.2, 1.2)
    elif name == "layers":
        for dy in (0, 5.5):
            path = QPainterPath(QPointF(12, 3 + dy))
            path.lineTo(20.5, 7.5 + dy)
            path.lineTo(12, 12 + dy)
            path.lineTo(3.5, 7.5 + dy)
            path.closeSubpath()
            p.drawPath(path)
    elif name == "cpu":
        _rounded(p, 6, 6, 12, 12, 2.5)
        _rounded(p, 9.5, 9.5, 5, 5, 1.2)
        for v in (9, 15):
            p.drawLine(QPointF(v, 2.8), QPointF(v, 6))
            p.drawLine(QPointF(v, 18), QPointF(v, 21.2))
            p.drawLine(QPointF(2.8, v), QPointF(6, v))
            p.drawLine(QPointF(18, v), QPointF(21.2, v))
    elif name == "wifi":
        for i, r in enumerate((8.5, 5.8, 3.0)):
            p.drawArc(QRectF(12 - r, 12.5 - r, r * 2, r * 2), 45 * 16, 90 * 16)
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(12, 18.4), 1.4, 1.4)
    elif name == "clock":
        p.drawEllipse(QPointF(12, 12), 8.2, 8.2)
        p.drawLine(QPointF(12, 7.5), QPointF(12, 12))
        p.drawLine(QPointF(12, 12), QPointF(15.8, 14))
    elif name == "users":
        p.drawEllipse(QPointF(9.5, 8.5), 3.2, 3.2)
        p.drawArc(QRectF(3.5, 13, 12, 10), 0, 180 * 16)
        p.drawEllipse(QPointF(17, 9.5), 2.4, 2.4)
        p.drawArc(QRectF(13.5, 14.5, 8, 8), 0, 150 * 16)
    elif name == "user":
        p.drawEllipse(QPointF(12, 8.5), 3.6, 3.6)
        p.drawArc(QRectF(5, 13.5, 14, 12), 0, 180 * 16)
    elif name == "spray":
        _rounded(p, 7, 9, 6.5, 12, 2)
        p.drawLine(QPointF(10, 9), QPointF(10, 6))
        p.drawLine(QPointF(8.5, 6), QPointF(15.5, 6))
        p.drawLine(QPointF(15.5, 6), QPointF(15.5, 4))
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        for x, y in ((15, 10), (18.5, 12.5), (16.5, 16), (20, 7.5)):
            p.drawEllipse(QPointF(x, y), 1.2, 1.2)
    elif name == "lock":
        _rounded(p, 5.5, 10.5, 13, 10, 2.5)
        p.drawArc(QRectF(8.5, 4, 7, 9), 0, 180 * 16)
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(12, 15.5), 1.4, 1.4)
    elif name == "mail":
        _rounded(p, 3, 5.5, 18, 13, 2.5)
        p.drawLine(QPointF(4, 7), QPointF(12, 13))
        p.drawLine(QPointF(20, 7), QPointF(12, 13))
    elif name == "eye":
        path = QPainterPath(QPointF(2.5, 12))
        path.cubicTo(6, 6, 18, 6, 21.5, 12)
        path.cubicTo(18, 18, 6, 18, 2.5, 12)
        p.drawPath(path)
        p.drawEllipse(QPointF(12, 12), 2.6, 2.6)
    elif name == "volume":
        path = QPainterPath(QPointF(4, 9))
        path.lineTo(8, 9)
        path.lineTo(12.5, 5)
        path.lineTo(12.5, 19)
        path.lineTo(8, 15)
        path.lineTo(4, 15)
        path.closeSubpath()
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(path)
        p.setPen(_pen(c))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(QRectF(12, 7, 6, 10), -60 * 16, 120 * 16)
        p.drawArc(QRectF(12.5, 4.5, 9.5, 15), -55 * 16, 110 * 16)
    elif name == "mic":
        _rounded(p, 9, 3, 6, 11, 3)
        p.drawArc(QRectF(5.5, 8, 13, 11), 180 * 16, 180 * 16)
        p.drawLine(QPointF(12, 19), QPointF(12, 21.5))
        p.drawLine(QPointF(8.5, 21.5), QPointF(15.5, 21.5))
    elif name == "send":
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath(QPointF(3, 11))
        path.lineTo(21, 3.5)
        path.lineTo(13, 21)
        path.lineTo(11, 13)
        path.closeSubpath()
        p.drawPath(path)
    elif name == "camera":
        _rounded(p, 3, 7, 18, 12, 3)
        p.drawEllipse(QPointF(12, 13), 3.6, 3.6)
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(17.5, 10.2), 1.0, 1.0)
    elif name == "battery":
        _rounded(p, 3, 8, 16, 9, 2.5)
        p.drawLine(QPointF(21, 10.5), QPointF(21, 13.5))
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(5, 10, 10, 5), 1.2, 1.2)
    elif name == "signal":
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        for i, h in enumerate((4, 8, 12, 16)):
            p.drawRoundedRect(QRectF(3.5 + i * 5, 19.5 - h, 3, h), 1, 1)
    elif name == "alert":
        path = QPainterPath(QPointF(12, 3))
        path.lineTo(21.5, 20)
        path.lineTo(2.5, 20)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QPointF(12, 9), QPointF(12, 14))
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(12, 17), 1.2, 1.2)
    elif name == "check":
        p.drawLine(QPointF(4.5, 12.5), QPointF(9.5, 18))
        p.drawLine(QPointF(9.5, 18), QPointF(20, 6))
    elif name == "plus":
        p.drawLine(QPointF(12, 5), QPointF(12, 19))
        p.drawLine(QPointF(5, 12), QPointF(19, 12))
    elif name == "logout":
        path = QPainterPath()
        p.drawArc(QRectF(3.5, 4, 12, 16), 90 * 16, 180 * 16)
        p.drawLine(QPointF(11, 12), QPointF(21, 12))
        p.drawLine(QPointF(17, 8), QPointF(21, 12))
        p.drawLine(QPointF(21, 12), QPointF(17, 16))
    elif name == "power":
        p.drawArc(QRectF(4.5, 4.5, 15, 15), -60 * 16, 300 * 16)
        p.drawLine(QPointF(12, 2.5), QPointF(12, 11.5))
    elif name == "activity":
        p.drawPolyline(
            [
                QPointF(3, 13),
                QPointF(7.5, 13),
                QPointF(10, 6),
                QPointF(13.5, 19),
                QPointF(16, 10),
                QPointF(18, 13),
                QPointF(21, 13),
            ]
        )
    elif name == "compass":
        p.drawEllipse(QPointF(12, 12), 8.2, 8.2)
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath(QPointF(12, 6.5))
        path.lineTo(15, 12)
        path.lineTo(12, 17.5)
        path.lineTo(9, 12)
        path.closeSubpath()
        p.drawPath(path)
    elif name == "satellite":
        p.save()
        p.translate(12, 12)
        p.rotate(-35)
        _rounded(p, -3, -6.5, 6, 13, 2)
        p.drawLine(QPointF(-7, -6), QPointF(7, -6))
        p.drawLine(QPointF(-7, 6), QPointF(7, 6))
        p.restore()
        p.drawArc(QRectF(3, 3, 9, 9), 200 * 16, 110 * 16)
    elif name == "home":
        path = QPainterPath(QPointF(4, 11))
        path.lineTo(12, 4)
        path.lineTo(20, 11)
        p.drawPath(path)
        p.drawLine(QPointF(6.5, 10), QPointF(6.5, 20))
        p.drawLine(QPointF(17.5, 10), QPointF(17.5, 20))
        p.drawLine(QPointF(6.5, 20), QPointF(17.5, 20))
        p.drawLine(QPointF(10.5, 20), QPointF(10.5, 14.5))
        p.drawLine(QPointF(13.5, 20), QPointF(13.5, 14.5))
    elif name == "filter":
        p.drawPolyline([QPointF(3.5, 5.5), QPointF(20.5, 5.5), QPointF(13.5, 13), QPointF(13.5, 20), QPointF(10.5, 18), QPointF(10.5, 13), QPointF(3.5, 5.5)])
    elif name == "info":
        p.drawEllipse(QPointF(12, 12), 8.4, 8.4)
        p.drawLine(QPointF(12, 11), QPointF(12, 16.5))
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(12, 8), 1.2, 1.2)
    elif name == "sparkles":
        for cx, cy, r in ((9, 8, 4), (17, 15, 3), (15, 6, 1.4)):
            p.drawEllipse(QPointF(cx, cy), r, r)
        p.drawLine(QPointF(9, 2.5), QPointF(9, 5))
        p.drawLine(QPointF(9, 11), QPointF(9, 13.5))
    elif name == "link":
        p.drawArc(QRectF(2.5, 8, 10, 8), 90 * 16, 180 * 16)
        p.drawArc(QRectF(11.5, 8, 10, 8), 270 * 16, 180 * 16)
        p.drawLine(QPointF(8.5, 12), QPointF(15.5, 12))
    elif name == "download":
        p.drawLine(QPointF(12, 3.5), QPointF(12, 15))
        p.drawLine(QPointF(7, 10.5), QPointF(12, 15.5))
        p.drawLine(QPointF(17, 10.5), QPointF(12, 15.5))
        p.drawPolyline([QPointF(4, 17), QPointF(4, 20.5), QPointF(20, 20.5), QPointF(20, 17)])
    elif name == "trash":
        p.drawLine(QPointF(4, 6.5), QPointF(20, 6.5))
        p.drawLine(QPointF(9, 6.5), QPointF(9, 3.8))
        p.drawLine(QPointF(9, 3.8), QPointF(15, 3.8))
        p.drawLine(QPointF(15, 3.8), QPointF(15, 6.5))
        path = QPainterPath(QPointF(6.5, 6.5))
        path.lineTo(7.5, 20.5)
        path.lineTo(16.5, 20.5)
        path.lineTo(17.5, 6.5)
        p.drawPath(path)
    else:  # 兜底：圆点
        p.drawEllipse(QPointF(12, 12), 6, 6)


@lru_cache(maxsize=1024)
def render(name: str, color: str = "#3D5449", size: int = 20, ratio: float = 2.0) -> QPixmap:
    """渲染为带 devicePixelRatio 的 pixmap（用于 QLabel.setPixmap）。"""
    pm = QPixmap(int(size * ratio), int(size * ratio))
    pm.setDevicePixelRatio(ratio)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.scale(size * ratio / _M, size * ratio / _M)
    _draw(painter, name, QColor(color))
    painter.end()
    return pm


@lru_cache(maxsize=512)
def _flat(name: str, color: str, pixels: int) -> QPixmap:
    """渲染为 DPR=1 的像素图，供 QIcon 使用（避免缩放裁切）。"""
    pm = QPixmap(pixels, pixels)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.scale(pixels / _M, pixels / _M)
    _draw(painter, name, QColor(color))
    painter.end()
    return pm


def icon(name: str, color: str = "#3D5449", size: int = 20) -> QIcon:
    ic = QIcon()
    ic.addPixmap(_flat(name, color, int(size)))
    ic.addPixmap(_flat(name, color, int(size * 2)))
    return ic


def pixmap(name: str, color: str = "#3D5449", size: int = 20) -> QPixmap:
    """返回 1:1 像素图：QLabel / QPainter 均按实际像素绘制，避免 DPR 缩放裁切。"""
    return _flat(name, color, int(size))
