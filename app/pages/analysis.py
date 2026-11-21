"""火点级火势推演和灭火策略（演示模型，不用于现场决策）。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QSlider, QVBoxLayout, QWidget

from .. import theme
from ..canvas import TerrainMap, VideoFeed
from ..simulation import SimEngine
from ..widgets import IconTile, Pill, ProgressLine, ToggleSwitch, label, soft_bg
from .base import Panel, ScrollPage, kv_chip


class AnalysisPage(ScrollPage):
    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(engine, "火情分析与决策", "选择火点，查看潜在燃烧区与建议隔离带 · 仿真推演仅供演示")
        self.selected_fire_id: str | None = None
        self.add_action(Pill("仿真推演", "info"))

        body = QHBoxLayout()
        body.setSpacing(14)

        vision = Panel("AI 火情识别", "可见光 / 热成像演示画面", "camera")
        self.cam = VideoFeed(engine)
        self.cam.setMinimumHeight(210)
        vision.add(self.cam, 1)
        mode = QHBoxLayout()
        mode.addWidget(label("热成像", "caption"))
        self.thermal = ToggleSwitch(False)
        self.thermal.toggled.connect(self.cam.set_thermal)
        mode.addWidget(self.thermal)
        mode.addStretch(1)
        vision.addLayout(mode)
        self.fire_bar = ProgressLine("明火 confidence", 96, theme.RED)
        self.smoke_bar = ProgressLine("烟雾 confidence", 88, theme.AMBER)
        self.normal_bar = ProgressLine("正常环境 confidence", 4, theme.ACCENT)
        for bar in (self.fire_bar, self.smoke_bar, self.normal_bar):
            vision.add(bar)
        vision.addWidget(label("识别分数与视频均为演示数据", "caption"))
        body.addWidget(vision, 2)

        spread = Panel("火势蔓延预测", "与林区实时态势使用同一底图 · 点击火点切换", "flame")
        self.selection_pill = Pill("无活跃火点", "info")
        spread.add_action(self.selection_pill)
        self.map = TerrainMap(engine, "analysis")
        self.map.set_robots_visible(False)
        self.map.select_fires = True
        self.map.fire_selected.connect(self._select_fire)
        self.map.setMinimumHeight(300)
        spread.add(self.map, 1)
        time_row = QHBoxLayout()
        time_row.addWidget(label("推演时刻", "caption"))
        self.time_label = label("", None, color=theme.ACCENT_DARK, size=12, weight=700)
        time_row.addWidget(self.time_label)
        time_row.addStretch(1)
        time_row.addWidget(label("0 / 30 / 60 / 90 分钟", "caption"))
        spread.addLayout(time_row)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 3)
        self.slider.setValue(1)
        self.slider.valueChanged.connect(self._on_time)
        spread.addWidget(self.slider)
        metrics = QHBoxLayout()
        self.m_area = kv_chip("flame", "潜在燃烧区 —", theme.RED, theme.RED_SOFT)
        self.m_dir = kv_chip("wind", "蔓延方向 —")
        metrics.addWidget(self.m_area)
        metrics.addWidget(self.m_dir)
        spread.addLayout(metrics)
        spread.addWidget(label("色块：潜在燃烧概率；虚线：建议隔离带。结果仅为简化模拟，非实战依据。", "caption"))
        body.addWidget(spread, 3)

        decision = Panel("灭火策略", "针对选中火点动态生成 · 仅供演示", "shield")
        self.strategy_pill = Pill("无火情", "info")
        decision.add_action(self.strategy_pill)

        # 以不同层级的卡片区分火情摘要、隔离带和行动建议。
        summary = QWidget()
        soft_bg(summary, theme.ACCENT_SOFT, 12)
        summary_lay = QHBoxLayout(summary)
        summary_lay.setContentsMargins(12, 12, 12, 12)
        summary_lay.setSpacing(10)
        summary_lay.addWidget(IconTile("flame", theme.RED, theme.RED_SOFT, 38, 19, 11),
                              0, Qt.AlignmentFlag.AlignTop)
        summary_col = QVBoxLayout()
        summary_col.setSpacing(4)
        summary_col.addWidget(label("当前分析火点", "caption", color=theme.ACCENT_DARK))
        self.fire_info = label("无火情", None, size=14, weight=700)
        self.fire_info.setWordWrap(True)
        summary_col.addWidget(self.fire_info)
        summary_lay.addLayout(summary_col, 1)
        decision.addWidget(summary)

        # 关键数值以独立小卡展示，避免在长段文字中寻找信息。
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(7)
        self.severity_value = label("—", None, size=17, weight=700, color=theme.RED)
        self.area_value = label("—", None, size=17, weight=700, color=theme.AMBER)
        self.containment_value = label("—", None, size=17, weight=700, color=theme.ACCENT_DARK)
        for title, value in (("火势强度", self.severity_value),
                             ("过火面积", self.area_value),
                             ("控制率", self.containment_value)):
            tile = QWidget()
            soft_bg(tile, theme.SURFACE_ALT, 10)
            tile_lay = QVBoxLayout(tile)
            tile_lay.setContentsMargins(9, 8, 9, 8)
            tile_lay.setSpacing(3)
            tile_lay.addWidget(label(title, "caption"))
            tile_lay.addWidget(value)
            metrics_row.addWidget(tile, 1)
        decision.addLayout(metrics_row)

        isolation = QWidget()
        soft_bg(isolation, theme.SURFACE_ALT, 12)
        iso_lay = QVBoxLayout(isolation)
        iso_lay.setContentsMargins(12, 11, 12, 12)
        iso_lay.setSpacing(8)
        iso_head = QHBoxLayout()
        iso_head.setSpacing(8)
        iso_head.addWidget(IconTile("route", theme.AMBER, theme.AMBER_SOFT, 30, 15, 9))
        iso_head.addWidget(label("建议隔离带", None, size=12.5, weight=700), 1)
        self.iso_direction = Pill("待分析", "info", dot=False)
        iso_head.addWidget(self.iso_direction)
        iso_lay.addLayout(iso_head)
        self.iso_text = label("暂无建议", None, color=theme.TEXT_SOFT, size=11.5)
        self.iso_text.setWordWrap(True)
        iso_lay.addWidget(self.iso_text)
        decision.addWidget(isolation)

        action = QWidget()
        soft_bg(action, theme.SURFACE_ALT, 12)
        action_lay = QVBoxLayout(action)
        action_lay.setContentsMargins(12, 11, 12, 12)
        action_lay.setSpacing(8)
        action_head = QHBoxLayout()
        action_head.setSpacing(8)
        action_head.addWidget(IconTile("shield", theme.BLUE, theme.BLUE_SOFT, 30, 15, 9))
        action_head.addWidget(label("处置建议", None, size=12.5, weight=700), 1)
        action_lay.addLayout(action_head)
        action_body = QHBoxLayout()
        action_body.setSpacing(8)
        number = label("01", None, color=theme.BLUE, size=11, weight=700)
        number.setAlignment(Qt.AlignmentFlag.AlignTop)
        action_body.addWidget(number)
        self.strategy_text = label("当前没有活跃火点，持续监测林区。", None, color=theme.TEXT_SOFT, size=11.5)
        self.strategy_text.setWordWrap(True)
        action_body.addWidget(self.strategy_text, 1)
        action_lay.addLayout(action_body)
        self.action_followup = label("", "caption", color=theme.MUTED)
        self.action_followup.setWordWrap(True)
        action_lay.addWidget(self.action_followup)
        decision.addWidget(action)

        force_head = QHBoxLayout()
        force_head.setSpacing(7)
        force_head.addWidget(IconTile("users", theme.ACCENT, theme.ACCENT_SOFT, 30, 15, 9))
        force_head.addWidget(label("投入力量", None, size=12, weight=700), 1)
        decision.addLayout(force_head)
        self.force_text = label("暂无已分配装备", "caption", color=theme.TEXT_SOFT)
        self.force_text.setWordWrap(True)
        decision.addWidget(self.force_text)
        decision.addStretch(1)
        body.addWidget(decision, 2)
        self.root.addLayout(body, 1)

        engine.tick.connect(self._refresh)
        engine.fire_appeared.connect(lambda _fire: self._refresh())
        engine.recon_confirmed.connect(lambda _fire: self._refresh())
        self._on_time(self.slider.value())

    def _select_fire(self, fire_id: str):
        if any(f.id == fire_id and f.state != "extinguished" for f in self.engine.fires):
            self.selected_fire_id = fire_id
            self._refresh()

    def _on_time(self, value: int):
        minutes = value * 30
        self.time_label.setText(f"T + {minutes} min")
        self.map.set_minutes(minutes)
        self._refresh()

    def _refresh(self):
        e = self.engine
        fire_score, smoke, normal = e.vision_scores()
        self.fire_bar.set_value(fire_score)
        self.smoke_bar.set_value(smoke)
        self.normal_bar.set_value(normal)
        active = sorted((f for f in e.fires if f.state != "extinguished"),
                        key=lambda f: f.ignited_at)
        fire = next((f for f in active if f.id == self.selected_fire_id), None)
        if fire is None:
            fire = active[0] if active else None
            self.selected_fire_id = fire.id if fire else None
        self.map.set_selected_fire(self.selected_fire_id)
        if fire is None:
            self.selection_pill.set_text("无活跃火点")
            self.strategy_pill.set_text("无火情")
            self.strategy_pill.set_kind("info")
            self.fire_info.setText("无火情")
            self.severity_value.setText("—")
            self.area_value.setText("—")
            self.containment_value.setText("—")
            self.action_followup.setText("持续监测 · 等待火情")
            self.iso_direction.set_text("待分析")
            self.iso_direction.set_kind("info")
            self.iso_text.setText("暂无建议")
            self.strategy_text.setText("当前没有活跃火点，持续监测林区。")
            self.force_text.setText("暂无已分配装备")
            self.m_area.set_text("潜在燃烧区 —")
            self.m_dir.set_text("蔓延方向 —")
            return

        prediction = e.spread_model.assess(fire, self.slider.value() * 30,
                                           e.wind_deg, e.wind_speed, e.humidity)
        a, b = prediction["line"]
        self.selection_pill.set_text(f"分析 {fire.id} · {len(active)} 个火点")
        self.strategy_pill.set_text("待勘察" if fire.state == "suspicious" else "模拟建议")
        self.strategy_pill.set_kind("warning")
        self.fire_info.setText(f"{fire.id} · 当前选中")
        self.severity_value.setText(f"{fire.intensity:.0f}%")
        self.area_value.setText(f"{fire.area:.1f} ha")
        self.containment_value.setText(f"{fire.containment:.0f}%")
        self.action_followup.setText(f"推演时刻 T+{self.slider.value() * 30} min · 随火情动态更新")
        self.iso_direction.set_text("下风向")
        self.iso_direction.set_kind("warning")
        self.iso_text.setText(f"下风向布设，建议宽 {prediction['width_m']} m\n"
                              f"({a[0]:.2f}, {a[1]:.2f}) → ({b[0]:.2f}, {b[1]:.2f})")
        if fire.state == "suspicious":
            advice = "优先派无人机核实热源，确认后再组织扑救；预先评估下风向隔离位置。"
        elif fire.intensity >= 70:
            advice = "高强度火点：优先压制火头，在下风向布设较宽隔离带，并预留增援力量。"
        elif fire.intensity >= 35:
            advice = "中等强度火点：空地协同压制火线，沿建议隔离带阻断蔓延。"
        else:
            advice = "低强度火点：重点清理余火并持续监测，防止复燃。"
        self.strategy_text.setText(advice)
        assigned = [r.id for r in e.robots if r.assigned_fire_id == fire.id]
        self.force_text.setText("已分配：" + "、".join(assigned) if assigned else "该火点暂无已分配装备")
        self.m_area.set_text(f"潜在燃烧区 {prediction['area']:.1f} ha")
        self.m_dir.set_text(f"蔓延方向 {e.wind_deg:.0f}°")
