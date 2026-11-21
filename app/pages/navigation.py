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
            "SLAM 融合建图 · 强化学习路径优化 · 风场/地形动态避险",
        )
        self._sliders: list[QSlider] = []
        self.slam_pill = self.add_action(Pill("SLAM 建图中 87%", "success"))
        self.add_action(button("重新建图", "soft", "refresh", height=34,
                               on_click=self._restart_slam))
        self.add_action(button("生成最优路径", "primary", "route", height=34,
                               on_click=self._replan))

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
        self.sw_lidar = ToggleSwitch(True)
        ctrl.addWidget(self.sw_lidar)
        ctrl.addWidget(label("激光点云", "caption"))
        self.sw_cost = ToggleSwitch(True)
        ctrl.addWidget(self.sw_cost)
        ctrl.addWidget(label("代价地图", "caption"))
        ctrl.addStretch(1)
        self.nav_state = label("● 自主导航中 · 动态避障已开启", None,
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
        band.addWidget(label("动态避障", "muted"))
        self.sw_avoid = ToggleSwitch(True)
        band.addWidget(self.sw_avoid)
        band.addSpacing(6)
        band.addWidget(label("自动急停", "muted"))
        self.sw_autostop = ToggleSwitch(True)
        band.addWidget(self.sw_autostop)
        band.addSpacing(6)
        band.addWidget(label("高温阈值", "muted"))
        self.temp_spin = QSpinBox()
        self.temp_spin.setRange(45, 180)
        self.temp_spin.setValue(85)
        self.temp_spin.setSuffix(" ℃")
        self.temp_spin.setFixedWidth(92)
        band.addWidget(self.temp_spin)
        band.addStretch(1)
        self.estop_btn = button("紧急停止 E-STOP", "danger", "power", height=38, size=12.5,
                                on_click=self._estop)
        self.estop_btn.setMinimumWidth(190)
        band.addWidget(self.estop_btn)
        safe.addLayout(band)
        self.safe_log = label("最近事件：T+02:14 绕行倒木障碍（距 1.6 m），导航任务未中断", "caption")
        safe.addWidget(self.safe_log)
        left.addWidget(safe)
        body.addLayout(left, 3)

        # ---------------- 右：SLAM 与路径 ----------------
        right = QVBoxLayout()
        right.setSpacing(12)

        slam = Panel("建图状态", "Gmapping + 视觉回环", "layers")
        slam.add_action(Pill("精度 0.08 m", "info"))
        for key, val in (("关键帧 / 回环", "1,284 帧 / 12 次"), ("累计里程", "3.42 km")):
            slam.addWidget(KeyValueRow(key, val))
        slam.addWidget(ProgressLine("建图进度", 87, theme.ACCENT))
        slam.addWidget(ProgressLine("点云覆盖率", 92, theme.BLUE))
        right.addWidget(slam)

        opt = Panel("路径优化 · 强化学习", "结合风向、坡度、热源的代价函数", "route")
        opt.add_action(Pill("RL-A*", "purple"))

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
        self.algo.addItems(["RL-A* 强化学习优化", "A* 经典启发式", "Dijkstra 最短路径", "RRT* 采样规划"])
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

        self.sw_lidar.toggled.connect(self.map.set_lidar_visible)
        self.sw_cost.toggled.connect(self.map.set_costmap_visible)
        self.temp_spin.valueChanged.connect(self._on_threshold)
        self._build_comparison()
        self._update_slider_labels()
        self.gain_pill.set_kind("success")
        self.gain_pill.set_text("RL 策略已生效 · 风险下降 5 分 / 耗时 -1 s")
        engine.tick.connect(self._refresh)
        self._refresh()

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
        if hasattr(self, "gain_pill"):
            self.gain_pill.set_kind("info")
            self.gain_pill.set_text("参数已修改，点击「生成最优路径」")

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
        rows = [
            ("路径长度", f"{self.engine.baseline.length_m:.0f} m", f"{self.engine.plan.length_m:.0f} m"),
            ("预计耗时", f"{self.engine.baseline.eta_s:.0f} s", f"{self.engine.plan.eta_s:.0f} s"),
            ("能耗预估", f"{self.engine.baseline.energy:.1f} %", f"{self.engine.plan.energy:.1f} %"),
            ("风险评分", f"{self.engine.baseline.risk * 100:.0f}", f"{self.engine.plan.risk * 100:.0f}"),
        ]
        while self.cmp_box.count():
            item = self.cmp_box.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(0, 0, 0, 0)
        for text, stretch, align in (("指标", 2, Qt.AlignmentFlag.AlignLeft),
                                     ("常规 A*", 1, Qt.AlignmentFlag.AlignRight),
                                     ("RL 优化", 1, Qt.AlignmentFlag.AlignRight)):
            hl.addWidget(label(text, "caption"), stretch, align)
        self.cmp_box.addWidget(header)
        for name, base, opt in rows:
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 1, 0, 1)
            rl.addWidget(label(name, "muted"), 2)
            rl.addWidget(label(base, None, color=theme.MUTED_LIGHT, size=11.5), 1,
                         Qt.AlignmentFlag.AlignRight)
            rl.addWidget(label(opt, None, color=theme.ACCENT_DARK, size=11.5, weight=700), 1,
                         Qt.AlignmentFlag.AlignRight)
            self.cmp_box.addWidget(row)

    # ------------------------------------------------------------------
    def _replan(self):
        wind_deg = self.slider_风向.value() + 180
        wspeed = self.slider_风速.value() / 10
        slope = self.slider_地形坡度.value() / 100
        algo = ["RL-A*", "A*", "Dijkstra", "RRT*"][self.algo.currentIndex()]
        r = next((x for x in self.engine.robots if x.id == self._selected_robot_id), self.engine.robots[0])
        start = (r.x, r.y)
        goal = (r.home_x, r.home_y) if r.mission == "returning" else (
            (r.target_x, r.target_y) if r.mission in ("en_route", "spraying", "recon") else self.engine.fire_origin
        )
        plan = self.engine.replan(wind_deg, wspeed, slope, algo, start=start, goal=goal)
        risk_drop = (self.engine.baseline.risk - plan.risk) * 100
        self._build_comparison()
        if risk_drop > 0.4:
            self.gain_pill.set_kind("success")
            self.gain_pill.set_text(
                f"风险评分下降 {risk_drop:.0f} 分 · 耗时 {plan.eta_s:.0f}s"
            )
        else:
            self.gain_pill.set_kind("warning")
            self.gain_pill.set_text("当前参数下常规算法更优")
        self.engine.push_event(
            f"{algo} 路径重算完成：{plan.length_m:.0f} m / 预计 {plan.eta_s:.0f} s，已下发 UGV-01", "success")
        self.map.set_static_dirty()
        toast(self, f"最优路径已生成：{plan.length_m:.0f} m，预计 {plan.eta_s:.0f} 秒到达")

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
            self.nav_state.setText("● 自主导航中 · 动态避障已开启")
            self.nav_state.setStyleSheet(f"color:{theme.ACCENT}; font-size:11.5px; font-weight:700;")
            self.engine.push_event("急停解除，导航任务恢复执行", "success")
            toast(self, "急停解除，任务已恢复")

    def _on_threshold(self, value: int):
        self.safe_log.setText(f"最近事件：温度阈值调整为 {value} ℃，超限将自动刹停并请求指挥确认")

    def _on_robot_selected(self, rid: str):
        self._selected_robot_id = rid
        self.map.show_path = True
        self._refresh()
        self._replan()

    def _refresh(self):
        if not self._selected_robot_id:
            self.robot_info_label.setText("点击地图上的设备查看单体状态与规划路径")
            return
        r = next((x for x in self.engine.robots if x.id == self._selected_robot_id), self.engine.robots[0])
        eta = f"ETA {r.eta_seconds:.0f}s ({r.eta_status})" if r.mission == "en_route" else r.task
        self.robot_info_label.setText(
            f"选中装备 {r.id} ({r.name}) · 电量 {r.battery:.0f}% · 机身温度 {r.temp:.1f}℃ · "
            f"速度 {r.speed:.1f} m/s · 高度 {r.altitude:.0f} m · {eta}"
        )
        e = self.engine
        self.t_speed.set_text("速度 1.8 m/s" if not e.estop else "速度 0.0 m/s（急停）")
        self.t_head.set_text(f"航向 {(e.wind_deg + 174) % 360:03.0f}°")
        self.t_obs.set_text("最近障碍 1.6 m" if not e.estop else "已制动 · 安全")
