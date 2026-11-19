"""系统设置页。"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .. import icons, theme
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
        self.add_action(Pill("配置已同步", "success"))
        self.add_action(button("保存配置", "primary", "check", height=34, on_click=self._save))

        top = QHBoxLayout()
        top.setSpacing(14)

        # 外观
        look = Panel("界面外观", "亮色森林主题 · 高对比度组件", "sparkles")
        look.add_action(Pill("亮色", "success"))
        swatch_row = QHBoxLayout()
        swatch_row.setSpacing(8)
        for name, color, active in (("森林绿", theme.ACCENT, True),
                                    ("天空蓝", theme.BLUE, False),
                                    ("琥珀橙", theme.AMBER, False),
                                    ("薰衣草", theme.PURPLE, False)):
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
            dot.mousePressEvent = lambda _e, n=name: toast(self, f"主题色「{n}」已记录，重启后生效", "info")
            swatch_row.addWidget(sw, 1)
        look.addLayout(swatch_row)
        look.addWidget(hline())
        self.dense = ToggleRow("紧凑信息密度", "同一屏展示更多卡片内容", False, "layers")
        look.addWidget(self.dense)
        look.addWidget(ToggleRow("启用界面动效", "地图与图表平滑过渡", True, "activity"))
        top.addWidget(look, 1)

        # 数据与刷新
        data = Panel("数据与刷新", "仿真引擎 / 真实链路可切换", "refresh")
        data.add_action(Pill("仿真数据", "info"))
        freq_row = QHBoxLayout()
        freq_row.addWidget(label("态势刷新频率", "muted"))
        freq_row.addStretch(1)
        self.freq = QComboBox()
        self.freq.addItems(["1 秒", "2 秒", "5 秒"])
        self.freq.setCurrentIndex(0)
        self.freq.setFixedWidth(110)
        self.freq.currentIndexChanged.connect(self._on_freq)
        freq_row.addWidget(self.freq)
        data.addLayout(freq_row)
        data.addWidget(ToggleRow("接入真实飞控链路", "连接 MAVLink / ROS2 话题", False, "link"))
        data.addWidget(ToggleRow("火场视频流接入", "RTSP 多路视频解码", True, "camera"))
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
        alarms.addWidget(ToggleRow("夜间静默模式", "22:00–06:00 仅保留紧急告警", True, "clock"))
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
                              on_click=lambda: toast(self, "已是最新版本（v3.2）")), 1)
        row2.addWidget(button("重新加载模型", "blue", "refresh", height=32,
                              on_click=lambda: toast(self, "推理服务已重新加载")), 1)
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
                                 on_click=lambda: toast(self, "已发送密码重置验证码", "info")), 1)
        actions.addWidget(button("退出登录", "dangerSoft", "logout", height=32,
                                 on_click=self._logout), 1)
        account.addLayout(actions)
        bottom.addWidget(account, 1)

        # 集成
        integ = Panel("系统集成", "外部平台接口状态", "link")
        integ.add_action(Pill("4/4 已连接", "success"))
        for name, desc, checked, icon in (
            ("林业 GIS 平台", "林班边界与地形数据", True, "map"),
            ("气象服务", "风速 / 湿度 / 降雨预报", True, "wind"),
            ("消防指挥平台", "119 联动与力量调度", True, "shield"),
            ("视频汇聚平台", "GB28181 视频接入", True, "camera"),
        ):
            integ.addWidget(ToggleRow(name, desc, checked, icon))
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
        slider.setValue(value)
        slider.valueChanged.connect(lambda v, l=val, s=suffix: l.setText(f"{v}{s}"))
        lay.addWidget(slider)
        self._thresholds[name] = slider
        return row

    def _on_freq(self, index: int):
        interval = [1000, 2000, 5000][index]
        self.engine.timer.setInterval(interval)
        toast(self, f"态势刷新频率已调整为 {interval // 1000} 秒")

    def _save(self):
        self.engine.push_event("系统配置已保存并同步至各终端", "success")
        toast(self, "配置已保存")

    def _logout(self):
        self.logout_requested.emit()
