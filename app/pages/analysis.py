"""火情分析与决策页（对应系统设计 2.3）。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QSlider, QVBoxLayout, QWidget

from .. import icons, theme
from ..canvas import TerrainMap, VideoFeed
from ..simulation import SimEngine
from ..widgets import (
    KeyValueRow,
    Pill,
    ProgressLine,
    ToggleSwitch,
    button,
    label,
    toast,
    soft_bg,
)
from .base import Panel, ScrollPage, hline, kv_chip


class AnalysisPage(ScrollPage):
    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(
            engine,
            "火情分析与决策",
            "深度学习火情识别 · 贝叶斯火势推演 · 自动生成灭火策略",
        )
        self.add_action(Pill("多模态推理在线", "success"))
        self.add_action(button("导出研判报告", "soft", "download", height=34, on_click=self._export))
        # 处置方案随火点态势自动生成

        body = QHBoxLayout()
        body.setSpacing(14)

        # ---------------- 1. 视觉识别 ----------------
        vision = Panel("AI 火情识别", "YOLO-Fire v3 · 明火 / 烟雾 / 正常环境", "camera")
        self.vision_pill = Pill("推理中", "success")
        vision.add_action(self.vision_pill)
        self.cam = VideoFeed(engine)
        self.cam.setMinimumHeight(210)
        vision.add(self.cam, 1)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(8)
        self.thermal = ToggleSwitch(False)
        self.thermal.toggled.connect(lambda v: (self.cam.set_thermal(v),
                                                toast(self, "已切换为热成像通道" if v else "已切换为可见光通道")))
        mode_row.addWidget(label("热成像", "caption"))
        mode_row.addWidget(self.thermal)
        mode_row.addStretch(1)
        mode_row.addWidget(label("24 FPS · 38 ms", "caption"))
        vision.addLayout(mode_row)

        self.fire_bar = ProgressLine("明火 confidence", 96, theme.RED)
        self.smoke_bar = ProgressLine("烟雾 confidence", 88, theme.AMBER)
        self.normal_bar = ProgressLine("正常环境 confidence", 4, theme.ACCENT)
        for b in (self.fire_bar, self.smoke_bar, self.normal_bar):
            vision.add(b)

        vision.addWidget(hline())
        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(4)
        for i, (k, v) in enumerate((("mAP@0.5", "0.921"), ("召回率", "0.94"),
                                    ("误检率", "2.1%"), ("模型版本", "v3.2"))):
            grid.addWidget(KeyValueRow(k, v), i // 2, i % 2)
        vision.addLayout(grid)
        body.addWidget(vision, 2)

        # ---------------- 2. 蔓延预测 ----------------
        spread = Panel("贝叶斯火势蔓延预测", "风场 / 坡度 / 湿度 / 植被为证据节点", "flame")
        spread.add_action(Pill("蔓延概率 0.83", "critical"))
        self.map = TerrainMap(engine, "analysis")
        self.map.setMinimumHeight(300)
        spread.add(self.map, 1)

        time_row = QHBoxLayout()
        time_row.setSpacing(8)
        time_row.addWidget(label("推演时刻", "caption"))
        self.time_label = label("T + 30 min", None, color=theme.ACCENT_DARK, size=12, weight=700)
        time_row.addWidget(self.time_label)
        time_row.addStretch(1)
        time_row.addWidget(label("T+30 / 60 / 90", "caption"))
        spread.addLayout(time_row)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 3)
        self.slider.setValue(1)
        self.slider.setPageStep(1)
        self.slider.valueChanged.connect(self._on_time)
        spread.addWidget(self.slider)

        metrics = QHBoxLayout()
        metrics.setSpacing(8)
        self.m_area = kv_chip("flame", "预测过火 21.4 ha", theme.RED, theme.RED_SOFT)
        self.m_speed = kv_chip("wind", "蔓延 3.2 m/min")
        self.m_dir = kv_chip("compass", "主方向 东北 42°")
        for w in (self.m_area, self.m_speed, self.m_dir):
            metrics.addWidget(w)
        spread.addLayout(metrics)

        spread.addWidget(hline())
        ev = QHBoxLayout()
        ev.setSpacing(6)
        ev.addWidget(label("证据", "caption"))
        for name, prob, color in (("风速", 0.68, theme.BLUE), ("坡度", 0.54, theme.AMBER),
                                  ("湿度", 0.41, theme.CYAN), ("植被", 0.77, theme.ACCENT)):
            chip = label(f"{name} {prob:.2f}", None, color=color, size=11, weight=700)
            chip.setStyleSheet(
                f"color:{color}; background:{theme.SURFACE_ALT}; border-radius:8px;"
                f" padding:4px 8px; font-size:11px; font-weight:700;"
            )
            ev.addWidget(chip)
        ev.addStretch(1)
        spread.addLayout(ev)
        body.addWidget(spread, 3)

        # ---------------- 3. 决策 ----------------
        decision = Panel("灭火策略生成", "基于风险等级与资源约束的最优处置", "shield")
        decision.add_action(Pill("待确认", "warning"))
        decision.addWidget(label("建议隔离带", "muted"))
        self.iso_text = label(
            "沿坐标 (0.62, 0.34) → (0.70, 0.46) → (0.76, 0.60)\n"
            "宽度 8 m，与主风向垂直，优先阻断东北蔓延", None,
            color=theme.TEXT_SOFT, size=11.5,
        )
        self.iso_text.setWordWrap(True)
        self.iso_text.setStyleSheet(
            f"color:{theme.TEXT_SOFT}; background:{theme.SURFACE_ALT}; border-radius:10px;"
            f" padding:9px 10px; font-size:11.5px;"
        )
        decision.addWidget(self.iso_text)

        decision.addWidget(label("灭火剂类型", "muted"))
        agent_row = QHBoxLayout()
        agent_row.setSpacing(6)
        for name, value, color, soft in (("水", "45%", theme.BLUE, theme.BLUE_SOFT),
                                         ("泡沫", "35%", theme.PURPLE, theme.PURPLE_SOFT),
                                         ("干粉", "20%", theme.AMBER, theme.AMBER_SOFT)):
            card = QWidget()
            soft_bg(card, soft, 10)
            lay = QVBoxLayout(card)
            lay.setContentsMargins(10, 7, 10, 7)
            lay.setSpacing(0)
            lay.addWidget(label(name, None, color=color, size=12, weight=700))
            lay.addWidget(label(value, None, color=color, size=14, weight=700))
            agent_row.addWidget(card, 1)
        decision.addLayout(agent_row)

        decision.addWidget(label("力量配置", "muted"))
        self.force_rows = QVBoxLayout()
        self.force_rows.setSpacing(7)
        decision.addLayout(self.force_rows)

        decision.addWidget(hline())
        decision.addWidget(label("处置时序", "muted"))
        self.steps = QVBoxLayout()
        self.steps.setSpacing(5)
        decision.addLayout(self.steps)
        self.apply_btn = button("确认并下发处置方案", "primary", "send", height=40,
                                on_click=self._confirm)
        decision.addWidget(self.apply_btn)
        body.addWidget(decision, 2)

        self.root.addLayout(body, 1)

        engine.tick.connect(self._refresh)
        self._on_time(1)
        self._build_force([("无人机侦察组", 2, 100, theme.BLUE),
                           ("地面扑打组", 3, 75, theme.ACCENT),
                           ("隔离带作业组", 2, 58, theme.AMBER)])
        self._build_steps(["0–5 min 无人机复核火线，更新蔓延概率",
                           "5–20 min 地面编队压制北侧火头",
                           "20–45 min 东侧开挖 8 m 隔离带",
                           "45–90 min 全线洒水降温，转入看守"])
        self._refresh()

    # ------------------------------------------------------------------
    def _build_force(self, items):
        while self.force_rows.count():
            item = self.force_rows.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for name, count, ratio, color in items:
            row = QWidget()
            lay = QHBoxLayout(row)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(8)
            lay.addWidget(label(name, "muted"))
            lay.addStretch(1)
            lay.addWidget(label(f"{count} 台", None, size=11.5, weight=700))
            lay.addWidget(label(f"{ratio}%", None, color=color, size=11.5, weight=700))
            self.force_rows.addWidget(row)

    def _build_steps(self, steps):
        while self.steps.count():
            item = self.steps.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for i, text in enumerate(steps):
            row = QWidget()
            lay = QHBoxLayout(row)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(8)
            num = label(str(i + 1), None, color=theme.ACCENT_DARK, size=10, weight=700)
            num.setFixedSize(18, 18)
            num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            num.setStyleSheet(
                f"background:{theme.ACCENT_SOFT}; color:{theme.ACCENT_DARK};"
                f" border-radius:9px; font-size:10px; font-weight:700;"
            )
            lay.addWidget(num, 0, Qt.AlignmentFlag.AlignTop)
            lb = label(text, "caption", color=theme.TEXT_SOFT)
            lb.setWordWrap(True)
            lay.addWidget(lb, 1)
            self.steps.addWidget(row)

    # ------------------------------------------------------------------
    def _on_time(self, value: int):
        minutes = value * 30
        self.time_label.setText(f"T + {minutes} min")
        self.map.set_minutes(max(1, minutes))
        area = 12.8 + minutes * 0.29
        speed = 1.6 + minutes * 0.035
        self.m_area.set_text(f"预测过火 {area:.1f} ha")
        self.m_speed.set_text(f"蔓延 {speed:.1f} m/min")
        self.m_dir.set_text(f"主方向 {['东北 42°', '东北 48°', '东北 55°', '北偏东 61°'][value]}")

    def _refresh(self):
        fire, smoke, normal = self.engine.vision_scores()
        self.fire_bar.set_value(fire)
        self.smoke_bar.set_value(smoke)
        self.normal_bar.set_value(normal)

    def _make_plan(self):
        self._build_force([("无人机侦察组", 3, 100, theme.BLUE),
                           ("地面扑打组", 4, 82, theme.ACCENT),
                           ("隔离带作业组", 1, 35, theme.AMBER)])
        self._build_steps(["立即派出 UAV-02/03 复核北侧火线",
                           "UGV-01/02 以楔形阵列压制主火头",
                           "UGV-03 沿 0.70→0.76 开挖隔离带",
                           "预留 1 台 UGV 作为机动增援"])
        self.iso_text.setText(
            "沿坐标 (0.66, 0.32) → (0.72, 0.44) → (0.78, 0.58)\n"
            "宽度 10 m，顺风侧加宽，重点阻断东北方向蔓延"
        )
        self.engine.push_event("AI 决策引擎生成新版处置方案：3 组力量 / 4 阶段时序", "success")
        toast(self, "已根据最新态势重新生成处置方案")

    def _confirm(self):
        self.apply_btn.setText("方案已下发")
        self.apply_btn.setEnabled(False)
        self.engine.push_event("指挥员确认处置方案，任务已下发至 8 台装备", "success")
        self.engine.push_alert("处置方案已下发", "3 组力量进入预定位置，10 分钟内完成展开", "info", "指挥终端")
        toast(self, "处置方案已下发，各编队开始执行")

    def _export(self):
        toast(self, "研判报告已生成：reports/fire_analysis_2026.pdf")
