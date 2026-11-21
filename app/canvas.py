"""自绘可视化画布：林区地图、AI 视觉识别、空地协同示意、灭火编队、语音波形。"""
from __future__ import annotations

import math
import os
import random
from typing import Sequence

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import (
    QBrush,
    QImage,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QSizePolicy, QWidget

from . import icons, theme
from .simulation import BASES, FireSpreadModel, SimEngine

C = QColor


def datetime_now() -> str:
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M')



def _qcolor(hex_or_color, alpha: int | None = None) -> QColor:
    c = QColor(hex_or_color)
    if alpha is not None:
        c.setAlpha(alpha)
    return c


def _font(size: float, weight: int = 500) -> QFont:
    f = QFont(theme.FONT_FAMILY)
    f.setPixelSize(max(8, int(size)))
    f.setWeight(QFont.Weight(weight))
    return f


class TerrainMap(QWidget):
    """林区态势地图（矢量绘制，支持 SLAM / 热力 / 编队图层）。

    mode: "overview" | "navigation" | "analysis"
    """

    clicked_map = Signal(float, float)
    hovered = Signal(str)
    robot_selected = Signal(str)
    fire_selected = Signal(str)

    def __init__(self, engine: SimEngine, mode: str = "overview", parent=None,
                 show_legend: bool = True):
        super().__init__(parent)
        self.engine = engine
        self.mode = mode
        self.show_lidar = mode == "navigation"
        self.show_costmap = mode == "navigation"
        self.show_heat = mode == "analysis"
        self.show_legend = show_legend
        self.show_path = mode == "navigation"
        self.fire_frame = 0
        self.phase = 0.0
        self.minutes = 30
        self.selected_robot = None
        self.selected_fire_id = None
        self.select_fires = False
        self._prediction_key = None
        self._prediction = None
        self._show_robots = True
        self._highlight = 0.0
        self._static: QPixmap | None = None
        self._spread = FireSpreadModel()
        self.setMinimumHeight(240)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._advance)
        self._timer.start()

    # ------------------------------------------------------------------
    def _advance(self):
        if not self.isVisible():
            return
        self.phase += 0.06
        self.fire_frame += 1
        if self._highlight > 0:
            self._highlight = max(0.0, self._highlight - 0.02)
        self.update()

    def set_mode(self, mode: str):
        self.mode = mode
        self.show_lidar = mode == "navigation"
        self.show_costmap = mode == "navigation"
        self.show_heat = mode == "analysis"
        self.show_path = mode == "navigation"
        self.update()

    def set_minutes(self, minutes: int):
        self.minutes = minutes
        self.update()

    def set_lidar_visible(self, visible: bool):
        self.show_lidar = visible
        self.update()

    def set_costmap_visible(self, visible: bool):
        self.show_costmap = visible
        self.update()

    def set_heat_visible(self, visible: bool):
        self.show_heat = visible
        self.update()

    def set_robots_visible(self, visible: bool):
        self._show_robots = visible
        self.update()

    def set_center_fire(self):
        self._highlight = 3.2
        self.update()

    def set_static_dirty(self):
        self._static = None
        self.update()

    def resizeEvent(self, event):
        self._static = None
        super().resizeEvent(event)

    # ------------------------------------------------------------------
    def _content(self) -> QRectF:
        w, h = self.width(), self.height()
        pad = 12
        return QRectF(pad, pad, max(10, w - 2 * pad), max(10, h - 2 * pad))

    def pt(self, xy) -> QPointF:
        r = self._content()
        return QPointF(r.left() + xy[0] * r.width(), r.top() + xy[1] * r.height())

    def norm(self, pos: QPointF):
        r = self._content()
        return ((pos.x() - r.left()) / r.width(), (pos.y() - r.top()) / r.height())

    # ------------------------------------------------------------------
    def _build_static(self) -> QPixmap:
        ratio = self.devicePixelRatioF() or 1.0
        pm = QPixmap(int(self.width() * ratio), int(self.height() * ratio))
        pm.setDevicePixelRatio(ratio)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self._content()
        rng = random.Random(42)

        # 底图渐变
        base = QLinearGradient(r.topLeft(), r.bottomRight())
        base.setColorAt(0.0, C("#F4FBF6"))
        base.setColorAt(0.55, C("#EDF7F0"))
        base.setColorAt(1.0, C("#E4F2EA"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(base)
        p.drawRoundedRect(r, 16, 16)

        # 网格
        p.setPen(QPen(_qcolor(theme.ACCENT, 16), 1))
        for i in range(1, 12):
            x = r.left() + r.width() * i / 12
            p.drawLine(QPointF(x, r.top()), QPointF(x, r.bottom()))
        for i in range(1, 8):
            y = r.top() + r.height() * i / 8
            p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))

        # 林地块
        patches = [
            (0.20, 0.26, 0.20, "#D8EEDA"),
            (0.76, 0.24, 0.17, "#DDF0DC"),
            (0.30, 0.66, 0.18, "#D4ECD8"),
            (0.72, 0.74, 0.16, "#DCEFDE"),
            (0.52, 0.30, 0.13, "#E1F2E0"),
        ]
        for cx, cy, rad, color in patches:
            path = QPainterPath()
            n = 22
            for i in range(n + 1):
                a = 2 * math.pi * i / n
                rr = rad * (1 + 0.20 * math.sin(3 * a + cx * 9) + 0.11 * math.cos(5 * a + cy * 7))
                px = r.left() + (cx + rr * math.cos(a) * 1.15) * r.width()
                py = r.top() + (cy + rr * math.sin(a) * 0.85) * r.height()
                if i == 0:
                    path.moveTo(px, py)
                else:
                    path.lineTo(px, py)
            path.closeSubpath()
            p.setPen(QPen(_qcolor("#8FCBA4", 120), 1.1))
            p.setBrush(C(color))
            p.drawPath(path)
            # 树冠纹理
            p.setPen(QPen(_qcolor("#7FC09A", 90), 1))
            for _ in range(16):
                tx = r.left() + (cx + rng.uniform(-rad, rad) * 0.95) * r.width()
                ty = r.top() + (cy + rng.uniform(-rad, rad) * 0.7) * r.height()
                p.drawPoint(QPointF(tx, ty))

        # 等高线
        for hx, hy, hrad, count in ((0.26, 0.30, 0.115, 6), (0.70, 0.62, 0.14, 7), (0.46, 0.80, 0.08, 4)):
            for k in range(count):
                path = QPainterPath()
                rr = hrad * (0.35 + k * 0.15)
                for i in range(49):
                    a = 2 * math.pi * i / 48
                    wob = 1 + 0.10 * math.sin(3 * a + k * 0.7) + 0.05 * math.cos(4 * a - k)
                    px = r.left() + (hx + rr * math.cos(a) * 1.15 * wob) * r.width()
                    py = r.top() + (hy + rr * math.sin(a) * 0.82 * wob) * r.height()
                    if i == 0:
                        path.moveTo(px, py)
                    else:
                        path.lineTo(px, py)
                p.setPen(QPen(_qcolor(theme.ACCENT_DARK, 55), 1))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawPath(path)

        # 河流
        river = QPainterPath(QPointF(r.left() - 8, r.top() + r.height() * 0.12))
        river.cubicTo(
            r.left() + r.width() * 0.18, r.top() + r.height() * 0.30,
            r.left() + r.width() * 0.30, r.top() + r.height() * 0.36,
            r.left() + r.width() * 0.42, r.top() + r.height() * 0.55,
        )
        river.cubicTo(
            r.left() + r.width() * 0.55, r.top() + r.height() * 0.75,
            r.left() + r.width() * 0.72, r.top() + r.height() * 0.72,
            r.left() + r.width() + 8, r.top() + r.height() * 0.92,
        )
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(C("#CBE9F7"), 13))
        p.drawPath(river)
        p.setPen(QPen(C("#A9DCF2"), 7))
        p.drawPath(river)

        # 山路
        road = QPainterPath(QPointF(r.left() + r.width() * 0.02, r.top() + r.height() * 0.92))
        road.cubicTo(
            r.left() + r.width() * 0.30, r.top() + r.height() * 0.86,
            r.left() + r.width() * 0.46, r.top() + r.height() * 0.62,
            r.left() + r.width() * 0.62, r.top() + r.height() * 0.42,
        )
        road.cubicTo(
            r.left() + r.width() * 0.74, r.top() + r.height() * 0.28,
            r.left() + r.width() * 0.86, r.top() + r.height() * 0.18,
            r.left() + r.width() * 0.98, r.top() + r.height() * 0.10,
        )
        pen = QPen(C("#E7E1D2"), 4)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([3, 4])
        p.setPen(pen)
        p.drawPath(road)

        # 网格坐标标注
        p.setFont(_font(8.5))
        p.setPen(_qcolor(theme.MUTED, 150))
        for i in range(6):
            x = r.left() + r.width() * (i + 0.5) / 6
            p.drawText(QRectF(x - 20, r.bottom() - 16, 40, 12),
                       Qt.AlignmentFlag.AlignCenter, f"{chr(65 + i)}")
        for i in range(4):
            y = r.top() + r.height() * (i + 0.5) / 4
            p.drawText(QRectF(r.left() + 3, y - 7, 22, 14),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, f"{i + 1:02d}")

        # 边框
        p.setPen(QPen(_qcolor(theme.BORDER_STRONG, 170), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r, 16, 16)
        p.end()
        return pm

    # ------------------------------------------------------------------
    def paintEvent(self, event):
        if self._static is None:
            self._static = self._build_static()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.drawPixmap(0, 0, self._static)
        r = self._content()
        p.save()
        clip = QPainterPath()
        clip.addRoundedRect(r, 16, 16)
        p.setClipPath(clip)

        if self.show_heat and any(f.state != "extinguished" for f in self.engine.fires):
            self._paint_heat(p, r)
        self._paint_bases(p, r)
        self._paint_fire(p, r)
        if self.show_path:
            self._paint_path(p, r)
        self._paint_robots(p, r)
        p.restore()
        self._paint_compass(p, r)
        if self.show_legend:
            self._paint_legend(p, r)
        p.end()

    # ------------------------------------------------------------------
    def set_selected_fire(self, fire_id: str | None):
        if self.selected_fire_id != fire_id:
            self.selected_fire_id = fire_id
            self._prediction_key = None
            self.update()

    def _paint_heat(self, p: QPainter, r: QRectF):
        fires = [f for f in self.engine.fires if f.state != "extinguished"]
        if not fires:
            return
        key = (tuple((f.id, f.origin, f.intensity, f.state) for f in fires), self.minutes,
               self.engine.wind_deg, self.engine.wind_speed, self.engine.humidity)
        if key != self._prediction_key:
            self._prediction = self._spread.assess_all(fires, self.minutes, self.engine.wind_deg,
                                                       self.engine.wind_speed, self.engine.humidity)
            self._prediction_key = key
        prediction = self._prediction
        grid = prediction["grid"]
        h, w = len(grid), len(grid[0])
        img = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(0)
        for y in range(h):
            for x in range(w):
                v = grid[y][x]
                if v < 0.10:
                    continue
                if v > 0.66:
                    color = QColor(226, 62, 66, int(110 + v * 70))
                elif v > 0.40:
                    color = QColor(240, 146, 52, int(80 + v * 70))
                else:
                    color = QColor(248, 202, 118, int(45 + v * 60))
                img.setPixelColor(x, y, color)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        p.drawImage(r, img)

        # 每条隔离带对应一个火点；选中的火点加粗，无法避让时标红提示复核。
        ordered = sorted(fires, key=lambda f: f.id == self.selected_fire_id)
        for fire in ordered:
            item = prediction["fires"][fire.id]
            points = [self.pt(point) for point in item["line"]]
            path = QPainterPath(points[0])
            for point in points[1:]:
                path.lineTo(point)
            selected = fire.id == self.selected_fire_id
            color = C(theme.RED if item["line_conflict"] else theme.AMBER)
            # 透明宽线表示隔离带的面积；中心虚线是建议路径。
            width = max(6.0, item["width_m"] / 1200 * r.width())
            band = QColor(color)
            band.setAlpha(75 if selected else 50)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(band, width + 3, Qt.PenStyle.SolidLine,
                          Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            p.drawPath(path)
            p.setPen(QPen(C("#FFFFFF"), 4 if selected else 3))
            p.drawPath(path)
            p.setPen(QPen(color, 2.5 if selected else 1.5, Qt.PenStyle.DashLine))
            p.drawPath(path)
            p.setFont(_font(9 if selected else 8, 700))
            p.setPen(QPen(color))
            p.drawText(points[len(points) // 2] + QPointF(4, -7), fire.id)

    def highlight_fire(self):
        self._highlight = 3.2
        self.update()

    def _paint_bases(self, p: QPainter, r: QRectF):
        for _bid, bname, bx, by in BASES:
            pt = self.pt((bx, by))
            p.setPen(QPen(C(theme.ACCENT_DARK), 1.5))
            p.setBrush(QColor(255, 255, 255, 225))
            p.drawRoundedRect(QRectF(pt.x() - 8, pt.y() - 8, 16, 16), 4, 4)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(C(theme.ACCENT))
            p.drawEllipse(pt, 3.5, 3.5)
            p.setFont(_font(8, 700))
            p.setPen(C(theme.ACCENT_DARK))
            p.drawText(QPointF(pt.x() + 11, pt.y() + 4), bname)

    def _paint_fire(self, p: QPainter, r: QRectF):
        fires = self.engine.fires
        if not fires:
            return
        for f in fires:
            if self.select_fires and f.state == "extinguished":
                continue
            center = self.pt(f.origin)
            if self.select_fires and f.id == self.selected_fire_id:
                p.setPen(QPen(C("#FFFFFF"), 3))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(center, 16, 16)
            if f.state == "extinguished" or f.intensity <= 0.1:
                p.setPen(QPen(C(theme.ACCENT), 2))
                p.setBrush(QColor(18, 166, 106, 40))
                p.drawEllipse(center, 16, 16)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(C(theme.ACCENT))
                p.drawEllipse(center, 5, 5)
                p.setFont(_font(9, 700))
                p.setPen(C(theme.ACCENT_DARK))
                p.drawText(QPointF(center.x() + 11, center.y() - 5), f"{f.id} 已扑灭 ✓")
                continue

            scale = 0.45 + 0.65 * (f.intensity / 100.0)
            pulse = (1 + 0.08 * math.sin(self.phase * 2.2)) * scale
            rad = QRectF(center.x() - 46 * pulse, center.y() - 46 * pulse, 92 * pulse, 92 * pulse)
            grad = QRadialGradient(center, 52 * pulse)
            grad.setColorAt(0.0, QColor(255, 120, 60, 230))
            grad.setColorAt(0.35, QColor(255, 175, 60, 150))
            grad.setColorAt(0.7, QColor(255, 210, 120, 60))
            grad.setColorAt(1.0, QColor(255, 220, 150, 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(grad)
            p.drawEllipse(rad)

            p.setBrush(C(theme.AMBER if f.state == "suspicious" else theme.RED))
            p.drawEllipse(center, 5.5, 5.5)
            p.setBrush(QColor(255, 255, 255, 230))
            p.drawEllipse(center, 2.2, 2.2)

            smoke_count = max(1, int(5 * (f.intensity / 100.0)))
            for i in range(smoke_count):
                t = (self.phase * 0.6 + i * 0.21) % 1.0
                alpha = int(120 * (1 - t) * (f.intensity / 100.0))
                p.setBrush(QColor(120, 130, 126, alpha))
                px = center.x() + math.sin(t * 6 + i) * (12 + 26 * t) - t * 8
                py = center.y() - 6 - 52 * t
                rad_s = (7 + 12 * t) * scale
                p.drawEllipse(QPointF(px, py), rad_s, rad_s)

            p.setFont(_font(9, 700))
            p.setPen(C(theme.AMBER if f.state == "suspicious" else theme.RED))
            tag = f"可疑 {f.id}" if f.state == "suspicious" else f"火点 {f.id} ({f.intensity:.0f}%)"
            p.drawText(QPointF(center.x() + 12, center.y() - 10), tag)

    def _paint_costmap(self, p: QPainter, r: QRectF):
        center = self.pt(self.engine.fire_origin)
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(4):
            rad = 40 + i * 22
            p.setBrush(QColor(229, 72, 77, 16))
            p.drawEllipse(center, rad, rad)
        for obs in ((0.36, 0.30), (0.48, 0.46), (0.31, 0.52)):
            c = self.pt(obs)
            p.setBrush(QColor(242, 169, 59, 60))
            p.drawEllipse(c, 16, 13)
            p.setPen(QPen(C(theme.AMBER), 1.2, Qt.PenStyle.DashLine))
            p.drawEllipse(c, 20, 16)
            p.setPen(Qt.PenStyle.NoPen)

    def _paint_path(self, p: QPainter, r: QRectF):
        path_pts = [self.pt(xy) for xy in self.engine.plan.path]
        path = QPainterPath(path_pts[0])
        for i in range(1, len(path_pts)):
            a, b = path_pts[i - 1], path_pts[i]
            mid = (a + b) / 2
            path.quadTo(a, mid)

        pen = QPen(QColor(255, 255, 255, 200), 7)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

        grad = QLinearGradient(path_pts[0], path_pts[-1])
        grad.setColorAt(0.0, C(theme.ACCENT))
        grad.setColorAt(0.6, C(theme.ACCENT_LIGHT))
        grad.setColorAt(1.0, C(theme.AMBER))
        pen = QPen(QBrush(grad), 3.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([6, 4])
        pen.setDashOffset(-self.phase * 10)
        p.setPen(pen)
        p.drawPath(path)

        start = path_pts[0]
        end = path_pts[-1]
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(C("#FFFFFF"))
        p.drawEllipse(start, 8, 8)
        p.setBrush(C(theme.ACCENT))
        p.drawEllipse(start, 4.6, 4.6)
        p.setFont(_font(9, 700))
        p.setPen(C(theme.ACCENT_DARK))
        p.drawText(QPointF(start.x() + 12, start.y() + 4), "起点")

        # 火点目标标记
        p.setBrush(QColor(255, 255, 255, 220))
        p.setPen(QPen(C(theme.AMBER), 2))
        p.drawEllipse(end, 9, 9)
        p.setPen(QPen(C(theme.AMBER), 2))
        p.drawLine(end + QPointF(-13, 0), end + QPointF(-5, 0))
        p.drawLine(end + QPointF(5, 0), end + QPointF(13, 0))
        p.drawLine(end + QPointF(0, -13), end + QPointF(0, -5))
        p.drawLine(end + QPointF(0, 5), end + QPointF(0, 13))

        # 沿路径运动的机器人（已移除假循环动画，由 SimEngine 实时驱动）

    def _paint_lidar(self, p: QPainter, r: QRectF):
        robot = next((x for x in self.engine.robots if x.id == "UGV-01"), self.engine.robots[0])
        origin = self.pt((robot.x, robot.y))
        p.setPen(Qt.PenStyle.NoPen)
        fan = QPainterPath(origin)
        fan.arcTo(QRectF(origin.x() - 72, origin.y() - 72, 144, 144), -160, 140)
        fan.closeSubpath()
        p.setBrush(QColor(18, 166, 106, 22))
        p.drawPath(fan)

        rng = random.Random(int(self.phase * 6))
        p.setPen(QPen(QColor(18, 166, 106, 90), 1))
        for i in range(26):
            ang = math.radians(-160 + i * (140 / 25) + rng.uniform(-2, 2))
            dist = rng.uniform(38, 70)
            end = QPointF(origin.x() + math.cos(ang) * dist, origin.y() + math.sin(ang) * dist)
            p.drawLine(origin, end)
            p.setBrush(QColor(18, 166, 106, 140))
            p.drawEllipse(end, 1.4, 1.4)

        # 障碍物回波
        for obs in ((0.36, 0.30), (0.48, 0.46)):
            c = self.pt(obs)
            p.setBrush(QColor(229, 72, 77, 170))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(c, 3, 3)

    def _paint_robots(self, p: QPainter, r: QRectF):
        if not self._show_robots:
            return
        fire_pt = self.pt(self.engine.fire_origin)
        for robot in self.engine.robots:
            if self.mode == "navigation" and robot.kind == "UGV":
                continue
            pos = self.pt((robot.x, robot.y))
            if robot.battery < 20 or robot.temp > 50 or robot.status == "offline":
                color = theme.RED          # 危险中
            elif robot.mission in ("en_route", "spraying", "recon"):
                color = "#F59E0B"          # 被调度中
            elif robot.mission == "patrol":
                color = theme.ACCENT       # 巡逻中
            else:
                color = theme.BLUE         # 待命 / 充电中

            # 赶赴火点虚线轨迹
            if robot.mission == "en_route":
                tpt = self.pt((robot.target_x, robot.target_y))
                pen = QPen(QColor(color), 1.4, Qt.PenStyle.DashLine)
                pen.setDashPattern([4, 4])
                p.setPen(pen)
                p.drawLine(pos, tpt)

            # 灭火喷洒水柱 / 粒子动画
            if robot.spraying and self.engine.fire.state != "extinguished":
                p.setPen(QPen(QColor(24, 174, 196, 160), 2.2))
                p.drawLine(pos, fire_pt)
                p.setPen(Qt.PenStyle.NoPen)
                for k in range(4):
                    t = (self.phase * 1.4 + k * 0.25) % 1.0
                    sx = pos.x() + (fire_pt.x() - pos.x()) * t
                    sy = pos.y() + (fire_pt.y() - pos.y()) * t
                    p.setBrush(QColor(56, 189, 248, int(220 * (1 - t * 0.5))))
                    p.drawEllipse(QPointF(sx, sy), 3.2, 3.2)

            is_docked = robot.mission == "idle" and robot.status in ("standby", "charging")
            if is_docked:
                # 在基地内以 2x4 小圆点网格排列，确保 8 台装备全部可见且不重叠
                docked_list = [
                    rb.id for rb in self.engine.robots
                    if rb.mission == "idle" and rb.status in ("standby", "charging")
                    and abs(rb.x - robot.x) < 0.08 and abs(rb.y - robot.y) < 0.08
                ]
                idx = docked_list.index(robot.id) if robot.id in docked_list else 0
                col, row = idx % 4, idx // 4
                pos = QPointF(pos.x() + (col - 1.5) * 11, pos.y() + (row - 0.5) * 11 - 14)
            self._draw_badge(p, pos, "drone" if robot.kind == "UAV" else "robot",
                             color, "",
                             highlight=robot.id == self.selected_robot,
                             small=is_docked)

    def _draw_badge(self, p: QPainter, pos: QPointF, icon_name: str, color: str,
                    text: str, highlight: bool = False, small: bool = False):
        radius = (4.5 if small else 13) if not highlight else (6.5 if small else 15)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 235))
        p.drawEllipse(pos, radius, radius)
        p.setBrush(QColor(color))
        p.drawEllipse(pos, radius - 1.5, radius - 1.5)
        if not small:
            pm = icons.pixmap(icon_name, "#FFFFFF", 14)
            p.drawPixmap(QPointF(pos.x() - 7, pos.y() - 7), pm)
        if highlight:
            p.setPen(QPen(QColor(color), 2, Qt.PenStyle.DashLine))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(pos, radius + 7, radius + 7)
        if not text:
            return
        p.setFont(_font(8.5, 700))
        fm_w = 26
        p.setPen(C("#FFFFFF"))
        p.setBrush(QColor(20, 37, 28, 205))
        p.drawRoundedRect(QRectF(pos.x() - fm_w / 2, pos.y() + radius + 3, fm_w, 13), 4, 4)
        p.setPen(C("#FFFFFF"))
        p.drawText(QRectF(pos.x() - fm_w / 2, pos.y() + radius + 3, fm_w, 13),
                   Qt.AlignmentFlag.AlignCenter, text)

    def _paint_compass(self, p: QPainter, r: QRectF):
        center = QPointF(r.right() - 42, r.top() + 42)
        p.setPen(QPen(QColor(255, 255, 255, 220), 1))
        p.setBrush(QColor(255, 255, 255, 190))
        p.drawEllipse(center, 24, 24)
        ang = math.radians(self.engine.wind_deg + 180)
        tip = QPointF(center.x() + math.cos(ang) * 15, center.y() + math.sin(ang) * 15)
        tail = QPointF(center.x() - math.cos(ang) * 11, center.y() - math.sin(ang) * 11)
        p.setPen(QPen(C(theme.BLUE), 2.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(tail, tip)
        # 箭头
        left = QPointF(tip.x() - math.cos(ang - 0.5) * 6, tip.y() - math.sin(ang - 0.5) * 6)
        right = QPointF(tip.x() - math.cos(ang + 0.5) * 6, tip.y() - math.sin(ang + 0.5) * 6)
        p.setBrush(C(theme.BLUE))
        p.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath(tip)
        path.lineTo(left)
        path.lineTo(right)
        path.closeSubpath()
        p.drawPath(path)
        p.setFont(_font(8, 700))
        p.setPen(C(theme.TEXT_SOFT))
        label = self.engine.wind_label().split(" ")[0]
        p.drawText(QRectF(center.x() - 26, center.y() + 25, 52, 14),
                   Qt.AlignmentFlag.AlignCenter, label)

    def _paint_legend(self, p: QPainter, r: QRectF):
        items = [
            (theme.RED, "火点/危险"),
            (theme.BLUE, "待命充电"),
            ("#F59E0B", "被调度中"),
            (theme.ACCENT, "巡逻中"),
            (theme.ACCENT_DARK, "基地"),
        ]
        if self.select_fires:
            items = [(theme.RED, "火点"), ("#F09234", "潜在燃烧区"), (theme.AMBER, "建议隔离带")]
        elif self.show_heat:
            items.append((theme.AMBER, "蔓延概率"))
        x = r.left() + 15
        y = r.top() + 18
        p.setFont(_font(9, 600))
        for color, text in items:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(C(color))
            p.drawEllipse(QPointF(x + 4, y), 3.5, 3.5)
            p.setPen(C(theme.TEXT_SOFT))
            p.drawText(QPointF(x + 12, y + 4), text)
            x += 20 + len(text) * 11
        # 图例底板
        # (直接绘制，避免额外底色)

    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._content().contains(event.position()):
            pos = event.position()
            if self.select_fires:
                active = [f for f in self.engine.fires if f.state != "extinguished"]
                nearest = min(active, key=lambda f: math.hypot(pos.x() - self.pt(f.origin).x(),
                                                                 pos.y() - self.pt(f.origin).y()), default=None)
                if nearest and math.hypot(pos.x() - self.pt(nearest.origin).x(),
                                          pos.y() - self.pt(nearest.origin).y()) <= 24:
                    self.fire_selected.emit(nearest.id)
                return
            for r in self.engine.robots if self._show_robots else []:
                pt = self.pt((r.x, r.y))
                if math.hypot(pos.x() - pt.x(), pos.y() - pt.y()) <= 20:
                    self.selected_robot = r.id
                    self.robot_selected.emit(r.id)
                    self.update()
                    break
            nx, ny = self.norm(pos)
            self.clicked_map.emit(nx, ny)
        super().mousePressEvent(event)


# ---------------------------------------------------------------------------
class CameraView(QWidget):
    """AI 视觉识别画面（明火 / 烟雾 / 正常环境）。"""

    def __init__(self, engine: SimEngine | None = None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.phase = 0.0
        self.mode = "rgb"  # rgb | thermal
        self.show_boxes = True
        self.setMinimumHeight(190)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._timer = QTimer(self)
        self._timer.setInterval(70)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self):
        if theme.ANIMATIONS and self.isVisible():
            self.phase += 0.08
            self.update()

    def set_thermal(self, thermal: bool):
        self.mode = "thermal" if thermal else "rgb"
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        p.save()
        clip = QPainterPath()
        clip.addRoundedRect(r.adjusted(0.5, 0.5, -0.5, -0.5), 12, 12)
        p.setClipPath(clip)
        w, h = r.width(), r.height()
        thermal = self.mode == "thermal"

        # 天空
        sky = QLinearGradient(0, 0, 0, h * 0.75)
        if thermal:
            sky.setColorAt(0, C("#171A33"))
            sky.setColorAt(0.6, C("#39203A"))
            sky.setColorAt(1, C("#5B3040"))
        else:
            sky.setColorAt(0, C("#CFE7F2"))
            sky.setColorAt(0.55, C("#E7F1E4"))
            sky.setColorAt(1, C("#F3F1DF"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(sky)
        p.drawRect(r)

        # 阳光光晕
        if not thermal:
            glow = QRadialGradient(QPointF(w * 0.18, h * 0.12), w * 0.5)
            glow.setColorAt(0, QColor(255, 248, 214, 140))
            glow.setColorAt(1, QColor(255, 248, 214, 0))
            p.setBrush(glow)
            p.drawRect(r)

        # 远山两层
        for base_y, color, amp in ((0.68, "#A9C9AE", 0.10), (0.76, "#8FB597", 0.07)):
            hill = QPainterPath(QPointF(0, h * base_y))
            hill.cubicTo(w * 0.16, h * (base_y - amp), w * 0.3, h * (base_y + amp * 0.4),
                         w * 0.46, h * (base_y - amp * 0.2))
            hill.cubicTo(w * 0.62, h * (base_y - amp), w * 0.8, h * (base_y + amp * 0.5),
                         w, h * (base_y - amp * 0.3))
            hill.lineTo(w, h)
            hill.lineTo(0, h)
            hill.closeSubpath()
            p.setBrush(QColor(color) if not thermal else QColor(62, 34, 58))
            p.drawPath(hill)

        # 树列（两层，远近区分）
        rng = random.Random(9)
        for layer, count, scale, alpha in ((0, 16, 0.30, 200), (1, 11, 0.44, 255)):
            for i in range(count):
                x = w * (i + 0.4 + (layer * 0.3)) / count
                base = h * (0.80 + rng.uniform(-0.03, 0.03) + layer * 0.06)
                th = h * rng.uniform(scale * 0.8, scale)
                if thermal:
                    color = QColor(38 + layer * 8, 26, 44 + layer * 6, alpha)
                else:
                    color = QColor(68 + layer * 14 + rng.randint(-8, 8),
                                   112 + layer * 12 + rng.randint(-10, 10),
                                   84 + layer * 8, alpha)
                tree = QPainterPath(QPointF(x, base - th))
                tree.cubicTo(x + th * 0.10, base - th * 0.5,
                             x + th * 0.20, base - th * 0.2,
                             x + th * 0.24, base)
                tree.lineTo(x - th * 0.24, base)
                tree.cubicTo(x - th * 0.20, base - th * 0.2,
                             x - th * 0.10, base - th * 0.5,
                             x, base - th)
                p.setBrush(color)
                p.drawPath(tree)

        # 地面
        ground = QLinearGradient(0, h * 0.78, 0, h)
        ground.setColorAt(0, C("#7CA878") if not thermal else C("#4C2A3C"))
        ground.setColorAt(1, C("#5C8A5E") if not thermal else C("#271524"))
        p.setBrush(ground)
        p.drawRect(QRectF(0, h * 0.80, w, h * 0.20))

        # 火焰（多层火舌）
        fx, fy = w * 0.71, h * 0.86
        pulse = 1 + 0.10 * math.sin(self.phase * 2.6)
        glow = QRadialGradient(QPointF(fx, fy - 12), 58 * pulse)
        glow.setColorAt(0, QColor(255, 200, 110, 220))
        glow.setColorAt(0.45, QColor(255, 130, 50, 130))
        glow.setColorAt(1, QColor(255, 100, 40, 0))
        p.setBrush(glow)
        p.drawEllipse(QPointF(fx, fy - 10), 62 * pulse, 54 * pulse)

        for k, (sw, ky, color) in enumerate((
                (17, 40, QColor(255, 120, 48, 220)),
                (12, 46, QColor(255, 174, 62, 235)),
                (6.5, 30, QColor(255, 232, 150, 240)))):
            tongue = QPainterPath(QPointF(fx + math.sin(self.phase * 2 + k) * 2.5, fy - ky * pulse))
            tongue.cubicTo(fx + sw, fy - ky * 0.35, fx + sw * 0.8, fy + 4, fx, fy + 6)
            tongue.cubicTo(fx - sw * 0.8, fy + 4, fx - sw, fy - ky * 0.35,
                           fx + math.sin(self.phase * 2 + k) * 2.5, fy - ky * pulse)
            p.setBrush(color)
            p.drawPath(tongue)

        # 火星
        for i in range(7):
            t = (self.phase * 0.5 + i * 0.14) % 1.0
            p.setBrush(QColor(255, 190 + int(40 * (1 - t)), 90, int(180 * (1 - t))))
            p.drawEllipse(QPointF(fx - 14 + math.sin(t * 7 + i) * 26,
                                  fy - 30 - 60 * t), 1.6 + 1.2 * (1 - t), 1.6 + 1.2 * (1 - t))

        # 烟雾柱
        for i in range(11):
            t = (self.phase * 0.16 + i * 0.09) % 1.0
            alpha = int(120 * (1 - t) * (0.4 + 0.6 * min(1, t * 3)))
            p.setBrush(QColor(196, 199, 196, alpha) if not thermal else QColor(120, 90, 130, alpha))
            px = fx - 18 + math.sin(t * 4.2 + i) * (10 + 30 * t) - t * 26
            py = fy - 46 - (h * 0.68) * t
            rr = 12 + 30 * t
            p.drawEllipse(QPointF(px, py), rr, rr * 0.85)

        # 检测框
        if self.show_boxes:
            self._box(p, QRectF(w * 0.55, h * 0.55, w * 0.30, h * 0.40),
                      "明火 fire", f"{self._score(0):.1f}%", theme.RED)
            self._box(p, QRectF(w * 0.56, h * 0.06, w * 0.38, h * 0.44),
                      "烟雾 smoke", f"{self._score(1):.1f}%", theme.AMBER)
            self._box(p, QRectF(w * 0.04, h * 0.62, w * 0.24, h * 0.30),
                      "正常 normal", f"{self._score(2):.1f}%", theme.ACCENT)

        # 扫描线
        y = h * ((self.phase * 0.5) % 1.0)
        p.setPen(QPen(QColor(255, 255, 255, 55), 1))
        p.drawLine(QPointF(0, y), QPointF(w, y))
        p.restore()

        # 角标
        p.setFont(_font(9.5, 700))
        p.setPen(C("#FFFFFF"))
        p.setBrush(QColor(20, 37, 28, 155))
        p.drawRoundedRect(QRectF(10, 9, 148, 21), 6, 6)
        p.drawText(QRectF(18, 9, 138, 21), Qt.AlignmentFlag.AlignVCenter,
                   f"UAV-02 · {'热成像' if thermal else '可见光'}")
        p.setBrush(QColor(20, 37, 28, 130))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(w - 20, 19), 4.5, 4.5)
        p.setBrush(C(theme.RED))
        p.drawEllipse(QPointF(w - 20, 19), 2.6, 2.6)

        p.setFont(_font(8.5, 600))
        p.setPen(C("#FFFFFF"))
        p.setBrush(QColor(20, 37, 28, 120))
        p.drawRoundedRect(QRectF(w - 108, h - 26, 98, 18), 6, 6)
        p.drawText(QRectF(w - 104, h - 26, 90, 18), Qt.AlignmentFlag.AlignVCenter,
                   datetime_now())
        p.end()

    def _score(self, idx: int) -> float:
        if self.engine:
            return self.engine.vision_scores()[idx]
        return (96.2, 88.4, 3.6)[idx]

    def _box(self, p: QPainter, rect: QRectF, title: str, conf: str, color: str):
        c = C(color)
        p.setPen(QPen(c, 1.6))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(rect)
        arm = min(14, rect.width() * 0.2)
        pen = QPen(c, 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        for corner in (rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight()):
            dx = arm if corner.x() == rect.left() else -arm
            dy = arm if corner.y() == rect.top() else -arm
            p.drawLine(corner, QPointF(corner.x() + dx, corner.y()))
            p.drawLine(corner, QPointF(corner.x(), corner.y() + dy))

        p.setFont(_font(8.5, 700))
        text = f"{title}  {conf}"
        tw = p.fontMetrics().horizontalAdvance(text) + 12
        box = QRectF(rect.left(), rect.top() - 17, tw, 15)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        p.drawRoundedRect(box, 3, 3)
        p.setPen(C("#FFFFFF"))
        p.drawText(box, Qt.AlignmentFlag.AlignCenter, text)


# ---------------------------------------------------------------------------
class LinkDiagram(QWidget):
    """空中—地面联动闭环示意。"""

    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.phase = 0.0
        self.setMinimumHeight(210)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self):
        if theme.ANIMATIONS and self.isVisible():
            self.phase += 0.05
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(C(theme.SURFACE_ALT))
        p.drawRoundedRect(QRectF(r).adjusted(0, 0, -1, -1), 14, 14)

        uav = QPointF(r.width() / 2, 48)
        ugv_pts = [QPointF(r.width() * (0.16 + i * 0.34), r.height() - 62) for i in range(3)]

        # 数据链（UAV -> UGV）
        for i, dst in enumerate(ugv_pts):
            path = QPainterPath(uav)
            cy = (uav.y() + dst.y()) / 2
            path.cubicTo(QPointF(uav.x(), cy), QPointF(dst.x(), cy), dst)
            pen = QPen(QColor(47, 125, 246, 90), 1.6)
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setDashPattern([5, 4])
            pen.setDashOffset(-self.phase * 8)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)

            t = (self.phase * 0.55 + i * 0.3) % 1.0
            pt = path.pointAtPercent(t)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(47, 125, 246, 180))
            p.drawEllipse(pt, 3.2, 3.2)

        # UAV 节点
        p.setBrush(C("#FFFFFF"))
        p.setPen(QPen(QColor(47, 125, 246, 90), 1.4))
        p.drawEllipse(uav, 27, 27)
        p.drawPixmap(QPointF(uav.x() - 13, uav.y() - 13), icons.pixmap("drone", theme.BLUE, 26))
        p.setFont(_font(9, 700))
        tw = p.fontMetrics().horizontalAdvance("UAV 侦察定位 · 火源坐标回传") + 18
        box = QRectF(uav.x() - tw / 2, uav.y() + 30, tw, 18)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 225))
        p.drawRoundedRect(box, 9, 9)
        p.setPen(C(theme.TEXT_SOFT))
        p.drawText(box, Qt.AlignmentFlag.AlignCenter, "UAV 侦察定位 · 火源坐标回传")

        # UGV 节点
        names = ["UGV-01", "UGV-02", "UGV-03"]
        for i, (pos, name) in enumerate(zip(ugv_pts, names)):
            p.setBrush(C("#FFFFFF"))
            p.setPen(QPen(QColor(18, 166, 106, 90), 1.4))
            p.drawEllipse(pos, 24, 24)
            p.drawPixmap(QPointF(pos.x() - 11, pos.y() - 11), icons.pixmap("robot", theme.ACCENT, 22))
            p.setFont(_font(8.5, 700))
            p.setPen(C(theme.TEXT_SOFT))
            p.drawText(QRectF(pos.x() - 45, pos.y() + 26, 90, 13),
                       Qt.AlignmentFlag.AlignCenter, name)

        # 覆盖标注（右上角，避免遮挡节点）
        p.setFont(_font(8.5, 600))
        p.setPen(C(theme.ACCENT_DARK))
        text = f"灭火阵列覆盖 {self.engine.coverage:.1f} ha"
        tw = p.fontMetrics().horizontalAdvance(text) + 16
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(C(theme.ACCENT_SOFT))
        p.drawRoundedRect(QRectF(r.width() - tw - 12, 12, tw, 20), 10, 10)
        p.setPen(C(theme.ACCENT_DARK))
        p.drawText(QRectF(r.width() - tw - 12, 12, tw, 20),
                   Qt.AlignmentFlag.AlignCenter, text)
        p.end()


# ---------------------------------------------------------------------------
class FormationView(QWidget):
    """地面机器人灭火阵列（编队推进）。"""

    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.phase = 0.0
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self):
        if theme.ANIMATIONS and self.isVisible():
            self.phase += 0.035
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(C(theme.SURFACE_ALT))
        p.drawRoundedRect(r.adjusted(0, 0, -1, -1), 14, 14)

        # 火线
        fire_y = 54 + math.sin(self.phase) * 3
        path = QPainterPath(QPointF(10, fire_y))
        path.cubicTo(r.width() * 0.3, fire_y - 18, r.width() * 0.6, fire_y + 16,
                     r.width() - 10, fire_y - 4)
        grad = QLinearGradient(0, fire_y - 24, 0, fire_y + 24)
        grad.setColorAt(0, QColor(255, 190, 90, 200))
        grad.setColorAt(0.5, QColor(239, 110, 60, 220))
        grad.setColorAt(1, QColor(200, 60, 50, 0))
        pen = QPen(QBrush(grad), 11)
        p.setPen(pen)
        p.drawPath(path)

        # 火舌
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(11):
            t = i / 10
            pt = path.pointAtPercent(t)
            fh = 9 + 4 * math.sin(self.phase * 2.6 + i * 1.3)
            flame = QPainterPath(QPointF(pt.x(), pt.y() - 4 - fh))
            flame.cubicTo(pt.x() + 5, pt.y() - fh * 0.4, pt.x() + 3.4, pt.y() + 1,
                          pt.x(), pt.y() + 2)
            flame.cubicTo(pt.x() - 3.4, pt.y() + 1, pt.x() - 5, pt.y() - fh * 0.4,
                          pt.x(), pt.y() - 4 - fh)
            p.setBrush(QColor(255, 196, 96, 200))
            p.drawPath(flame)

        p.setPen(Qt.PenStyle.NoPen)
        for i in range(6):
            t = ((self.phase * 0.45) + i * 0.16) % 1.0
            pt = path.pointAtPercent(t)
            p.setBrush(QColor(198, 206, 200, int(70 * (1 - t))))
            p.drawEllipse(QPointF(pt.x() + math.sin(t * 6 + i) * 12, pt.y() - 16 - 34 * t),
                          7 + 11 * t, 7 + 11 * t)

        # 机器人阵列
        formation = self.engine.formation
        n = 5
        base_y = r.height() - 56 + math.sin(self.phase * 1.6) * 2
        for i in range(n):
            k = i / (n - 1) - 0.5
            if formation.startswith("楔形"):
                x = r.width() / 2 + k * r.width() * 0.62
                y = base_y - (0.5 - abs(k)) * 34
            elif formation.startswith("弧形"):
                x = r.width() / 2 + k * r.width() * 0.66
                y = base_y - (1 - abs(k) * 1.6) * 18
            else:
                x = r.width() / 2 + k * r.width() * 0.66
                y = base_y
            p.setBrush(QColor(18, 166, 106, 26))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(x, y), 34, 22)
            p.setBrush(C("#FFFFFF"))
            p.setPen(QPen(QColor(18, 166, 106, 120), 1.2))
            p.drawEllipse(QPointF(x, y), 14, 14)
            p.drawPixmap(QPointF(x - 7, y - 7), icons.pixmap("robot", theme.ACCENT, 14))

        # 覆盖宽度
        p.setPen(QPen(QColor(18, 166, 106, 120), 1.2, Qt.PenStyle.DashLine))
        p.drawLine(QPointF(r.width() * 0.15, base_y + 27), QPointF(r.width() * 0.85, base_y + 27))
        p.setFont(_font(8.5, 600))
        p.setPen(C(theme.ACCENT_DARK))
        p.drawText(QRectF(r.width() * 0.15, base_y + 30, r.width() * 0.70, 14),
                   Qt.AlignmentFlag.AlignCenter, f"覆盖宽度 ≈ 120 m · {formation}")
        p.end()


# ---------------------------------------------------------------------------
class Waveform(QWidget):
    """语音输入波形。"""

    def __init__(self, parent=None, color: str = theme.ACCENT):
        super().__init__(parent)
        self.active = False
        self.phase = 0.0
        self._color = QColor(color)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._timer = QTimer(self)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self):
        if theme.ANIMATIONS and self.active and self.isVisible():
            self.phase += 0.28
            self.update()

    def set_active(self, active: bool):
        self.active = active
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        bars = max(12, w // 9)
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(bars):
            x = w * i / bars
            if self.active:
                amp = (0.25 + 0.75 * abs(math.sin(self.phase + i * 0.55)
                                        * math.cos(self.phase * 0.6 + i * 0.23)))
            else:
                amp = 0.30 + 0.16 * abs(math.sin(i * 0.9))
            bh = max(4.0, h * 0.80 * amp)
            c = QColor(self._color)
            c.setAlpha(230 if self.active else 90)
            p.setBrush(c)
            bw = max(2.5, w / bars - 2.5)
            p.drawRoundedRect(QRectF(x, (h - bh) / 2, bw, bh), bw / 2, bw / 2)
        p.end()


_ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_feed_cache: dict[str, QPixmap] = {}


def feed_pixmap(mode: str = "eo", fire_active: bool = True) -> QPixmap:
    """加载演示素材：按可见光/红外与火情状态选择，并缓存。"""
    key = ("feed_ir" if mode == "ir" else "feed_eo") + ("" if fire_active else "_clear")
    if key not in _feed_cache:
        pm = QPixmap(os.path.join(_ASSET_DIR, f"{key}.jpg"))
        _feed_cache[key] = pm
    return _feed_cache[key]


class VideoFeed(QWidget):
    """无人机视频演示画面：根据火情切换素材，并叠加模拟遥测。"""

    def __init__(self, engine: SimEngine | None = None, mode: str = "eo",
                 connected: bool = True, parent=None, show_boxes: bool = True):
        super().__init__(parent)
        self.engine = engine
        self.mode = mode
        self.connected = connected
        self.show_boxes = show_boxes
        self.phase = 0.0
        self.rec_seconds = 12 * 60 + 34
        self.setMinimumSize(320, 180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._timer = QTimer(self)
        self._timer.setInterval(80)
        self._timer.timeout.connect(self._tick)
        self._timer.start()
        if self.engine is not None:
            self.engine.tick.connect(self.update)

    def _has_active_fire(self) -> bool:
        return self.engine is not None and any(f.state != "extinguished" for f in self.engine.fires)

    # ------------------------------------------------------------------
    def _tick(self):
        if not self.isVisible() or not theme.ANIMATIONS:
            return
        self.phase += 0.06
        self.rec_seconds += 0.08
        self.update()

    def set_mode(self, mode: str):
        self.mode = mode
        self.update()

    def set_connected(self, connected: bool):
        self.connected = connected
        self.update()

    def set_thermal(self, on: bool):
        self.set_mode("ir" if on else "eo")

    def set_boxes(self, show: bool):
        self.show_boxes = show
        self.update()

    # ------------------------------------------------------------------
    def _cover_source(self, target_ratio: float, pm: QPixmap | None = None) -> QRectF:
        if pm is None:
            pm = feed_pixmap(self.mode, self._has_active_fire())
        if pm.isNull():
            return QRectF()
        sw, sh = pm.width(), pm.height()
        # 轻微摇镜 + 1.06 倍数字变焦
        zoom = 1.06
        cw, ch = sw / zoom, sh / zoom
        ratio = sw / sh
        if target_ratio > ratio:
            ch = cw / target_ratio
        else:
            cw = ch * target_ratio
        cx = sw / 2 + math.sin(self.phase * 0.21) * sw * 0.012
        cy = sh / 2 + math.cos(self.phase * 0.17) * sh * 0.010
        x = min(max(cx - cw / 2, 0), sw - cw)
        y = min(max(cy - ch / 2, 0), sh - ch)
        return QRectF(x, y, cw, ch)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        r = QRectF(self.rect())
        p.save()
        clip = QPainterPath()
        clip.addRoundedRect(r, 12, 12)
        p.setClipPath(clip)
        p.fillRect(r, QColor("#05080A"))

        if not self.connected:
            self._paint_offline(p, r)
            p.restore()
            p.end()
            return

        pm = feed_pixmap(self.mode, self._has_active_fire())
        src = self._cover_source(r.width() / max(1, r.height()), pm)
        p.drawPixmap(r, pm, src)

        # 动态噪点 + 扫描线 + 暗角
        rng = random.Random(int(self.phase * 7) % 97)
        p.setPen(Qt.PenStyle.NoPen)
        for _ in range(70):
            x = r.left() + rng.random() * r.width()
            y = r.top() + rng.random() * r.height()
            a = rng.randint(8, 26)
            p.setBrush(QColor(255, 255, 255, a) if rng.random() > 0.5 else QColor(0, 0, 0, a))
            p.drawRect(QRectF(x, y, 1.4, 1.4))
        p.setPen(QPen(QColor(0, 0, 0, 26), 1))
        y = r.top()
        while y < r.bottom():
            p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
            y += 3
        vignette = QRadialGradient(r.center(), r.width() * 0.72)
        vignette.setColorAt(0.55, QColor(0, 0, 0, 0))
        vignette.setColorAt(1, QColor(0, 0, 0, 120))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(vignette)
        p.drawRect(r)

        self._paint_hud(p, r)
        p.restore()
        p.end()

    # ------------------------------------------------------------------
    def _paint_offline(self, p: QPainter, r: QRectF):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#0B1014"))
        p.drawRect(r)
        p.setFont(_font(11, 600))
        msg = "视频信号中断 · 等待重连"
        tw = p.fontMetrics().horizontalAdvance(msg) + 34
        box = QRectF(r.center().x() - tw / 2, r.center().y() - 14, tw, 28)
        p.setBrush(QColor(229, 72, 77, 40))
        p.setPen(QPen(QColor(229, 72, 77, 120), 1))
        p.drawRoundedRect(box, 14, 14)
        p.setPen(QColor("#F09A9C"))
        p.drawText(box, Qt.AlignmentFlag.AlignCenter, msg)

    def _paint_hud(self, p: QPainter, r: QRectF):
        w, h = r.width(), r.height()
        pad = 12
        compact = w < 420 or h < 260

        # 取景角标
        p.setPen(QPen(QColor(255, 255, 255, 150), 1.4))
        arm = 16
        for cx, cy, dx, dy in ((pad, pad, 1, 1), (w - pad, pad, -1, 1),
                               (pad, h - pad, 1, -1), (w - pad, h - pad, -1, -1)):
            p.drawLine(QPointF(cx, cy), QPointF(cx + arm * dx, cy))
            p.drawLine(QPointF(cx, cy), QPointF(cx, cy + arm * dy))

        # 中心准星
        cx, cy = w / 2, h / 2
        p.setPen(QPen(QColor(255, 255, 255, 120), 1))
        p.drawLine(QPointF(cx - 14, cy), QPointF(cx - 4, cy))
        p.drawLine(QPointF(cx + 4, cy), QPointF(cx + 14, cy))
        p.drawLine(QPointF(cx, cy - 14), QPointF(cx, cy - 4))
        p.drawLine(QPointF(cx, cy + 4), QPointF(cx, cy + 14))

        # 左上：录制状态
        p.setFont(_font(9.5, 700))
        rec = "REC" if int(self.phase) % 2 == 0 else "REC"
        p.setPen(QColor("#FF5A5F"))
        p.drawText(QRectF(32, 16, 30, 14), Qt.AlignmentFlag.AlignVCenter, rec)
        p.setBrush(QColor("#FF5A5F"))
        p.setPen(Qt.PenStyle.NoPen)
        if int(self.phase * 1.5) % 2 == 0:
            p.drawEllipse(QPointF(68, 23), 3.2, 3.2)
        mm, ss = int(self.rec_seconds // 60), int(self.rec_seconds % 60)
        p.setPen(QColor(255, 255, 255, 210))
        p.setFont(_font(9, 600))
        p.drawText(QRectF(76, 16, 90, 14), Qt.AlignmentFlag.AlignVCenter,
                   f"00:{mm:02d}:{ss:02d}")
        if not compact:
            p.setPen(QColor(255, 255, 255, 190))
            p.drawText(QRectF(32, 32, 170, 14), Qt.AlignmentFlag.AlignVCenter,
                       f"UAV-03  ·  {'IR 640×512' if self.mode == 'ir' else 'EO 1080P'}")

        # 右上：信号强度
        bx, by = w - 26, 18
        if compact:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 255, 255, 200))
            for i in range(4):
                hh = 3 + i * 2
                p.drawRoundedRect(
                    QRectF(bx - 18 + i * 5, by + (8.5 - hh), 3, hh), 1, 1)
            bx = -999
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(4):
            hh = 3 + i * 2.4
            p.setBrush(QColor(255, 255, 255, 220 if i < 3 else 90))
            p.drawRoundedRect(QRectF(bx - 26 + i * 5, by + (9 - hh), 3, hh), 1, 1)
        if not compact:
            p.setPen(QColor(255, 255, 255, 210))
            p.setFont(_font(9, 600))
            p.drawText(QRectF(bx - 74, by + 12, 74, 14), Qt.AlignmentFlag.AlignRight,
                       "-52 dBm")
            p.setPen(QColor(255, 255, 255, 170))
            p.drawText(QRectF(bx - 96, by + 26, 96, 14), Qt.AlignmentFlag.AlignRight,
                       "4.2 Mbps · 42 ms")

        # 数字变焦
        if not compact:
            p.setPen(QColor(255, 255, 255, 200))
            p.setFont(_font(9, 700))
            p.drawText(QRectF(w - 96, h - 52, 70, 14), Qt.AlignmentFlag.AlignRight, "ZOOM ×1.0")

        # 目标框
        if self.show_boxes and self._has_active_fire():
            fire = (0.44, 0.46, 0.40, 0.34)
            smoke = (0.52, 0.15, 0.40, 0.28)
            p.setFont(_font(8.5, 700))
            for (rx, ry, rw_, rh), name, color, score in (
                    (fire, "明火 fire", theme.RED, 95.9),
                    (smoke, "烟雾 smoke", theme.AMBER, 86.0)):
                jitter = math.sin(self.phase * 0.9) * 1.2
                box = QRectF(w * rx + jitter, h * ry, w * rw_, h * rh)
                p.setPen(QPen(QColor(color), 1.4))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRect(box)
                tag = f"{name} {score:.1f}%"
                tw = p.fontMetrics().horizontalAdvance(tag) + 10
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QColor(color))
                p.drawRoundedRect(QRectF(box.left(), box.top() - 15, tw, 15), 3, 3)
                p.setPen(QColor("#FFFFFF"))
                p.drawText(QRectF(box.left() + 5, box.top() - 15, tw, 15),
                           Qt.AlignmentFlag.AlignVCenter, tag)

        # 底部遥测
        bar = QRectF(10, h - 32, w - 20, 22)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(8, 14, 18, 150))
        p.drawRoundedRect(bar, 6, 6)
        p.setFont(_font(9, 600))
        p.setPen(QColor(255, 255, 255, 225))
        alt = 92 if self.engine is None else 92
        spd = 4.3 if self.engine is None else 4.3
        bat = 51 if self.engine is None else 51
        if compact:
            p.drawText(bar.adjusted(8, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter,
                       f"ALT {alt}m  SPD {spd}  BAT {bat}%")
        else:
            p.drawText(bar.adjusted(10, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter,
                       f"ALT {alt} m    SPD {spd} m/s    HDG 041°    BAT {bat}%    GPS 12")
            p.drawText(bar.adjusted(0, 0, -10, 0),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                       "640×512 30FPS  H.265" if self.mode == "ir" else "1080P 30FPS  H.265")


class FirstPerson3DView(QWidget):
    """3D 游戏化第一人称视角（支持左右转向、前后移动、喷水灭火特效与红外切换）。"""

    def __init__(self, engine: SimEngine, robot=None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.robot = robot
        self.yaw = 0.0        # 弧度，左右视角
        self.pitch = 0.0      # 弧度，俯仰视角
        self.pos_z = 0.0      # 前后推进偏移
        self.spraying = False
        self.thermal = False
        self.connected = True
        self.phase = 0.0
        self._last_mouse = None
        self.setMinimumHeight(300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._timer = QTimer(self)
        self._timer.setInterval(45)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        # 预生成 3D 森林树木坐标 (x, z, height)
        rng = random.Random(42)
        self._trees = [
            (rng.uniform(-4.5, 4.5), rng.uniform(1.8, 11.0), rng.uniform(0.7, 1.5))
            for _ in range(42)
        ]

    def _tick(self):
        if self.isVisible():
            self.phase += 0.12
            self.update()

    def set_connected(self, connected: bool):
        self.connected = connected
        self.update()

    def set_mode(self, mode: str):
        self.thermal = (mode == "ir")
        self.update()

    def pan(self, dyaw: float = 0.0, dpitch: float = 0.0, dz: float = 0.0):
        self.yaw = (self.yaw + dyaw) % (2 * math.pi)
        self.pitch = max(-0.35, min(0.35, self.pitch + dpitch))
        self.pos_z = max(-3.0, min(4.5, self.pos_z + dz))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._last_mouse = event.position()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._last_mouse is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            delta = event.position() - self._last_mouse
            self._last_mouse = event.position()
            self.pan(dyaw=delta.x() * 0.008, dpitch=-delta.y() * 0.005)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._last_mouse = None
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        w, h = r.width(), r.height()
        clip = QPainterPath()
        clip.addRoundedRect(r, 12, 12)
        p.setClipPath(clip)

        if not self.connected:
            p.fillRect(r, C("#0E1418"))
            p.setPen(C("#7C8F87"))
            p.setFont(_font(14, 700))
            p.drawText(r, Qt.AlignmentFlag.AlignCenter, "3D 图传链路已断开 · 点击右上角重连")
            p.end()
            return

        horizon_y = h * (0.46 + self.pitch * 0.55)

        # 天空与地面
        sky = QLinearGradient(0, 0, 0, horizon_y)
        if self.thermal:
            sky.setColorAt(0, C("#121329"))
            sky.setColorAt(1, C("#341E38"))
        else:
            sky.setColorAt(0, C("#7EC8E3"))
            sky.setColorAt(1, C("#D8EFE6"))
        p.fillRect(QRectF(0, 0, w, horizon_y), sky)

        ground = QLinearGradient(0, horizon_y, 0, h)
        if self.thermal:
            ground.setColorAt(0, C("#23182D"))
            ground.setColorAt(1, C("#110D18"))
        else:
            ground.setColorAt(0, C("#3E6B48"))
            ground.setColorAt(1, C("#1E3A26"))
        p.fillRect(QRectF(0, horizon_y, w, h - horizon_y), ground)

        # 3D 透视地面网格线（随 yaw / pos_z 移动）
        p.setPen(QPen(QColor(255, 255, 255, 22 if not self.thermal else 30), 1))
        for i in range(1, 9):
            t = i / 9.0
            y = horizon_y + (h - horizon_y) * (t ** 1.7)
            p.drawLine(QPointF(0, y), QPointF(w, y))
        for gx in range(-6, 7):
            x_off = (gx - math.sin(self.yaw) * 2.5) * 90
            p.drawLine(QPointF(w * 0.5 + x_off * 0.15, horizon_y),
                       QPointF(w * 0.5 + x_off * 1.4, h))

        # 3D 投影函数
        def project(wx: float, wz: float):
            rx = wx * math.cos(self.yaw) - wz * math.sin(self.yaw)
            rz = wx * math.sin(self.yaw) + wz * math.cos(self.yaw) - self.pos_z
            if rz < 0.6:
                return None
            scale = 340.0 / rz
            sx = w * 0.5 + rx * scale
            sy = horizon_y + (1.1 * scale) * 0.35
            return sx, sy, scale, rz

        # 绘制 3D 树木（按远近排序）
        items = []
        for tx, tz, th in self._trees:
            proj = project(tx, tz)
            if proj:
                items.append((proj[3], "tree", proj, th))

        # 火点 3D 位置（正前方 5.2m）
        f_proj = project(0.0, 5.2)
        if f_proj:
            items.append((f_proj[3], "fire", f_proj, 1.0))

        items.sort(key=lambda x: x[0], reverse=True)
        for _rz, kind, (sx, sy, sc, _), extra in items:
            if kind == "tree":
                tw = max(4.0, sc * 0.22)
                th_px = max(12.0, sc * 0.65 * extra)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(C("#2C1E16") if not self.thermal else C("#3B2840"))
                p.drawRect(QRectF(sx - tw * 0.14, sy - th_px * 0.25, tw * 0.28, th_px * 0.25))
                p.setBrush(C("#245937") if not self.thermal else C("#4A3052"))
                tri = QPainterPath(QPointF(sx, sy - th_px))
                tri.lineTo(sx - tw * 0.6, sy - th_px * 0.22)
                tri.lineTo(sx + tw * 0.6, sy - th_px * 0.22)
                tri.closeSubpath()
                p.drawPath(tri)
            elif kind == "fire":
                f = self.engine.fire
                if f.state != "extinguished" and f.intensity > 0.1:
                    f_scale = 0.5 + 0.7 * (f.intensity / 100.0)
                    rad = max(18.0, sc * 0.48 * f_scale)
                    glow = QRadialGradient(QPointF(sx, sy - rad * 0.4), rad * 1.4)
                    glow.setColorAt(0.0, QColor(255, 240, 140, 235))
                    glow.setColorAt(0.45, QColor(255, 110, 40, 185))
                    glow.setColorAt(1.0, QColor(255, 60, 20, 0))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.setBrush(glow)
                    p.drawEllipse(QPointF(sx, sy - rad * 0.4), rad * 1.4, rad * 1.1)
                    # 3D 跳动火舌
                    for k in range(3):
                        fl = rad * (0.75 + 0.2 * math.sin(self.phase * 2.1 + k))
                        p.setBrush(QColor(255, 160 - k * 30, 40, 200))
                        p.drawEllipse(QPointF(sx + (k - 1) * rad * 0.22, sy - fl * 0.5),
                                      rad * 0.28, fl * 0.55)
                else:
                    p.setPen(QPen(C(theme.ACCENT), 2))
                    p.setBrush(QColor(18, 166, 106, 80))
                    p.drawEllipse(QPointF(sx, sy), 24, 10)
                    p.setPen(C("#FFFFFF"))
                    p.setFont(_font(11, 700))
                    p.drawText(QPointF(sx - 28, sy - 18), "火点已扑灭 ✓")

        # 第一人称喷水灭火水柱特效
        if self.spraying:
            p.setPen(QPen(QColor(56, 189, 248, 190), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(QPointF(w * 0.5, h), QPointF(w * 0.5, horizon_y + 12))
            p.setPen(Qt.PenStyle.NoPen)
            for k in range(8):
                t = (self.phase * 1.8 + k * 0.125) % 1.0
                py = h - (h - (horizon_y + 12)) * t
                px = w * 0.5 + math.sin(t * 10 + k) * 8 * t
                p.setBrush(QColor(186, 230, 253, int(220 * (1 - t * 0.4))))
                p.drawEllipse(QPointF(px, py), 4.5, 4.5)

        # HUD 准星与航向角
        cx, cy = w * 0.5, h * 0.5
        p.setPen(QPen(QColor(255, 255, 255, 160), 1.4))
        p.drawLine(QPointF(cx - 14, cy), QPointF(cx - 5, cy))
        p.drawLine(QPointF(cx + 5, cy), QPointF(cx + 14, cy))
        p.drawLine(QPointF(cx, cy - 14), QPointF(cx, cy - 5))
        p.drawLine(QPointF(cx, cy + 5), QPointF(cx, cy + 14))

        deg = int(math.degrees(self.yaw)) % 360
        bar = QRectF(10, h - 32, w - 20, 22)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(8, 14, 18, 165))
        p.drawRoundedRect(bar, 6, 6)
        p.setFont(_font(9.5, 600))
        p.setPen(QColor(255, 255, 255, 230))
        p.drawText(bar.adjusted(10, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter,
                   f"3D 第一人称视角 · 航向 {deg:03d}° · 火势 {self.engine.fire.intensity:.0f}% · 鼠标拖拽/ADJL左右转")
        p.end()
