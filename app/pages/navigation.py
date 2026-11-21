"""自主导航与路径规划页（对应系统设计 2.1）。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QComboBox,
    QHBoxLayout,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .. import icons, theme
from ..canvas import TerrainMap
from ..simulation import SimEngine
from ..widgets import (
    KeyValueRow,
    Pill,
    ProgressLine,
    ToggleSwitch,
    button,
    label,
    toast,
)
from .base import Panel, ScrollPage, hline, kv_chip


class NavPage(ScrollPage):
    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(
            engine,
            "自主导航与路径规划",
            "演示栅格规划 · 每台设备独立配置 · 所有地图和设备共用路线",
        )
        self._sliders: list[QSlider] = []
        self.slam_pill = self.add_action(Pill("SLAM 建图中 87%", "success"))
        self.add_action(button("重新建图", "soft", "refresh", height=34,
                               on_click=self._restart_slam))
        # 路径随选中装备与参数实时规划

        body = QHBoxLayout()
        body.setSpacing(14)

        # ---------------- 左：建图 + 避险 ----------------
        left = QVBoxLayout()
        left.setSpacing(12)

        map_panel = Panel("SLAM 高精度地图", "激光雷达 + 视觉融合 · 实时占据栅格", "radar")
        map_panel.add_action(kv_chip("cpu", "关键帧 1,284"))
        self.map = TerrainMap(engine, "navigation")
        self.map.setMinimumHeight(372)
        self.map.show_path = False
        self._selected_robot_id = None
        self.map.robot_selected.connect(self._on_robot_selected)
        map_panel.add(self.map, 1)
        self.robot_info_label = label("点击地图上的设备查看单体状态与规划路径", "caption", color=theme.TEXT_SOFT)
        map_panel.add(self.robot_info_label)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(9)
        ctrl.addWidget(label("图层", "muted"))
        # 已移除激光点云与代价地图图层开关
        ctrl.addStretch(1)
        self.nav_state = label("● 自主导航中 · 静态栅格避障", None,
                               color=theme.ACCENT, size=11.5, weight=700)
        ctrl.addWidget(self.nav_state)
        map_panel.addLayout(ctrl)

        map_panel.add(hline())
        tele = QHBoxLayout()
        tele.setSpacing(8)
        self.t_speed = kv_chip("activity", "速度 1.8 m/s")
        self.t_head = kv_chip("compass", "航向 042°")
        self.t_obs = kv_chip("alert", "最近障碍 1.6 m", theme.AMBER, theme.AMBER_SOFT)
        self.t_acc = kv_chip("target", "定位精度 ±0.08 m")
        for w in (self.t_speed, self.t_head, self.t_obs, self.t_acc):
            tele.addWidget(w)
        tele.addStretch(1)
        map_panel.addLayout(tele)
        left.addWidget(map_panel, 1)

        # 紧急避险条
        safe = Panel("自动紧急避险", "检测到高温或障碍物时自动调整路线 / 制动", "shield")
        safe.add_action(Pill("防护生效", "warning"))
        band = QHBoxLayout()
        band.setSpacing(10)
        band.addWidget(label("演示规则：机身温度超过 60℃ 或电量低于 30% 自动返航", "caption"))
        band.addStretch(1)
        self.estop_btn = button("紧急停止 E-STOP", "danger", "power", height=38, size=12.5,
                                on_click=self._estop)
        self.estop_btn.setMinimumWidth(190)
        band.addWidget(self.estop_btn)
        safe.addLayout(band)
        self.safe_log = label("路线不可达时停止移动，不会直线穿越障碍。", "caption")
        safe.addWidget(self.safe_log)
        left.addWidget(safe)
        body.addLayout(left, 3)

        # ---------------- 右：SLAM 与路径 ----------------
        right = QVBoxLayout()
        right.setSpacing(12)

        slam = Panel("建图状态（演示）", "静态模拟栅格，非真实 SLAM", "layers")
        slam.add_action(Pill("精度 0.08 m", "info"))
        for key, val in (("关键帧 / 回环", "1,284 帧 / 12 次"), ("累计里程", "3.42 km")):
            slam.addWidget(KeyValueRow(key, val))
        slam.addWidget(ProgressLine("建图进度", 87, theme.ACCENT))
        slam.addWidget(ProgressLine("点云覆盖率", 92, theme.BLUE))
        right.addWidget(slam)

        opt = Panel("设备路径规划", "设置仅作用于选中设备；任务、巡逻和返航共用", "route")
        self.robot_picker = QComboBox()
        for robot in engine.robots:
            self.robot_picker.addItem(f"{robot.id} · {robot.name}", robot.id)
        opt.addWidget(self.robot_picker)
        opt.addWidget(label("路径为仿真示意；终点不可达时设备停止", "caption"))

        self.lbl_wind = label("", "caption")
        opt.addWidget(self._slider_row("风向", self.lbl_wind, -180, 180,
                                       int(engine.wind_deg) - 180, self._on_param))
        self.lbl_wspeed = label("", "caption")
        opt.addWidget(self._slider_row("风速", self.lbl_wspeed, 0, 120,
                                       int(engine.wind_speed * 10), self._on_param))
        self.lbl_slope = label("", "caption")
        opt.addWidget(self._slider_row("地形坡度", self.lbl_slope, 0, 100,
                                       int(engine.slope * 100), self._on_param))

        algo_row = QHBoxLayout()
        algo_row.addWidget(label("规划算法", "muted"))
        algo_row.addStretch(1)
        self.algo = QComboBox()
        self.algo.addItems(["风险加权 A*（演示）", "A* 经典启发式", "Dijkstra 最短路径"])
        self.algo.setFixedWidth(180)
        algo_row.addWidget(self.algo)
        opt.addLayout(algo_row)

        self.cmp_box = QVBoxLayout()
        self.cmp_box.setSpacing(5)
        opt.addLayout(self.cmp_box)
        self.gain_pill = Pill("等待重新规划", "info")
        opt.content.addWidget(self.gain_pill, 0, Qt.AlignmentFlag.AlignLeft)
        right.addWidget(opt)
        right.addStretch(1)
        body.addLayout(right, 2)

        self.root.addLayout(body, 1)

        # 已移除激光点云与代价地图开关
        self.algo.currentIndexChanged.connect(self._on_param)
        self.robot_picker.currentIndexChanged.connect(self._on_picker)
        engine.tick.connect(self._refresh)
        self._on_picker()

    # ------------------------------------------------------------------
    def _slider_row(self, title: str, value_label, lo: int, hi: int, value: int, callback) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        head = QHBoxLayout()
        head.addWidget(label(title, "muted"))
        head.addStretch(1)
        head.addWidget(value_label)
        lay.addLayout(head)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(lo, hi)
        slider.setValue(value)
        slider.valueChanged.connect(callback)
        lay.addWidget(slider)
        self._sliders.append(slider)
        setattr(self, f"slider_{title}", slider)
        return w

    def _on_param(self, *_):
        self._update_slider_labels()
        if not hasattr(self, "algo") or not hasattr(self, "gain_pill") or not self._selected_robot_id:
            return
        self.engine.configure_robot_route(self._selected_robot_id,
            ["RL-A*", "A*", "Dijkstra"][self.algo.currentIndex()],
            self.slider_风向.value() + 180, self.slider_风速.value() / 10,
            self.slider_地形坡度.value() / 100)
        self._refresh()

    def _on_picker(self, *_):
        rid = self.robot_picker.currentData()
        if rid:
            self._on_robot_selected(rid)

    def _update_slider_labels(self):
        if not hasattr(self, "slider_风向"):
            return
        wind_deg = self.slider_风向.value() + 180
        wspeed = self.slider_风速.value() / 10
        slope = self.slider_地形坡度.value() / 100
        self.lbl_wind.setText(f"{wind_deg:.0f}°")
        self.lbl_wspeed.setText(f"{wspeed:.1f} m/s")
        self.lbl_slope.setText(f"{slope * 100:.0f}%")

    def _build_comparison(self):
        while self.cmp_box.count():
            item = self.cmp_box.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        r = next((x for x in self.engine.robots if x.id == self._selected_robot_id), None)
        if r is None:
            return
        plan = r.route_plan
        if r.route_failed:
            text = "路线不可达：设备已停止，等待目标或算法变更"
        elif plan is None:
            text = "当前无移动任务；新任务将使用此设备的设置"
        else:
            text = f"规划长度 {plan.length_m:.0f} m · 风险评分 {plan.risk * 100:.0f} · 剩余约 {r.eta_seconds:.0f} 步"
        self.cmp_box.addWidget(label(text, "caption"))
        self.gain_pill.set_kind("warning" if r.route_failed else "info")
        self.gain_pill.set_text("路径不可达" if r.route_failed else "设备路线已同步")

    def _restart_slam(self):
        self.slam_pill.set_text("SLAM 重建中 12%")
        self.slam_pill.set_kind("info")
        self.engine.push_event("SLAM 建图服务重新初始化，开始回环校准", "info")
        toast(self, "已重新启动 SLAM 建图，正在回环校准")

    def _estop(self):
        self.engine.estop = not self.engine.estop
        if self.engine.estop:
            self.estop_btn.setText("解除急停 / 恢复运行")
            self.estop_btn.setProperty("variant", "soft")
            self.estop_btn.setIcon(icons.icon("play", theme.ACCENT_DARK, 16))
            self.estop_btn.style().unpolish(self.estop_btn)
            self.estop_btn.style().polish(self.estop_btn)
            self.nav_state.setText("● 已紧急停止 · 等待指挥员确认")
            self.nav_state.setStyleSheet(f"color:{theme.RED}; font-size:11.5px; font-weight:700;")
            self.engine.push_event("指挥员触发 E-STOP，全部装备立即制动", "critical")
            self.engine.push_alert("紧急停止已触发", "8 台装备已制动，等待现场确认后恢复", "critical", "指挥终端")
            toast(self, "紧急停止已触发，全部装备制动", "warning")
        else:
            self.estop_btn.setText("紧急停止 E-STOP")
            self.estop_btn.setProperty("variant", "danger")
            self.estop_btn.setIcon(icons.icon("power", "#FFFFFF", 16))
            self.estop_btn.style().unpolish(self.estop_btn)
            self.estop_btn.style().polish(self.estop_btn)
            self.nav_state.setText("● 自主导航中 · 静态栅格避障")
            self.nav_state.setStyleSheet(f"color:{theme.ACCENT}; font-size:11.5px; font-weight:700;")
            self.engine.push_event("急停解除，导航任务恢复执行", "success")
            toast(self, "急停解除，任务已恢复")

    def _on_robot_selected(self, rid: str):
        r = next((x for x in self.engine.robots if x.id == rid), None)
        if r is None:
            return
        self._selected_robot_id = rid
        self.map.selected_robot = rid
        self.map.show_path = True
        controls = (self.robot_picker, self.algo, self.slider_风向, self.slider_风速, self.slider_地形坡度)
        for control in controls:
            control.blockSignals(True)
        self.robot_picker.setCurrentIndex(self.robot_picker.findData(rid))
        self.algo.setCurrentIndex(["RL-A*", "A*", "Dijkstra"].index(r.route_algo))
        self.slider_风向.setValue(round(r.route_wind) - 180)
        self.slider_风速.setValue(round(r.route_wind_speed * 10))
        self.slider_地形坡度.setValue(round(r.route_slope * 100))
        for control in controls:
            control.blockSignals(False)
        self._update_slider_labels()
        self._refresh()
        self.map.update()

    def _refresh(self):
        if not self._selected_robot_id:
            self.robot_info_label.setText("点击地图上的设备查看单体状态与规划路径")
            return
        r = next((x for x in self.engine.robots if x.id == self._selected_robot_id), self.engine.robots[0])
        eta = f"ETA {r.eta_seconds:.0f}s ({r.eta_status})" if r.mission == "en_route" else r.task
        self._build_comparison()
        self.robot_info_label.setText(
            f"选中装备 {r.id} ({r.name}) · 电量 {r.battery:.0f}% · 机身温度 {r.temp:.1f}℃ · "
            f"速度 {r.speed:.1f} m/s · 高度 {r.altitude:.0f} m · {eta}"
        )
        e = self.engine
        self.t_speed.set_text(f"速度 {r.speed:.1f} m/s" if not e.estop else "速度 0.0 m/s（急停）")
        import math
        self.t_head.set_text(f"航向 {math.degrees(r.heading) % 360:03.0f}°")
        self.t_obs.set_text("最近障碍 1.6 m" if not e.estop else "已制动 · 安全")
