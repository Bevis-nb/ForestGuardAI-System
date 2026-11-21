"""人机交互页（对应系统设计 2.4）。"""
from __future__ import annotations

import random
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QTextCursor
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QTextEdit, QVBoxLayout, QWidget

from .. import icons, theme
from ..canvas import Waveform
from ..simulation import SimEngine
from ..widgets import Dialog, Pill, ToggleRow, button, icon_button, label, soft_bg, toast
from .base import Panel, ScrollPage, hline, kv_chip


EXAMPLES = [
    "一键启动预案 A",
    "无人机返航",
    "喷洒灭火剂",
    "开挖隔离带",
    "查看火场态势",
    "紧急停止",
]


class Console(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFrameShape(QTextEdit.Shape.NoFrame)
        self.setStyleSheet(
            f"QTextEdit {{ background:{theme.SURFACE_ALT}; border-radius:12px; padding:10px;"
            f" font-size:12.5px; color:{theme.TEXT_SOFT}; }}"
        )
        self.setMinimumHeight(260)

    def add(self, who: str, text: str, kind: str = "system"):
        color = {"system": theme.ACCENT_DARK, "user": theme.BLUE,
                 "alert": theme.RED, "ok": theme.ACCENT}[kind]
        tag = {"system": "指挥终端", "user": "指挥员", "alert": "告警", "ok": "执行回执"}[kind]
        stamp = datetime.now().strftime("%H:%M:%S")
        html = (
            f"<div style='margin-bottom:7px'>"
            f"<span style='color:{theme.MUTED_LIGHT}; font-size:11px;'>{stamp}</span> "
            f"<span style='color:{color}; font-weight:700;'>[{tag}]</span> "
            f"<span style='color:{theme.TEXT_SOFT};'>{text}</span></div>"
        )
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.insertHtml(html)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class InteractionPage(ScrollPage):
    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(
            engine,
            "人机交互",
            "语音 / 文本指令 · 一键预设方案 · 人工干预与接管",
        )
        self.add_action(Pill("语音引擎就绪", "success"))
        self.add_action(button("语音唤醒", "soft", "mic", height=34, on_click=self._voice_once))
        self.add_action(button("一键启动预案 A", "primary", "sparkles", height=34,
                               on_click=lambda: self._launch_plan("A")))

        body = QHBoxLayout()
        body.setSpacing(14)

        # ---------------- 左：语音 ----------------
        voice = Panel("语音指挥", "离线唤醒词「智护森林」· 支持 6 类指令", "mic")
        voice.add_action(Pill("就绪", "success"))
        self.wave = Waveform()
        voice.add(self.wave)
        self.mic_btn = QWidget()
        mic_lay = QHBoxLayout(self.mic_btn)
        mic_lay.setContentsMargins(0, 0, 0, 0)
        mic_lay.setSpacing(10)
        self.mic = button("按住说话", "primary", "mic", height=42, size=13, on_click=self._toggle_voice)
        mic_lay.addWidget(self.mic, 1)
        voice.addWidget(self.mic_btn)

        voice.addWidget(label("识别结果", "muted"))
        self.recognized = label("等待语音输入…", None, color=theme.MUTED, size=12)
        self.recognized.setWordWrap(True)
        self.recognized.setStyleSheet(
            f"color:{theme.MUTED}; background:{theme.SURFACE_ALT}; border-radius:10px;"
            f" padding:10px; font-size:12px;"
        )
        voice.addWidget(self.recognized)

        voice.addWidget(label("示例指令", "muted"))
        chips = QVBoxLayout()
        chips.setSpacing(6)
        for i in range(0, len(EXAMPLES), 2):
            row = QHBoxLayout()
            row.setSpacing(6)
            for text in EXAMPLES[i:i + 2]:
                chip = button(text, "soft", height=28, size=11,
                              on_click=lambda _=False, t=text: self._run_command(t))
                row.addWidget(chip, 1)
            chips.addLayout(row)
        voice.addLayout(chips)
        voice.addWidget(label("最近语音指令", "muted"))
        self.voice_log = QVBoxLayout()
        self.voice_log.setSpacing(3)
        voice.addLayout(self.voice_log)
        self._add_voice_log("一键启动预案 A", "14:32", "success")
        self._add_voice_log("无人机返航", "14:18", "info")
        voice.addStretch(1)
        self.speak_back = ToggleRow("语音播报回执", "执行结果通过扬声器播报", True, "volume")
        voice.addWidget(self.speak_back)
        voice.addWidget(label("ASR 引擎 · 本地部署 · 推理 320 ms · 唤醒词「智护森林」", "caption"))
        body.addWidget(voice, 2)

        # ---------------- 中：指挥终端 ----------------
        terminal = Panel("指挥终端", "实时火场态势 · 支持自然语言指令", "chat")
        terminal.add_action(Pill("链路加密", "info"))
        self.console = Console()
        terminal.add(self.console, 1)

        quick = QHBoxLayout()
        quick.setSpacing(6)
        for text in ("态势", "返航", "喷洒", "急停"):
            quick.addWidget(button(text, "ghost", height=28, size=11,
                                   on_click=lambda _=False, t=text: self._run_command(t)))
        quick.addStretch(1)
        terminal.addLayout(quick)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        self.input = QLineEdit()
        self.input.setPlaceholderText("输入指令，例如：UGV-02 前往 B 区开挖隔离带")
        self.input.setMinimumHeight(40)
        self.input.returnPressed.connect(self._send)
        input_row.addWidget(self.input, 1)
        send = button("发送", "primary", "send", height=40, size=13, on_click=self._send)
        input_row.addWidget(send)
        terminal.addLayout(input_row)
        body.addWidget(terminal, 3)

        # ---------------- 右：预案与干预 ----------------
        right = QVBoxLayout()
        right.setSpacing(14)

        plans = Panel("预设方案", "经专家评审的标准处置流程", "shield")
        plans.add_action(Pill("3 套", "purple"))
        self._plans = [
            ("A", "空地协同压制", "4 架 UAV + 4 台 UGV，楔形推进压制主火头", theme.ACCENT, theme.ACCENT_SOFT),
            ("B", "隔离阻截", "集中 3 台 UGV 开挖隔离带，UAV 持续监测飞火", theme.BLUE, theme.BLUE_SOFT),
            ("C", "夜间看守", "低功耗值守模式，红外扫描 + 定时洒水", theme.PURPLE, theme.PURPLE_SOFT),
        ]
        for key, name, desc, color, soft in self._plans:
            plans.add(self._plan_card(key, name, desc, color, soft))
        right.addWidget(plans)

        manual = Panel("人工干预", "指挥员可随时接管自动流程", "user")
        manual.add_action(Pill("权限：指挥员", "info"))
        grid = QVBoxLayout()
        grid.setSpacing(8)
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        self.pause_btn = button("暂停全部任务", "soft", "pause", height=34,
                                on_click=self._toggle_pause)
        row1.addWidget(self.pause_btn, 1)
        row1.addWidget(button("全部返航", "soft", "home", height=34,
                              on_click=lambda: self._broadcast("全部返航")), 1)
        grid.addLayout(row1)
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        row2.addWidget(button("急停", "dangerSoft", "power", height=34,
                              on_click=lambda: self._run_command("紧急停止")), 1)
        row2.addWidget(button("恢复自动", "blue", "refresh", height=34,
                              on_click=self._resume), 1)
        grid.addLayout(row2)
        manual.addLayout(grid)
        manual.addWidget(hline())
        manual.addWidget(label("操作留痕", "muted"))
        self.trace = label("", "caption")
        self.trace.setWordWrap(True)
        manual.addWidget(self.trace)
        right.addWidget(manual)
        right.addStretch(1)
        body.addLayout(right, 2)

        self.root.addLayout(body, 1)

        self._voice_timer = QTimer(self)
        self._voice_timer.setSingleShot(True)
        self._voice_timer.timeout.connect(self._voice_result)
        self._recording = False
        self._update_trace("等待指挥员操作…")
        self.console.add("system", "指挥终端已接入火场态势链路，8 台装备在线。")
        self.console.add("system", "可用指令：返航 / 喷洒灭火剂 / 开挖隔离带 / 一键启动预案 / "
                                   "查看火场态势 / 紧急停止。")

    # ------------------------------------------------------------------
    def _plan_card(self, key: str, name: str, desc: str, color: str, soft: str) -> QWidget:
        card = QWidget()
        card.setMinimumHeight(62)
        soft_bg(card, soft, 12)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(11, 9, 11, 9)
        lay.setSpacing(9)
        key_lb = label(key, None, color=color, size=14, weight=800)
        key_lb.setFixedSize(28, 28)
        key_lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_lb.setStyleSheet(
            f"color:{color}; background:#FFFFFF; border-radius:9px; font-size:14px; font-weight:800;"
        )
        lay.addWidget(key_lb, 0, Qt.AlignmentFlag.AlignTop)
        col = QVBoxLayout()
        col.setSpacing(1)
        col.addWidget(label(name, None, size=12.5, weight=700))
        d = label(desc, "caption", color=theme.MUTED)
        d.setWordWrap(True)
        d.setMinimumHeight(28)
        col.addWidget(d)
        lay.addLayout(col, 1)
        start = button("启动", "soft", height=26, size=11,
                       on_click=lambda _=False, k=key: self._launch_plan(k))
        lay.addWidget(start, 0, Qt.AlignmentFlag.AlignTop)
        return card

    # ------------------------------------------------------------------
    def _toggle_voice(self):
        if self._recording:
            return
        self._recording = True
        self.wave.set_active(True)
        self.mic.setText("正在聆听…")
        self.recognized.setText("◉ 正在采集语音，请说出指令…")
        self.recognized.setStyleSheet(
            f"color:{theme.ACCENT_DARK}; background:{theme.ACCENT_SOFT}; border-radius:10px;"
            f" padding:10px; font-size:12px;"
        )
        self._voice_timer.start(1600)

    def _voice_result(self):
        self.wave.set_active(False)
        self._recording = False
        self.mic.setText("按住说话")
        text = random.choice(EXAMPLES)
        self.recognized.setText(f"「{text}」")
        self.recognized.setStyleSheet(
            f"color:{theme.TEXT}; background:{theme.SURFACE_ALT}; border-radius:10px;"
            f" padding:10px; font-size:12px;"
        )
        self.console.add("user", f"（语音）{text}", "user")
        self._dispatch(text)

    def _voice_once(self):
        self._toggle_voice()

    def _send(self):
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self.console.add("user", text, "user")
        self._dispatch(text)

    def _run_command(self, text: str):
        self.console.add("user", text, "user")
        self._dispatch(text)

    def _add_voice_log(self, text: str, time: str, kind: str):
        row = QWidget()
        lay = QHBoxLayout(row)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(7)
        color, _ = theme.SEVERITY.get(kind, theme.SEVERITY["info"])
        dot = label("●", None, color=color, size=8)
        lay.addWidget(dot)
        lay.addWidget(label(text, "caption", color=theme.TEXT_SOFT), 1)
        lay.addWidget(label(time, "caption", color=theme.MUTED_LIGHT))
        self.voice_log.addWidget(row)

    def _dispatch(self, text: str):
        e = self.engine
        if any(k in text for k in ("返航", "回家")):
            reply = "已向 2 台装备下发返航指令，正在规划安全空域航路。"
            e.return_robot(e.robots[0])
            e.return_robot(e.robots[1])
            e.push_event("指挥员语音指令：无人机编队返航", "info")
            kind = "ok"
        elif any(k in text for k in ("急停", "停止", "中止")):
            e.estop = True
            reply = "E-STOP 已触发，全部装备立即制动，等待现场确认后恢复。"
            e.push_event("指挥终端执行紧急停止", "critical")
            e.push_alert("紧急停止已执行", "8 台装备制动，任务挂起", "critical", "指挥终端")
            kind = "alert"
        elif any(k in text for k in ("喷洒", "灭火剂", "洒水")):
            reply = "UGV-01 / UGV-02 已切换至喷洒模式，按 45% 水 + 35% 泡沫比例执行。"
            e.push_event("喷洒灭火剂指令已下发至地面编队", "success")
            kind = "ok"
        elif any(k in text for k in ("隔离带", "开挖")):
            reply = "UGV-02 已接受隔离带开挖任务，目标宽度 8 m，预计 18 分钟完成。"
            e.push_event("隔离带开挖任务已派发（UGV-02）", "info")
            kind = "ok"
        elif any(k in text for k in ("预案", "一键")):
            key = "A" if "A" not in text else text[text.find("A")]
            self.console.add("system", f"正在加载预设方案 {key}…", "system")
            reply = "预设方案已加载，8 台装备进入预定阵位，进入执行状态。"
            e.push_event(f"预设方案 {key} 已启动", "success")
            kind = "ok"
        elif any(k in text for k in ("态势", "状态", "情况")):
            risk_level, _ = e.risk_level()
            reply = (f"当前火险指数 {e.risk:.0f}（{risk_level}），过火面积 {e.fire_area:.1f} ha，"
                     f"控制率 {e.containment:.1f}%，8 台装备在线，链路时延 42 ms。")
            kind = "system"
        elif any(k in text for k in ("恢复", "继续")):
            e.estop = False
            e.paused = False
            reply = "已解除急停并恢复自动流程，装备重新进入任务队列。"
            e.push_event("系统恢复自动流程", "success")
            kind = "ok"
        else:
            reply = ("未匹配到标准指令，可尝试：返航 / 喷洒灭火剂 / 开挖隔离带 / "
                     "一键启动预案 / 查看火场态势 / 紧急停止。")
            kind = "system"
        self.console.add("system", reply, kind)
        self._update_trace(f"{datetime.now().strftime('%H:%M:%S')} 指令「{text}」已执行，回执已记录")
        toast(self, "指令已执行", "success" if kind != "alert" else "warning")

    def _update_trace(self, text: str):
        self.trace.setText(text)

    def _launch_plan(self, key: str):
        target = next((p for p in self._plans if p[0] == key), None)
        if not target:
            return
        Dialog(
            self, f"启动预设方案 {key} · {target[1]}",
            f"{target[2]}。确认后将同步调度空中与地面单元，是否继续？",
            kind="warning", confirm_text="启动方案",
            on_confirm=lambda: self._plan_started(key, target[1]),
        ).exec()

    def _plan_started(self, key: str, name: str):
        self.console.add("user", f"一键启动预案 {key}", "user")
        self.console.add("system", f"预设方案 {key}「{name}」已启动，装备开始机动。", "ok")
        self.engine.push_event(f"预设方案 {key}「{name}」启动，编队开始机动", "success")
        self._update_trace(f"{datetime.now().strftime('%H:%M:%S')} 启动预设方案 {key}（{name}）")
        toast(self, f"预设方案 {key} 已启动")

    def _toggle_pause(self):
        paused = not self.engine.paused
        self.engine.paused = paused
        self.pause_btn.setText("恢复全部任务" if paused else "暂停全部任务")
        self.console.add("system", "全部任务已暂停，等待指挥员恢复。" if paused
                         else "全部任务已恢复执行。", "system")
        self.engine.push_event("指挥员暂停全部任务" if paused else "指挥员恢复全部任务", "warning" if paused else "success")
        toast(self, "已暂停全部任务" if paused else "已恢复全部任务", "warning" if paused else "success")

    def _resume(self):
        self.engine.estop = False
        self.engine.paused = False
        self.pause_btn.setText("暂停全部任务")
        self.console.add("system", "急停解除，系统恢复自动流程。", "ok")
        toast(self, "已恢复自动流程")

    def _broadcast(self, text: str):
        self.console.add("user", text, "user")
        self.console.add("system", "已广播至全部在线装备，返航航路已生成。", "ok")
        self.engine.push_event(f"广播指令：{text}，全部装备确认收到", "info")
        toast(self, "广播指令已下发")
