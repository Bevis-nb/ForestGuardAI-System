"""指挥总览页。"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from .. import icons, theme
from ..canvas import VideoFeed, TerrainMap
from ..simulation import SimEngine
from ..widgets import (
    Card,
    IconTile,
    Pill,
    ProgressLine,
    RingGauge,
    StatCard,
    button,
    label,
    toast,
)
from .base import EventList, Panel, ScrollPage, alert_row, kv_chip, robot_row


class OverviewPage(ScrollPage):
    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(
            engine,
            "指挥总览",
            "智护森林 ForestGuard AI · 林区火情态势与多机协同实时监控",
            padding=(20, 14, 10, 12),
        )
        self.fire_pill = Pill("扑救进行中", "warning")
        self.add_action(self.fire_pill)
        self.speed_btn = button("1× 倍速", "ghost", "clock", height=34, on_click=self._cycle_speed)
        self.add_action(self.speed_btn)
        self.add_action(button("调度确认", "primary", "sparkles", height=34,
                               on_click=self._open_dispatch_dialog))

        self._build_stats()
        self._build_middle()
        self._build_bottom()
        self.root.addStretch(1)

        self._refresh_alerts()
        engine.tick.connect(self._refresh)
        engine.event_added.connect(self._on_event_added)
        engine.alert_added.connect(self._on_alert_added)
        if hasattr(engine, "recon_confirmed"):
            engine.recon_confirmed.connect(self._on_recon_confirmed)
        if hasattr(engine, "fire_appeared"):
            engine.fire_appeared.connect(self._on_fire_appeared)
        self._refresh()

    # ------------------------------------------------------------------
    def _build_stats(self):
        row = QHBoxLayout()
        row.setSpacing(14)
        self.stat_fire = StatCard("过火面积", "12.8", "ha", "flame", theme.RED,
                                  theme.RED_SOFT, "2.4%", "up", [3, 5, 4, 6, 8, 7, 9])
        self.stat_uav = StatCard("在线航空器", "6 / 8", "架", "drone", theme.BLUE,
                                 theme.BLUE_SOFT, "正常", "flat", [5, 6, 6, 5, 6, 6, 6])
        self.stat_risk = StatCard("火险指数", "82", "极高", "alert", theme.AMBER,
                                  theme.AMBER_SOFT, "6.2%", "up", [58, 62, 66, 70, 74, 78, 82])
        self.stat_resp = StatCard("平均响应", "42", "s", "clock", theme.ACCENT,
                                  theme.ACCENT_SOFT, "18%", "down", [60, 56, 54, 50, 48, 44, 42])
        for card in (self.stat_fire, self.stat_uav, self.stat_risk, self.stat_resp):
            card.setFixedHeight(84)
            row.addWidget(card, 1)
        self.root.addLayout(row)

    def _build_middle(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        # 地图
        map_panel = Panel("林区实时态势", "多源融合 · 热成像火点已标定", "map")
        map_panel.add_action(kv_chip("wind", self.engine.wind_label(), theme.BLUE, theme.BLUE_SOFT))
        map_panel.add_action(kv_chip("thermo", f"{self.engine.temperature:.1f}℃", theme.AMBER, theme.AMBER_SOFT))
        self.map = TerrainMap(self.engine, "overview")
        self.map.setMinimumHeight(180)
        map_panel.add(self.map, 1)
        foot = QHBoxLayout()
        foot.setSpacing(8)
        self.fire_chip = kv_chip("target", "暂无活跃火点")
        self.fleet_chip = kv_chip("users", "装备在线")
        foot.addWidget(self.fire_chip)
        foot.addWidget(self.fleet_chip)
        foot.addStretch(1)
        self.map_status = label("● 链路稳定", None, color=theme.ACCENT, size=11, weight=700)
        foot.addWidget(self.map_status)
        map_panel.addLayout(foot)
        row.addWidget(map_panel, 3)

        # 右侧：风险 + 告警
        right = QVBoxLayout()
        right.setSpacing(14)

        risk_panel = Panel("火险综合研判", "多因子加权 · 每 60 秒刷新", "shield")
        risk_panel.add_action(Pill("极高风险", "critical"))
        self.contain_pill = Pill("控制率 18.4%", "success")
        inner = QHBoxLayout()
        inner.setSpacing(10)
        self.gauge = RingGauge(self.engine.risk, 100, "", "火险指数", theme.RED, 112, 10)
        self.gauge.setFixedSize(112, 112)
        inner.addWidget(self.gauge, 0, Qt.AlignmentFlag.AlignLeft)
        bars = QVBoxLayout()
        bars.setSpacing(9)
        self.bar_temp = ProgressLine("地表温度", 62, theme.AMBER)
        self.bar_hum = ProgressLine("空气湿度（反向）", 69, theme.BLUE)
        self.bar_wind = ProgressLine("风场影响", 58, theme.RED)
        for b in (self.bar_temp, self.bar_hum, self.bar_wind):
            bars.addWidget(b)
        bars.addStretch(1)
        inner.addLayout(bars, 1)
        risk_panel.addLayout(inner)
        risk_panel.add(self.contain_pill)
        right.addWidget(risk_panel)

        events_panel = Panel("协同事件流", "分布式协商 · 实时", "activity")
        events_panel.add_action(Pill("9 台在线", "success"))
        self.events = EventList(self.engine.events, limit=3, show_time=True)
        events_panel.add(self.events)
        events_panel.content.addStretch(1)
        right.addWidget(events_panel, 1)
        row.addLayout(right, 2)
        self.root.addLayout(row)

    def _build_bottom(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        detect = Panel("AI 火情识别", "深度学习目标检测 · YOLO-Fire v3", "camera")
        detect.add_action(Pill("在线推理", "success"))
        body = QHBoxLayout()
        body.setSpacing(12)
        self.cam = VideoFeed(self.engine)
        self.cam.setMinimumWidth(250)
        self.cam.setMinimumHeight(112)
        body.addWidget(self.cam, 1)
        scores = QVBoxLayout()
        scores.setSpacing(8)
        self.fire_bar = ProgressLine("明火 confidence", 96.2, theme.RED)
        self.smoke_bar = ProgressLine("烟雾 confidence", 88.4, theme.AMBER)
        self.normal_bar = ProgressLine("正常环境 confidence", 3.6, theme.ACCENT)
        scores.addWidget(self.fire_bar)
        scores.addWidget(self.smoke_bar)
        scores.addWidget(self.normal_bar)
        scores.addStretch(1)
        scores.addWidget(label("24 FPS · 38 ms", "caption"))
        body.addLayout(scores, 1)
        detect.addLayout(body)
        row.addWidget(detect, 3)

        fleet = Panel("装备状态", "空地协同编队 · 8 台", "robot")
        fleet.add_action(button("装备管理", "ghost", height=26, size=11,
                                on_click=self._go_fleet))
        self.fleet_rows = QVBoxLayout()
        self.fleet_rows.setSpacing(0)
        fleet.addLayout(self.fleet_rows)
        row.addWidget(fleet, 2)
        self._refresh_robot_rows()

        self.alerts_panel = Panel("实时告警", "自动推送 · 按等级排序", "bell")
        self.alerts_panel.add_action(button("全部", "ghost", height=26, size=11,
                                            on_click=self._go_alerts))
        self.alert_list = QVBoxLayout()
        self.alert_list.setSpacing(0)
        self.alerts_panel.addLayout(self.alert_list)
        row.addWidget(self.alerts_panel, 2)
        self.root.addLayout(row)

    # ------------------------------------------------------------------
    def _on_event_added(self, _ev=None):
        self.events.set_events(self.engine.events)

    def _on_alert_added(self, ev=None):
        self._refresh_alerts()
        if ev and self.isVisible():
            lv = ev.get("level", "info")
            if lv in ("critical", "success"):
                toast(self, f"{ev.get('title', '')} · {ev.get('detail', '')}",
                      "error" if lv == "critical" else "success")

    def _refresh_alerts(self):
        while self.alert_list.count():
            item = self.alert_list.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for alert in self.engine.alerts[:2]:
            self.alert_list.addWidget(alert_row(alert, compact=True))
            line = hline_row()
            self.alert_list.addWidget(line)

    def _refresh_robot_rows(self):
        while self.fleet_rows.count():
            item = self.fleet_rows.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for robot in self.engine.robots[:3]:
            self.fleet_rows.addWidget(robot_row(robot, compact=True))
        rest = len(self.engine.robots) - 3
        if rest > 0:
            self.fleet_rows.addWidget(
                label(f"其余 {rest} 台在线 · 见装备管理", "caption", color=theme.MUTED))

    def _refresh(self):
        e = self.engine
        active_fires = [f for f in e.fires if f.state != "extinguished"]
        self.fire_chip.set_text(f"活跃火点 {len(active_fires)} 处" if active_fires else "暂无活跃火点")
        self.fleet_chip.set_text(f"{sum(r.status != 'offline' for r in e.robots)} 台装备在线 · 空地协同")
        self.stat_fire.set_value(f"{e.fire_area:.1f}")
        self.stat_risk.set_value(f"{e.risk:.0f}")
        self.gauge.set_target(e.risk, theme.RED if e.risk >= 80 else theme.AMBER)
        self.bar_temp.set_value(min(100, e.temperature / 40 * 100))
        self.bar_hum.set_value(min(100, (100 - e.humidity) * 1.1))
        self.bar_wind.set_value(min(100, e.wind_speed / 10 * 100))
        self.contain_pill.set_text(f"控制率 {e.containment:.1f}%")
        st_map = {
            "suspicious": ("预警勘察中", "warning"),
            "spreading": ("火势蔓延", "critical"),
            "suppressing": ("扑救压制中", "warning"),
            "contained": ("火势已控", "info"),
            "extinguished": ("无火情" if not active_fires else "已扑灭 ✓", "success"),
        }
        st_txt, st_kind = st_map.get(e.fire.state, ("监控中", "info"))
        self.fire_pill.set_text(f"{e.fire.id} {st_txt}" if active_fires else "无火情")
        self.fire_pill.set_kind(st_kind)
        fire, smoke, normal = e.vision_scores()
        self.fire_bar.set_value(fire)
        self.smoke_bar.set_value(smoke)
        self.normal_bar.set_value(normal)
        self.events.set_events(e.events)
        self._refresh_robot_rows()

    # ------------------------------------------------------------------
    def _trigger_suspicious(self):
        f = self.engine.trigger_suspicious_fire()
        self.map.highlight_fire()
        toast(self, f"预警：发现可疑火点 {f.id}，已派无人机前往勘察", "warning")

    def _on_fire_appeared(self, _fire=None):
        self.map.highlight_fire()
        if self.isVisible():
            self._open_dispatch_dialog()

    def _on_recon_confirmed(self, _fire=None):
        if self.isVisible():
            self._open_dispatch_dialog()

    def _open_dispatch_dialog(self):
        from PySide6.QtWidgets import QCheckBox, QDialog
        plan = self.engine.recommend_dispatch()
        dlg = QDialog(self)
        dlg.setWindowTitle(f"设备调度推荐与人工确认 · 火点 {self.engine.fire.id}")
        dlg.setMinimumWidth(520)
        lay = QVBoxLayout(dlg)
        lay.setSpacing(10)
        lay.addWidget(label(
            f"火点 {self.engine.fire.id}（强度 {self.engine.fire.intensity:.0f}% · 面积 {self.engine.fire.area:.1f} ha）",
            None, size=14, weight=700,
        ))
        lay.addWidget(label(
            "算法评判标准：能力匹配 40% + 距火点距离 25% + 剩余电量 20% + 载荷/水量 15%",
            "caption", color=theme.MUTED,
        ))
        checks: list[tuple[str, QCheckBox]] = []
        for p in plan:
            cb = QCheckBox(f"[{p['robot_id']}] {p['task']}  —  {p['reason']}")
            cb.setChecked(True)
            lay.addWidget(cb)
            checks.append((p["robot_id"], cb))
        btns = QHBoxLayout()
        btns.addStretch(1)
        btns.addWidget(button("取消", "ghost", height=32, on_click=dlg.reject))
        btns.addWidget(button("确认并下发扑救", "primary", "sparkles", height=32, on_click=dlg.accept))
        lay.addLayout(btns)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            chosen = [rid for rid, cb in checks if cb.isChecked()]
            self.engine.confirm_dispatch(chosen)
            toast(self, f"已按人工确认方案下发 {len(chosen)} 台装备前往扑救", "success")

    def _cycle_speed(self):
        nxt = {1: 2, 2: 4, 4: 1}.get(self.engine.sim_speed, 1)
        self.engine.sim_speed = nxt
        self.speed_btn.setText(f"{nxt}× 倍速")
        toast(self, f"仿真推演速度已切换为 {nxt}×", "info")

    def _go_alerts(self):
        window = self.window()
        if hasattr(window, "navigate_to"):
            window.navigate_to("interaction")

    def _go_fleet(self):
        window = self.window()
        if hasattr(window, "navigate_to"):
            window.navigate_to("fleet")


def hline_row():
    from PySide6.QtWidgets import QFrame

    line = QFrame()
    line.setObjectName("Divider")
    line.setFixedHeight(1)
    return line
