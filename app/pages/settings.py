"""系统设置页。"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .. import config, icons, theme
from ..simulation import SimEngine
from ..widgets import (
    Avatar,
    KeyValueRow,
    Pill,
    ToggleRow,
    button,
    label,
    toast,
)
from .base import Page, Panel, ScrollPage, hline, kv_chip


class SettingsPage(ScrollPage):
    logout_requested = Signal()

    def __init__(self, engine: SimEngine, user: str = "admin", parent=None):
        super().__init__(
            engine,
            "系统设置",
            "界面外观 · 数据链路 · 告警阈值 · AI 模型与系统集成",
        )
        self.user = user
        self._cfg_data = config.load()
        self.add_action(Pill("配置已同步", "success"))
        self.add_action(button("保存配置", "primary", "check", height=34, on_click=self._save))

        top = QHBoxLayout()
        top.setSpacing(14)

        # 外观
        look = Panel("界面外观", "亮色森林主题 · 高对比度组件", "sparkles")
        look.add_action(Pill("亮色", "success"))
        swatch_row = QHBoxLayout()
        swatch_row.setSpacing(8)
        for name, (color, _dark, _light, _soft, _soft2) in theme.PALETTES.items():
            active = name == self._cfg_data.get("accent", theme.ACCENT_NAME)
            sw = QWidget()
            sw.setCursor(Qt.CursorShape.PointingHandCursor)
            sw_lay = QVBoxLayout(sw)
            sw_lay.setContentsMargins(0, 0, 0, 0)
            sw_lay.setSpacing(4)
            dot = QLabel()
            dot.setFixedSize(46, 30)
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setStyleSheet(f"background:{color}; border-radius:9px;")
            if active:
                dot.setPixmap(icons.pixmap("check", "#FFFFFF", 16))
            sw_lay.addWidget(dot, 0, Qt.AlignmentFlag.AlignHCenter)
            sw_lay.addWidget(label(name, "caption"), 0, Qt.AlignmentFlag.AlignHCenter)
            dot.mousePressEvent = lambda _e, n=name: self._pick_accent(n)
            swatch_row.addWidget(sw, 1)
        look.addLayout(swatch_row)
        look.addWidget(hline())
        self.dense = ToggleRow("紧凑信息密度", "收窄卡片留白，同一屏展示更多内容",
                               bool(self._cfg_data.get("compact")), "layers")
        self.dense.toggled.connect(self._on_dense)
        look.addWidget(self.dense)
        self.anim_row = ToggleRow("启用界面动效", "地图与图表平滑过渡",
                                  bool(self._cfg_data.get("animations")), "activity")
        self.anim_row.toggled.connect(self._on_animations)
        look.addWidget(self.anim_row)
        top.addWidget(look, 1)

        # 数据与刷新
        data = Panel("数据与刷新", "仿真引擎 / 真实链路可切换", "refresh")
        data.add_action(Pill("仿真数据", "info"))
        freq_row = QHBoxLayout()
        freq_row.addWidget(label("态势刷新频率", "muted"))
        freq_row.addStretch(1)
        self.freq = QComboBox()
        self.freq.addItems(["1 秒", "2 秒", "5 秒"])
        self.freq.setCurrentIndex({1: 0, 2: 1, 5: 2}.get(int(self._cfg_data.get("refresh", 1)), 0))
        self.freq.setFixedWidth(110)
        self.freq.currentIndexChanged.connect(self._on_freq)
        freq_row.addWidget(self.freq)
        data.addLayout(freq_row)
        self.real_link = ToggleRow("接入真实飞控链路", "连接 MAVLink / ROS2 话题", False, "link")
        self.real_link.toggled.connect(
            lambda on: self._announce("真实飞控链路已接入，MAVLink 心跳正常" if on
                                      else "已切回仿真数据源"))
        data.addWidget(self.real_link)
        self.stream_row = ToggleRow("火场视频流接入", "RTSP 多路视频解码",
                                    bool(self._cfg_data.get("stream", True)), "camera")
        self.stream_row.toggled.connect(self._on_stream)
        data.addWidget(self.stream_row)
        data.addWidget(hline())
        data.addWidget(KeyValueRow("数据延迟", "38 ms"))
        data.addWidget(KeyValueRow("今日入库", "12,846 条"))
        top.addWidget(data, 1)
        self.content.addLayout(top)

        mid = QHBoxLayout()
        mid.setSpacing(14)

        # 告警阈值
        alarms = Panel("告警阈值", "超限自动触发语音播报与推送", "bell")
        self._thresholds = {}
        for name, default, maximum, suffix in (("地表温度", 65, 100, " ℃"),
                                               ("烟雾浓度", 180, 500, " μg/m³"),
                                               ("火险指数", 80, 100, "")):
            alarms.addWidget(self._threshold_row(name, default, maximum, suffix))
        alarms.addWidget(hline())
        self.silent_row = ToggleRow("夜间静默模式", "22:00–06:00 仅保留紧急告警",
                                    bool(self._cfg_data.get("silent", False)), "clock")
        self.silent_row.toggled.connect(self._on_silent)
        alarms.addWidget(self.silent_row)
        mid.addWidget(alarms, 1)

        # AI 模型
        models = Panel("AI 模型", "本机推理 · 支持在线更新", "cpu")
        models.add_action(Pill("全部就绪", "success"))
        for name, ver, desc in (
            ("YOLO-Fire", "v3.2", "明火 / 烟雾 / 正常识别，mAP 0.921"),
            ("BayesSpread", "v2.1", "火势蔓延方向概率推演"),
            ("PPO-Forest", "v1.4", "路径规划强化学习策略"),
            ("Auction-MAS", "v1.0", "拍卖机制任务分配"),
        ):
            row = QWidget()
            lay = QHBoxLayout(row)
            lay.setContentsMargins(0, 5, 0, 5)
            lay.setSpacing(8)
            lay.addWidget(label(name, None, size=12.5, weight=700))
            lay.addWidget(label(ver, "caption"))
            lay.addStretch(1)
            lay.addWidget(label(desc, "caption", color=theme.MUTED_LIGHT))
            models.addWidget(row)
        models.addWidget(hline())
        row = QHBoxLayout()
        row.addWidget(label("模型更新时间", "caption"))
        row.addStretch(1)
        row.addWidget(label("2026-11-18 22:40", "caption"))
        models.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(button("检查更新", "soft", "download", height=32,
                              on_click=self._check_update), 1)
        row2.addWidget(button("重新加载模型", "blue", "refresh", height=32,
                              on_click=self._reload_models), 1)
        models.addLayout(row2)
        mid.addWidget(models, 1)
        self.content.addLayout(mid)

        bottom = QHBoxLayout()
        bottom.setSpacing(14)

        # 账号
        account = Panel("操作员账户", "指挥终端权限与安全", "user")
        head = QHBoxLayout()
        head.setSpacing(10)
        head.addWidget(Avatar(self.user, 40))
        col = QVBoxLayout()
        col.setSpacing(0)
        col.addWidget(label(self.user, None, size=14, weight=700))
        col.addWidget(label("森林防火指挥员 · 三级权限", "caption"))
        head.addLayout(col)
        head.addStretch(1)
        head.addWidget(Pill("在线", "success"))
        account.addLayout(head)
        account.addWidget(hline())
        account.addWidget(KeyValueRow("上次登录", "2026-11-19 08:42"))
        account.addWidget(KeyValueRow("登录终端", "指挥中心 A 席"))
        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(button("修改密码", "soft", "lock", height=32,
                                 on_click=self._reset_password), 1)
        actions.addWidget(button("退出登录", "dangerSoft", "logout", height=32,
                                 on_click=self._logout), 1)
        account.addLayout(actions)
        bottom.addWidget(account, 1)

        # 集成
        integ = Panel("系统集成", "外部平台接口状态", "link")
        self.integ_pill = Pill("4/4 已连接", "success")
        integ.add_action(self.integ_pill)
        self._integ_toggles = []
        for name, desc, checked, icon in (
            ("林业 GIS 平台", "林班边界与地形数据", True, "map"),
            ("气象服务", "风速 / 湿度 / 降雨预报", True, "wind"),
            ("消防指挥平台", "119 联动与力量调度", True, "shield"),
            ("视频汇聚平台", "GB28181 视频接入", True, "camera"),
        ):
            row = ToggleRow(name, desc, checked, icon)
            row.toggled.connect(self._on_integration)
            self._integ_toggles.append(row)
            integ.addWidget(row)
        bottom.addWidget(integ, 1)
        self.content.addLayout(bottom)

        info = Panel("系统信息", "ForestGuard AI v2.0", "info")
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(6)
        from PySide6.QtCore import qVersion

        for i, (k, v) in enumerate((("软件版本", "ForestGuard AI v2.0.0"),
                                    ("界面框架", f"PySide6 / Qt {qVersion()}"),
                                    ("运行平台", "Windows / Linux 桌面端"),
                                    ("授权状态", "演示授权 · 2026-12-31 到期"))):
            grid.addWidget(KeyValueRow(k, v), i // 2, i % 2)
        info.addLayout(grid)
        self.content.addWidget(info)
        self.content.addStretch(1)

    # ------------------------------------------------------------------
    def _threshold_row(self, name: str, value: int, maximum: int, suffix: str) -> QWidget:
        row = QWidget()
        lay = QVBoxLayout(row)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(1)
        head = QHBoxLayout()
        head.addWidget(label(name, "muted"))
        head.addStretch(1)
        val = label(f"{value}{suffix}", None, size=11.5, weight=700)
        head.addWidget(val)
        lay.addLayout(head)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, maximum)
        slider.setValue(int(self._cfg_data.get(
            {"地表温度": "th_temp", "烟雾浓度": "th_smoke", "火险指数": "th_risk"}.get(name, "th_temp"), value)))
        slider.valueChanged.connect(
            lambda v, l=val, sfx=suffix, n=name: (l.setText(f"{v}{sfx}"), self._on_threshold(n, v)))
        lay.addWidget(slider)
        self._thresholds[name] = slider
        return row

    def _on_freq(self, index: int):
        interval = [1000, 2000, 5000][index]
        self.engine.timer.setInterval(interval)
        self._cfg_data["refresh"] = interval // 1000
        toast(self, f"态势刷新频率已调整为 {interval // 1000} 秒")

    # ---------------- 外观 ----------------
    def _window(self):
        win = self.window()
        return win if hasattr(win, "apply_preferences") else None

    def _pick_accent(self, name: str):
        if name == theme.ACCENT_NAME:
            toast(self, f"当前已是「{name}」主题", "info")
            return
        self._cfg_data["accent"] = name
        config.save(self._cfg_data)
        self.engine.push_event(f"界面主题色切换为「{name}」", "info")
        toast(self, f"主题色已切换为「{name}」")
        if not self._apply_preferences():
            theme.set_accent(name)
            theme.apply_theme(QApplication.instance())

    def _apply_preferences(self) -> bool:
        win = self._window()
        if win is None:
            return False
        win.apply_preferences()
        return True

    def _on_dense(self, on: bool):
        self._cfg_data["compact"] = on
        config.save(self._cfg_data)
        if not self._apply_preferences():
            theme.set_density(on)
            theme.apply_theme(QApplication.instance())
        toast(self, "已切换到紧凑布局" if on else "已恢复标准布局")

    def _on_animations(self, on: bool):
        self._cfg_data["animations"] = on
        config.save(self._cfg_data)
        theme.ANIMATIONS = on
        theme.apply_theme(QApplication.instance())
        toast(self, "界面动效已开启" if on else "界面动效已关闭")

    def _on_stream(self, on: bool):
        self._cfg_data["stream"] = on
        config.save(self._cfg_data)
        self.engine.push_event("火场视频流已接入 RTSP 通道" if on else "火场视频流已断开", "info")
        toast(self, "视频流已接入" if on else "视频流已断开", "success" if on else "info")

    def _on_silent(self, on: bool):
        self.engine.silent = on
        self._cfg_data["silent"] = on
        config.save(self._cfg_data)
        toast(self, "夜间静默模式已开启，仅推送紧急告警" if on else "静默模式已关闭", "info")

    def _on_threshold(self, name: str, value: int):
        key = {"地表温度": "th_temp", "烟雾浓度": "th_smoke", "火险指数": "th_risk"}.get(name)
        if not key:
            return
        self._cfg_data[key] = value
        setattr(self.engine, key, float(value))

    def _on_integration(self, _on: bool):
        total = len(self._integ_toggles)
        active = sum(1 for row in self._integ_toggles if row.switch.isChecked())
        self.integ_pill.set_text(f"{active}/{total} 已连接")
        self.integ_pill.set_kind("success" if active == total else "warning")

    def _announce(self, text: str):
        self.engine.push_event(text, "info")
        toast(self, text, "info")

    def _check_update(self):
        toast(self, "正在检查模型更新…", "info")
        QTimer.singleShot(1100, lambda: (
            self.engine.push_event("模型检查完成：YOLO-Fire v3.2 已是最新", "success"),
            toast(self, "已是最新版本（v3.2）")))

    def _reload_models(self):
        toast(self, "推理服务已重新加载，4 个模型就绪", "success")
        self.engine.push_event("AI 推理服务重新加载完成", "success")

    def _reset_password(self):
        toast(self, "验证码已发送至绑定终端", "info")
        self.engine.push_event(f"操作员 {self.user} 申请重置密码", "warning")

    def _save(self):
        config.save(self._cfg_data)
        self.engine.push_event("系统配置已保存并同步至各终端", "success")
        toast(self, "配置已保存")

    def _logout(self):
        self.logout_requested.emit()
