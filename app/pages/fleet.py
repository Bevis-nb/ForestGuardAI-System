"""装备管理页与遥控终端。"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .. import icons, theme
from ..canvas import CameraView
from ..charts import LineChart
from ..simulation import Robot, SimEngine
from ..widgets import (
    Card,
    IconTile,
    KeyValueRow,
    Pill,
    ProgressLine,
    RingGauge,
    ToggleSwitch,
    button,
    icon_button,
    label,
    shadow,
    toast,
    soft_bg,
)
from .base import Panel, ScrollPage, hline, kv_chip


class RobotCard(QFrame):
    clicked = Signal(str)

    def __init__(self, robot: Robot, parent=None):
        super().__init__(parent)
        self.robot = robot
        self.setObjectName("RobotCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(126)
        self._selected = False
        self._apply_style()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 11)
        lay.setSpacing(7)

        top = QHBoxLayout()
        top.setSpacing(9)
        color = theme.BLUE if robot.kind == "UAV" else theme.ACCENT
        soft = theme.BLUE_SOFT if robot.kind == "UAV" else theme.ACCENT_SOFT
        top.addWidget(IconTile("drone" if robot.kind == "UAV" else "robot", color, soft, 34, 17, 10))
        col = QVBoxLayout()
        col.setSpacing(0)
        col.addWidget(label(robot.id, None, size=13, weight=700))
        col.addWidget(label(robot.name, "caption"))
        top.addLayout(col)
        top.addStretch(1)
        self.status = Pill(robot.status_text, robot.status_kind)
        top.addWidget(self.status, 0, Qt.AlignmentFlag.AlignTop)
        lay.addLayout(top)

        self.task_label = label(f"任务：{robot.task}", "caption")
        lay.addWidget(self.task_label)

        self.battery = ProgressLine("", robot.battery,
                                    theme.ACCENT if robot.battery > 40 else theme.RED,
                                    suffix="%", show_head=False)
        lay.addWidget(self.battery)

        foot = QHBoxLayout()
        foot.setSpacing(6)
        self.battery_label = label(f"电量 {robot.battery:.0f}%", "caption")
        foot.addWidget(self.battery_label)
        foot.addStretch(1)
        self.signal_label = label(f"信号 {robot.signal:.0f}%", "caption")
        foot.addWidget(self.signal_label)
        self.temp_label = label(f"{robot.temp:.1f}℃", "caption",
                                color=theme.RED if robot.temp > 42 else theme.MUTED)
        foot.addWidget(self.temp_label)
        lay.addLayout(foot)

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet(
                f"#RobotCard {{ background:{theme.ACCENT_SOFT}; border:1.5px solid {theme.ACCENT};"
                f" border-radius:14px; }}"
            )
        else:
            self.setStyleSheet(
                f"#RobotCard {{ background:{theme.SURFACE}; border:1px solid {theme.BORDER};"
                f" border-radius:14px; }}"
                f"#RobotCard:hover {{ border:1px solid {theme.ACCENT_LIGHT}; }}"
            )

    def set_selected(self, selected: bool):
        self._selected = selected
        self._apply_style()

    def update_robot(self):
        r = self.robot
        self.status.set_text(r.status_text)
        self.status.set_kind(r.status_kind)
        self.task_label.setText(f"任务：{r.task}")
        self.battery.set_value(r.battery)
        self.battery_label.setText(f"电量 {r.battery:.0f}%")
        self.signal_label.setText(f"信号 {r.signal:.0f}%")
        self.temp_label.setText(f"{r.temp:.1f}℃")
        self.temp_label.setStyleSheet(
            f"color:{theme.RED if r.temp > 42 else theme.MUTED}; font-size:11px;"
        )

    def mousePressEvent(self, event):
        self.clicked.emit(self.robot.id)
        super().mousePressEvent(event)


class TelemetryGauge(QWidget):
    """小型半环遥测仪表。"""

    def __init__(self, title: str, value: float = 0, maximum: float = 100,
                 color: str = theme.ACCENT, suffix: str = "%", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.maximum = maximum
        self.color = QColor(color)
        self.suffix = suffix
        self.setFixedHeight(80)

    def set_value(self, value: float):
        self.value = value
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        radius = min(w / 2 - 12, h * 0.40)
        cx, cy = w / 2, h * 0.50
        rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
        p.setPen(QPen(QColor(theme.BG_DEEP), 7))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(rect, 210 * 16, -240 * 16)
        ratio = max(0.0, min(1.0, self.value / self.maximum)) if self.maximum else 0
        pen = QPen(self.color, 7)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, 210 * 16, int(-240 * 16 * ratio))

        p.setPen(QColor(theme.TEXT))
        f = self.font()
        f.setPixelSize(14)
        f.setWeight(f.Weight.Bold)
        p.setFont(f)
        p.drawText(QRectF(cx - w / 2, cy - 16, w, 20), Qt.AlignmentFlag.AlignCenter,
                   f"{self.value:.0f}{self.suffix}")
        p.setPen(QColor(theme.MUTED))
        f.setPixelSize(10)
        f.setWeight(f.Weight.Normal)
        p.setFont(f)
        p.drawText(QRectF(cx - w / 2, cy + 3, w, 15), Qt.AlignmentFlag.AlignCenter, self.title)
        p.end()


class RemoteControlDialog(QDialog):
    """亮色遥控终端：方向控制 + 云台 + 喷洒 + 一键返航。"""

    def __init__(self, engine: SimEngine, robot: Robot, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.robot = robot
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(False)
        self.resize(880, 560)
        self._drag = None

        shell = QFrame(self)
        shell.setObjectName("Card")
        shadow(shell, 40, 10, 60)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(shell)
        body = QVBoxLayout(shell)
        body.setContentsMargins(20, 16, 20, 18)
        body.setSpacing(12)

        # 标题栏
        head = QHBoxLayout()
        head.setSpacing(9)
        color = theme.BLUE if robot.kind == "UAV" else theme.ACCENT
        soft = theme.BLUE_SOFT if robot.kind == "UAV" else theme.ACCENT_SOFT
        head.addWidget(IconTile("drone" if robot.kind == "UAV" else "robot", color, soft, 34, 17, 10))
        col = QVBoxLayout()
        col.setSpacing(0)
        col.addWidget(label(f"遥控终端 · {robot.id} {robot.name}", None, size=15, weight=700))
        col.addWidget(label(f"{robot.model} · 链路时延 42 ms · 加密通道", "caption"))
        head.addLayout(col)
        head.addStretch(1)
        self.link_pill = Pill("链路正常", "success")
        head.addWidget(self.link_pill)
        head.addWidget(icon_button("close", theme.MUTED, 32, 16, self.close))
        body.addLayout(head)

        content = QHBoxLayout()
        content.setSpacing(14)

        # 左：画面 + 遥测
        left = QVBoxLayout()
        left.setSpacing(10)
        self.cam = CameraView(engine)
        self.cam.setMinimumSize(420, 250)
        left.addWidget(self.cam, 1)
        tele = QHBoxLayout()
        tele.setSpacing(6)
        self.chips = {
            "alt": kv_chip("activity", f"高度 {robot.altitude:.0f} m"),
            "speed": kv_chip("wind", f"速度 {robot.speed:.1f} m/s"),
            "bat": kv_chip("battery", f"电量 {robot.battery:.0f}%"),
            "temp": kv_chip("thermo", f"温度 {robot.temp:.1f} ℃", theme.AMBER, theme.AMBER_SOFT),
        }
        for chip in self.chips.values():
            tele.addWidget(chip)
        tele.addStretch(1)
        left.addLayout(tele)
        sw_row = QHBoxLayout()
        sw_row.setSpacing(8)
        sw_row.addWidget(label("热成像", "caption"))
        self.thermal = ToggleSwitch(False)
        self.thermal.toggled.connect(self.cam.set_thermal)
        sw_row.addWidget(self.thermal)
        sw_row.addStretch(1)
        sw_row.addWidget(label("云台 0.0° / 0.0°", "caption"))
        left.addLayout(sw_row)
        content.addLayout(left, 3)

        # 右：控制
        right = QVBoxLayout()
        right.setSpacing(10)

        dpad_wrap = QWidget()
        soft_bg(dpad_wrap, theme.SURFACE_ALT, 14)
        dpad = QGridLayout(dpad_wrap)
        dpad.setContentsMargins(14, 12, 14, 12)
        dpad.setSpacing(6)
        self._dir_buttons = {}
        layout_cells = [
            (0, 0, "左旋"), (0, 1, "前进"), (0, 2, "右旋"),
            (1, 0, "左移"), (1, 1, "悬停"), (1, 2, "右移"),
            (2, 0, "上升"), (2, 1, "后退"), (2, 2, "下降"),
        ]
        for r, c, text in layout_cells:
            center = text == "悬停"
            btn = button(text, "primary" if center else "soft", height=40, size=12,
                         on_click=lambda _=False, t=text: self._command(t))
            btn.setMinimumWidth(74)
            self._dir_buttons[text] = btn
            dpad.addWidget(btn, r, c)
        right.addWidget(dpad_wrap)

        speed_row = QHBoxLayout()
        speed_row.setSpacing(8)
        speed_row.addWidget(label("速度上限", "muted"))
        speed_row.addStretch(1)
        self.speed_label = label("2.0 m/s", None, size=11.5, weight=700)
        speed_row.addWidget(self.speed_label)
        right.addLayout(speed_row)
        self.speed = QSlider(Qt.Orientation.Horizontal)
        self.speed.setRange(5, 80)
        self.speed.setValue(20)
        self.speed.valueChanged.connect(lambda v: self.speed_label.setText(f"{v / 10:.1f} m/s"))
        right.addWidget(self.speed)

        spray = QWidget()
        soft_bg(spray, theme.SURFACE_ALT, 12)
        spray_lay = QHBoxLayout(spray)
        spray_lay.setContentsMargins(12, 9, 12, 9)
        spray_lay.addWidget(label("喷洒 / 载荷", "muted"))
        spray_lay.addStretch(1)
        self.spray = ToggleSwitch(False)
        self.spray.toggled.connect(lambda v: self._command("开启喷洒" if v else "关闭喷洒"))
        spray_lay.addWidget(self.spray)
        right.addWidget(spray)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(button("一键返航", "blue", "home", height=38,
                                 on_click=lambda: self._command("返航")), 1)
        actions.addWidget(button("急停", "dangerSoft", "power", height=38,
                                 on_click=lambda: self._command("急停")), 1)
        right.addLayout(actions)

        log_panel = QWidget()
        soft_bg(log_panel, theme.SURFACE_ALT, 12)
        log_lay = QVBoxLayout(log_panel)
        log_lay.setContentsMargins(12, 9, 12, 9)
        log_lay.setSpacing(4)
        log_lay.addWidget(label("指令回执", "caption"))
        self.log = label("等待指令…", "caption", color=theme.MUTED)
        self.log.setWordWrap(True)
        log_lay.addWidget(self.log)
        right.addWidget(log_panel)

        info = QVBoxLayout()
        info.setSpacing(2)
        for k, v in (("剩余续航", f"{max(6, int(robot.battery * 0.22))} min"),
                     ("载荷余量", "12 L" if robot.kind == "UGV" else "4 L"),
                     ("定位精度", "±0.08 m"),
                     ("链路质量", f"{robot.signal:.0f}% · 42 ms")):
            row = QHBoxLayout()
            row.addWidget(label(k, "caption"))
            row.addStretch(1)
            row.addWidget(label(v, None, size=11.5, weight=600, color=theme.TEXT_SOFT))
            info.addLayout(row)
        right.addSpacing(2)
        right.addLayout(info)
        right.addStretch(1)
        right.addStretch(1)
        content.addLayout(right, 2)
        body.addLayout(content, 1)

        self.timer = QTimer(self)
        self.timer.setInterval(900)
        self.timer.timeout.connect(self._tick)
        self.timer.start()

    # ------------------------------------------------------------------
    def _command(self, text: str):
        r = self.robot
        if text == "返航":
            r.status = "returning"
            self.log.setText("返航指令已下发，正在规划安全航路…")
            self.engine.push_event(f"{r.id} 由遥控终端下发返航指令", "info")
        elif text == "急停":
            self.log.setText("已制动，等待指挥员确认。")
            self.engine.estop = True
            self.engine.push_event(f"{r.id} 遥控急停，链路保持", "critical")
        elif text in ("开启喷洒", "关闭喷洒"):
            self.log.setText(f"{r.id} 载荷状态：{text}")
        else:
            self.log.setText(f"{r.id} 执行「{text}」，速度 {self.speed.value() / 10:.1f} m/s")
        self.link_pill.set_text("指令已送达")

    def _tick(self):
        if not self.isVisible():
            return
        r = self.robot
        self.chips["bat"].set_text(f"电量 {r.battery:.0f}%")
        self.chips["temp"].set_text(f"温度 {r.temp:.1f} ℃")
        self.chips["speed"].set_text(f"速度 {r.speed:.1f} m/s")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag = None
        super().mouseReleaseEvent(event)


class FleetPage(ScrollPage):
    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(
            engine,
            "装备管理",
            "8 台林火装备 · 电池 / 链路 / 载荷实时遥测 · 支持远程接管",
        )
        self.add_action(Pill("8 台在线", "success"))
        self.add_action(button("批量充电", "soft", "battery", height=34, on_click=self._charge_all))
        self.add_action(button("接入新装备", "primary", "plus", height=34, on_click=self._add))

        body = QHBoxLayout()
        body.setSpacing(14)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.cards: dict[str, RobotCard] = {}
        for i, robot in enumerate(engine.robots):
            card = RobotCard(robot)
            card.clicked.connect(self._select)
            self.cards[robot.id] = card
            grid.addWidget(card, i // 2, i % 2)
        left = QVBoxLayout()
        left.setSpacing(12)
        left.addLayout(grid, 1)

        stats = Card(padding=14, spacing=6)
        st = QHBoxLayout()
        st.setSpacing(10)
        for title, value, unit, color in (("机巢占用", "6 / 8", "位", theme.ACCENT),
                                          ("今日任务", "24", "项", theme.BLUE),
                                          ("平均续航", "72", "%", theme.AMBER),
                                          ("故障告警", "0", "次", theme.RED)):
            col = QVBoxLayout()
            col.setSpacing(1)
            col.addWidget(label(title, "caption"))
            row = QHBoxLayout()
            row.setSpacing(3)
            row.addWidget(label(value, None, size=18, weight=700, color=color))
            row.addWidget(label(unit, "caption"))
            row.addStretch(1)
            col.addLayout(row)
            st.addLayout(col, 1)
        stats.add_layout(st)
        left.addWidget(stats)
        body.addLayout(left, 3)

        # 右侧详情
        self.detail = Panel("装备详情", "选择左侧装备查看遥测", "info")
        self.detail_pill = Pill("待命", "info")
        self.detail.add_action(self.detail_pill)
        self.detail_title = label("UGV-01 獾式一号", None, size=16, weight=700)
        self.detail.addWidget(self.detail_title)
        self.detail_sub = label("FG-R3 履带底盘 · 编队 1 号位", "caption")
        self.detail.addWidget(self.detail_sub)
        self.detail.addWidget(hline())

        gauges = QHBoxLayout()
        gauges.setSpacing(6)
        self.g_battery = TelemetryGauge("电量", 68, 100, theme.ACCENT)
        self.g_temp = TelemetryGauge("温度", 41, 80, theme.AMBER, "℃")
        self.g_signal = TelemetryGauge("链路", 89, 100, theme.BLUE)
        for g in (self.g_battery, self.g_temp, self.g_signal):
            gauges.addWidget(g, 1)
        self.detail.addLayout(gauges)

        self.kv_task = KeyValueRow("当前任务", "地面扑打")
        self.kv_payload = KeyValueRow("载荷余量", "78%")
        self.kv_alt = KeyValueRow("相对高度", "0 m")
        self.kv_coord = KeyValueRow("坐标", "B-07 / 124.6 ha")
        for kv in (self.kv_task, self.kv_payload, self.kv_alt, self.kv_coord):
            self.detail.addWidget(kv)

        self.detail.addWidget(label("近 10 分钟温度趋势", "muted"))
        self.chart = LineChart({"温度 ℃": engine.robots[4].history or [38, 39, 41]},
                               colors=(theme.AMBER,), height=110, y_min=20, fill=True)
        self.detail.addWidget(self.chart)

        self.detail.addWidget(hline())
        self.detail.addWidget(label("近期任务履历", "muted"))
        for t, task, state in (("14:12", "A-09 火线北侧压制", "完成"),
                               ("13:40", "B-07 隔离带开挖", "完成"),
                               ("12:55", "基地补给 · 更换电池", "完成"),
                               ("11:20", "C-02 水带铺设", "中止")):
            row = QHBoxLayout()
            row.setSpacing(8)
            row.addWidget(label(t, "caption", color=theme.MUTED))
            row.addWidget(label(task, None, size=11.5, color=theme.TEXT_SOFT))
            row.addStretch(1)
            row.addWidget(Pill(state, "success" if state == "完成" else "warning"))
            self.detail.addLayout(row)

        btns = QHBoxLayout()
        btns.setSpacing(8)
        btns.addWidget(button("遥控接管", "primary", "drone", height=38, on_click=self._open_remote), 1)
        btns.addWidget(button("返航", "soft", "home", height=38, on_click=self._return), 1)
        btns.addWidget(button("充电", "blue", "battery", height=38, on_click=self._charge), 1)
        self.detail.addLayout(btns)
        self.detail.content.addStretch(1)
        body.addWidget(self.detail, 2)

        self.root.addLayout(body, 1)

        self.selected = engine.robots[4].id
        self._select(self.selected)
        engine.tick.connect(self._refresh)

    # ------------------------------------------------------------------
    def _select(self, robot_id: str):
        self.selected = robot_id
        for rid, card in self.cards.items():
            card.set_selected(rid == robot_id)
        robot = next(r for r in self.engine.robots if r.id == robot_id)
        self.detail_title.setText(f"{robot.id} {robot.name}")
        self.detail_sub.setText(f"{robot.model} · 任务：{robot.task}")
        self.detail_pill.set_text(robot.status_text)
        self.detail_pill.set_kind(robot.status_kind)
        self.g_battery.set_value(robot.battery)
        self.g_temp.set_value(robot.temp)
        self.g_signal.set_value(robot.signal)
        self.kv_task.set_value(robot.task)
        self.kv_payload.set_value(f"{robot.payload:.0f}%")
        self.kv_alt.set_value(f"{robot.altitude:.0f} m")
        self.kv_coord.set_value(f"{'A' if robot.x < 0.34 else ('B' if robot.x < 0.62 else 'C')}-{int(robot.y * 12) + 1:02d}")
        self.chart.set_series({"温度 ℃": robot.history[-14:] or [38, 39, 41]})
        self._robot = robot

    def _refresh(self):
        for card in self.cards.values():
            card.update_robot()
        robot = getattr(self, "_robot", None)
        if robot:
            self.g_battery.set_value(robot.battery)
            self.g_temp.set_value(robot.temp)
            self.g_signal.set_value(robot.signal)
            self.chart.set_series({"温度 ℃": robot.history[-14:] or [38]})

    def _open_remote(self):
        robot = getattr(self, "_robot", self.engine.robots[0])
        dlg = RemoteControlDialog(self.engine, robot, self)
        dlg.show()

    def _return(self):
        robot = getattr(self, "_robot", self.engine.robots[0])
        robot.status = "returning"
        self.engine.push_event(f"{robot.id} 收到返航指令，正在规划安全路线", "info")
        toast(self, f"{robot.id} 已开始返航")
        self._refresh()

    def _charge(self):
        robot = getattr(self, "_robot", self.engine.robots[0])
        robot.status = "charging"
        toast(self, f"{robot.id} 已进入机巢充电")
        self._refresh()

    def _charge_all(self):
        for r in self.engine.robots:
            if r.status in ("standby", "returning"):
                r.status = "charging"
        self.engine.push_event("指挥终端下发批量充电指令", "info")
        toast(self, "待命装备已进入机巢充电")

    def _add(self):
        toast(self, "新装备接入需在机巢完成配对（演示环境）", "info")
