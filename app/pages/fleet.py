"""装备管理页与遥控终端。"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .. import icons, theme
from ..canvas import CameraView, FirstPerson3DView, VideoFeed
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
    """遥控终端：真实视频流画面（EO / 红外）+ 键盘直控。"""

    KEYMAP = {
        Qt.Key.Key_W: "前进", Qt.Key.Key_S: "后退",
        Qt.Key.Key_A: "左移", Qt.Key.Key_D: "右移",
        Qt.Key.Key_J: "左旋", Qt.Key.Key_L: "右旋",
        Qt.Key.Key_I: "上升", Qt.Key.Key_K: "下降",
        Qt.Key.Key_Space: "悬停",
    }

    DARK_QSS = """
    #console { background: #0D1216; border-radius: 18px; }
    #console QLabel { color: #C6D5CE; }
    #console QLabel[role="title"] { color: #FFFFFF; }
    #console QLabel[role="caption"] { color: #7C8F87; }
    #console QLabel[role="strong"] { color: #EAF3EE; }
    #console QPushButton[variant="dp"] {
        background: #182026; border: 1px solid #26343B; border-radius: 9px;
        color: #D8E5DF; font-weight: 600;
    }
    #console QPushButton[variant="dp"]:hover { background: #223038; border-color: #12A66A; }
    #console QPushButton[variant="dp"]:pressed { background: #12A66A; color: #FFFFFF; }
    #console QPushButton[variant="dpCenter"] {
        background: #12A66A; border: 1px solid #16C07C; border-radius: 9px;
        color: #FFFFFF; font-weight: 700;
    }
    #console QPushButton[variant="dpCenter"]:hover { background: #16C07C; }
    #console QPushButton[variant="darkSoft"] {
        background: #182026; border: 1px solid #26343B; border-radius: 9px;
        color: #D8E5DF; font-weight: 600;
    }
    #console QPushButton[variant="darkSoft"]:hover { background: #223038; border-color: #12A66A; }
    #console QPushButton[variant="darkDanger"] {
        background: rgba(229, 72, 77, 0.16); border: 1px solid rgba(229, 72, 77, 0.45);
        border-radius: 9px; color: #FF9EA1; font-weight: 600;
    }
    #console QPushButton[variant="darkDanger"]:hover { background: rgba(229, 72, 77, 0.28); }
    #console QSlider::groove:horizontal {
        height: 4px; background: #24313A; border-radius: 2px;
    }
    #console QSlider::sub-page:horizontal { background: #12A66A; border-radius: 2px; }
    #console QSlider::handle:horizontal {
        background: #FFFFFF; width: 12px; height: 12px; margin: -5px 0; border-radius: 6px;
        border: 2px solid #12A66A;
    }
    """

    def __init__(self, engine: SimEngine, robot: Robot, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.robot = robot
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.resize(880, 512)
        self._drag = None
        self.connected = True

        shell = QFrame(self)
        shell.setObjectName("console")
        shell.setStyleSheet(self.DARK_QSS)
        shadow(shell, 44, 12, 70)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(shell)
        body = QVBoxLayout(shell)
        body.setContentsMargins(18, 14, 18, 16)
        body.setSpacing(10)

        # ---------------- 标题栏 ----------------
        head = QHBoxLayout()
        head.setSpacing(9)
        color = theme.BLUE if robot.kind == "UAV" else theme.ACCENT
        head.addWidget(IconTile("drone" if robot.kind == "UAV" else "robot",
                                color, "#1A2530", 32, 16, 9))
        col = QVBoxLayout()
        col.setSpacing(0)
        t = label(f"遥控终端 · {robot.id} {robot.name}", None, size=14, weight=700,
                  color="#FFFFFF")
        t.setProperty("role", "title")
        col.addWidget(t)
        c = label(f"{robot.model} · 2.4G 加密链路 · 时延 42 ms", None, size=10.5,
                  color="#7C8F87")
        c.setProperty("role", "caption")
        col.addWidget(c)
        head.addLayout(col)
        head.addStretch(1)

        self.link_pill = Pill("链路正常", "success")
        head.addWidget(self.link_pill)
        self.link_btn = QPushButton("断开")
        self.link_btn.setProperty("variant", "darkSoft")
        self.link_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.link_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.link_btn.setFixedSize(58, 28)
        self.link_btn.clicked.connect(self._toggle_link)
        head.addWidget(self.link_btn)
        close = QPushButton("×")
        close.setProperty("variant", "darkSoft")
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close.setFixedSize(28, 28)
        close.setStyleSheet("color:#D8E5DF; font-size:16px; padding:0px;")
        close.clicked.connect(self.close)
        head.addWidget(close)
        body.addLayout(head)

        # ---------------- 主体 ----------------
        content = QHBoxLayout()
        content.setSpacing(12)

        # 左：3D 第一人称视角 + 按键提示
        left = QVBoxLayout()
        left.setSpacing(7)
        self.feed = FirstPerson3DView(engine, robot)
        self.feed.setMinimumHeight(300)
        left.addWidget(self.feed, 1)

        hint = QLabel("W/S 前进后退 · A/D 或 J/L 左右转动视角 · I/K 俯仰 · 鼠标拖拽视角 · ESC 关闭")
        hint.setStyleSheet("color:#7C8F87; font-size:10.5px; background:transparent;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left.addWidget(hint)
        content.addLayout(left, 1)

        # 右：控制列
        rail = QVBoxLayout()
        rail.setSpacing(8)

        stats = QGridLayout()
        stats.setHorizontalSpacing(6)
        stats.setVerticalSpacing(6)
        self.stat_labels = {}
        stats.setColumnStretch(0, 1)
        stats.setColumnStretch(1, 1)
        for i, (k, v) in enumerate((("链路", "-52 dBm"), ("码率", "4.2 Mbps"),
                                    ("电量", f"{robot.battery:.0f}%"),
                                    ("续航", f"{max(6, int(robot.battery * 0.22))} min"))):
            tile = QWidget()
            soft_bg(tile, "#141B21", 9)
            lay = QVBoxLayout(tile)
            lay.setContentsMargins(9, 6, 9, 6)
            lay.setSpacing(0)
            kl = label(k, None, size=9.5, color="#7C8F87")
            vl = label(v, None, size=12, weight=700, color="#EAF3EE")
            lay.addWidget(kl)
            lay.addWidget(vl)
            self.stat_labels[k] = vl
            stats.addWidget(tile, i // 2, i % 2)
        rail.addLayout(stats)

        dpad = QGridLayout()
        dpad.setSpacing(5)
        cells = [(0, 0, "左旋"), (0, 1, "前进"), (0, 2, "右旋"),
                 (1, 0, "左移"), (1, 1, "悬停"), (1, 2, "右移"),
                 (2, 0, "上升"), (2, 1, "后退"), (2, 2, "下降")]
        for r, c, text in cells:
            b = QPushButton(text)
            b.setProperty("variant", "dpCenter" if text == "悬停" else "dp")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(32)
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            b.setStyleSheet("font-size:11.5px;")
            b.clicked.connect(lambda _=False, t=text: self._command(t))
            dpad.addWidget(b, r, c)
        rail.addLayout(dpad)

        spd_row = QHBoxLayout()
        spd_row.setSpacing(6)
        spd_row.addWidget(label("速度上限", None, size=10.5, color="#7C8F87"))
        spd_row.addStretch(1)
        self.speed_label = label("2.0 m/s", None, size=11, weight=700, color="#EAF3EE")
        spd_row.addWidget(self.speed_label)
        rail.addLayout(spd_row)
        self.speed = QSlider(Qt.Orientation.Horizontal)
        self.speed.setRange(5, 80)
        self.speed.setValue(20)
        self.speed.valueChanged.connect(lambda v: self.speed_label.setText(f"{v / 10:.1f} m/s"))
        rail.addWidget(self.speed)

        spray_row = QHBoxLayout()
        spray_row.setSpacing(6)
        spray_row.addWidget(label("喷洒 / 载荷", None, size=10.5, color="#7C8F87"))
        spray_row.addStretch(1)
        self.spray = ToggleSwitch(False)
        self.spray.toggled.connect(lambda v: self._command("开启喷洒" if v else "关闭喷洒"))
        spray_row.addWidget(self.spray)
        self.thermal = ToggleSwitch(False)
        self.thermal.toggled.connect(self._toggle_thermal)
        spray_row.addWidget(label("红外", None, size=10.5, color="#7C8F87"))
        spray_row.addWidget(self.thermal)
        rail.addLayout(spray_row)

        acts = QHBoxLayout()
        acts.setSpacing(6)
        home_btn = QPushButton("一键返航")
        home_btn.setProperty("variant", "darkSoft")
        home_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        home_btn.setFixedHeight(32)
        home_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        home_btn.clicked.connect(lambda: self._command("返航"))
        stop_btn = QPushButton("急停")
        stop_btn.setProperty("variant", "darkDanger")
        stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        stop_btn.setFixedHeight(32)
        stop_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        stop_btn.clicked.connect(lambda: self._command("急停"))
        acts.addWidget(home_btn, 1)
        acts.addWidget(stop_btn, 1)
        rail.addLayout(acts)

        self.log = label("等待指令…", None, size=10, color="#8FA79C")
        self.log.setWordWrap(True)
        self.log.setFixedHeight(34)
        rail.addWidget(self.log)
        rail.addStretch(1)
        content.addLayout(rail, 0)
        rail.setAlignment(Qt.AlignmentFlag.AlignTop)

        body.addLayout(content, 1)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    # ------------------------------------------------------------------
    def _toggle_link(self):
        self.connected = not self.connected
        self.feed.set_connected(self.connected)
        self.link_btn.setText("断开" if self.connected else "重连")
        self.link_pill.set_kind("success" if self.connected else "critical")
        self.link_pill.set_text("链路正常" if self.connected else "未连接")
        self.log.setText("视频链路已断开，飞行器保持悬停。" if not self.connected
                         else "链路已恢复，视频流重连成功。")

    def _toggle_thermal(self, on: bool):
        self.feed.set_mode("ir" if on else "eo")
        self.log.setText("已切换至红外热成像通道。" if on else "已切换至可见光通道。")

    def _command(self, text: str):
        if not self.connected and text != "返航":
            self.log.setText("链路未连接，指令已排队等待重连…")
            return
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
            self.feed.spraying = (text == "开启喷洒")
            self.log.setText(f"{r.id} 载荷状态：{text}")
        else:
            if text in ("左移", "左旋"):
                self.feed.pan(dyaw=-0.16)
            elif text in ("右移", "右旋"):
                self.feed.pan(dyaw=0.16)
            elif text == "前进":
                self.feed.pan(dz=0.35)
            elif text == "后退":
                self.feed.pan(dz=-0.35)
            elif text == "上升":
                self.feed.pan(dpitch=0.06)
            elif text == "下降":
                self.feed.pan(dpitch=-0.06)
            self.log.setText(f"{r.id} 执行「{text}」· {self.speed.value() / 10:.1f} m/s")
        if self.connected:
            self.link_pill.set_text("指令已送达")

    def _tick(self):
        if not self.isVisible():
            return
        r = self.robot
        if "电量" in self.stat_labels:
            self.stat_labels["电量"].setText(f"{r.battery:.0f}%")

    # ------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return
        cmd = self.KEYMAP.get(event.key())
        if cmd:
            self._command(cmd)
            return
        super().keyPressEvent(event)

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
