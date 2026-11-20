"""火情态势地图页（含在线底图能力）。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
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
    SearchBox,
    ToggleSwitch,
    button,
    label,
    toast,
)
from .base import EventList, Panel, ScrollPage, alert_row, kv_chip


class MapPage(ScrollPage):
    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(
            engine,
            "火情态势地图",
            "SLAM 融合底图 · 热成像火点 · 多机位置实时标定",
        )
        self.add_action(Pill("底图已同步", "success"))
        self.add_action(button("在线卫星底图", "soft", "satellite", height=34,
                               on_click=self._open_web_map))
        self.add_action(button("定位火点", "primary", "target", height=34,
                               on_click=self._locate_fire))

        body = QHBoxLayout()
        body.setSpacing(14)

        left = QVBoxLayout()
        left.setSpacing(10)

        toolbar = QWidget()
        toolbar.setObjectName("MapToolbar")
        toolbar.setStyleSheet(
            f"#MapToolbar {{ background:{theme.SURFACE}; border:1px solid {theme.BORDER};"
            f" border-radius:14px; }}"
        )
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(12, 8, 12, 8)
        tb.setSpacing(10)
        self.search = SearchBox("搜索林班 / 坐标 / 火点编号", width=250)
        tb.addWidget(self.search)
        tb.addWidget(kv_chip("layers", "图层 4"))
        tb.addWidget(kv_chip("clock", "刷新 5s"))
        tb.addStretch(1)
        self.layer_heat = ToggleSwitch(True)
        self.layer_heat.setToolTip("热力预测图层")
        tb.addWidget(label("热力预测", "caption"))
        tb.addWidget(self.layer_heat)
        self.layer_robots = ToggleSwitch(True)
        tb.addWidget(label("装备", "caption"))
        tb.addWidget(self.layer_robots)
        left.addWidget(toolbar)

        map_panel = Panel("林区电子地图", "离线矢量底图 · 支持在线影像切换", "map")
        map_panel.add_action(kv_chip("wind", engine.wind_label(), theme.BLUE, theme.BLUE_SOFT))
        self.map = TerrainMap(engine, "analysis")
        self.map.setMinimumHeight(430)
        map_panel.add(self.map, 1)
        footer = QHBoxLayout()
        footer.setSpacing(8)
        footer.addWidget(kv_chip("compass", "北纬 29°42′18″ / 东经 106°18′04″"))
        footer.addWidget(kv_chip("flame", f"火点 3 处 · 过火 {engine.fire_area:.1f} ha", theme.RED, theme.RED_SOFT))
        footer.addStretch(1)
        footer.addWidget(label("地图精度 0.08 m", "caption"))
        map_panel.addLayout(footer)
        left.addWidget(map_panel, 1)
        body.addLayout(left, 3)

        # 右栏
        right = QVBoxLayout()
        right.setSpacing(14)

        weather = Panel("林区气象", "地面站 07 · 更新于 1 分钟前", "wind")
        weather.add_action(Pill("干燥", "warning"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(8)
        self.kv_temp = KeyValueRow("温度", f"{engine.temperature:.1f} ℃", icon_name="thermo")
        self.kv_hum = KeyValueRow("湿度", f"{engine.humidity:.0f} %", icon_name="drop")
        self.kv_wind = KeyValueRow("风速", f"{engine.wind_speed:.1f} m/s", icon_name="wind")
        self.kv_dir = KeyValueRow("风向", "西南 228°", icon_name="compass")
        self.kv_rain = KeyValueRow("降雨", "0.0 mm", icon_name="rain")
        self.kv_press = KeyValueRow("气压", "1006 hPa", icon_name="activity")
        for i, kv in enumerate((self.kv_temp, self.kv_hum, self.kv_wind,
                                self.kv_dir, self.kv_rain, self.kv_press)):
            grid.addWidget(kv, i // 2, i % 2)
        weather.addLayout(grid)
        weather.addWidget(hline_row())
        weather.addWidget(label("林火行为推演", "muted"))
        self.spread_bar = ProgressLine("蔓延速度", 58, theme.RED, suffix=" m/min")
        self.flame_bar = ProgressLine("火焰长度", 44, theme.AMBER, suffix=" m")
        self.heat_bar = ProgressLine("热释放", 71, theme.AMBER, suffix=" MW")
        weather.addWidget(self.spread_bar)
        weather.addWidget(self.flame_bar)
        weather.addWidget(self.heat_bar)
        right.addWidget(weather)

        sensors = Panel("监测站点", "6 个地面站 · 2 个中继", "signal")
        self.sensor_rows = QVBoxLayout()
        self.sensor_rows.setSpacing(0)
        sensors.addLayout(self.sensor_rows)
        right.addWidget(sensors)

        alerts = Panel("区域告警", "近 30 分钟", "bell")
        alerts.add_action(button("全部", "ghost", height=26, size=11,
                                 on_click=lambda: toast(self, "已展开全部 12 条告警")))
        self.alert_box = QVBoxLayout()
        self.alert_box.setSpacing(0)
        alerts.addLayout(self.alert_box)
        right.addWidget(alerts, 1)
        body.addLayout(right, 2)
        self.root.addLayout(body, 1)

        self.layer_heat.toggled.connect(self.map.set_heat_visible)
        self.layer_robots.toggled.connect(self.map.set_robots_visible)
        engine.tick.connect(self._refresh)
        self._refresh()
        self._fill_sensors()
        self._fill_alerts()

    # ------------------------------------------------------------------
    def _fill_sensors(self):
        stations = [
            ("地面站 07", "东北坡 · 在线", "success", 96),
            ("地面站 03", "西侧防火道 · 在线", "success", 88),
            ("中继站 R2", "山脊高点 · 在线", "info", 74),
            ("地面站 11", "南线 · 低电量", "warning", 32),
        ]
        for name, desc, kind, level in stations:
            row = QWidget()
            lay = QHBoxLayout(row)
            lay.setContentsMargins(0, 4, 0, 4)
            lay.setSpacing(8)
            dot = label("●", None, color=theme.SEVERITY[kind][0], size=10)
            lay.addWidget(dot)
            col = QVBoxLayout()
            col.setSpacing(0)
            col.addWidget(label(name, None, size=12, weight=700))
            col.addWidget(label(desc, "caption"))
            lay.addLayout(col)
            lay.addStretch(1)
            lay.addWidget(label(f"{level}%", "caption", color=theme.MUTED))
            self.sensor_rows.addWidget(row)

    def _fill_alerts(self):
        while self.alert_box.count():
            item = self.alert_box.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for alert in self.engine.alerts[:3]:
            self.alert_box.addWidget(alert_row(alert, compact=True))

    def _refresh(self):
        e = self.engine
        self.kv_temp.set_value(f"{e.temperature:.1f} ℃")
        self.kv_hum.set_value(f"{e.humidity:.0f} %")
        self.kv_wind.set_value(f"{e.wind_speed:.1f} m/s")
        self.kv_dir.set_value(f"{e.wind_label().split(' ')[0]} {e.wind_deg:.0f}°")
        self.spread_bar.set_value(min(100, e.wind_speed / 9 * 100))
        self.flame_bar.set_value(min(100, e.temperature - 18))
        self.heat_bar.set_value(min(100, e.fire_area * 5.2))
        self.map.set_minutes(30)

    # ------------------------------------------------------------------
    def _locate_fire(self):
        self.map.set_center_fire()
        toast(self, "已定位至火点 A-03，热成像通道已锁定")
        self.engine.push_event("指挥终端定位火点 A-03，多机视角同步", "info")

    def _open_web_map(self):
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
        except Exception:
            toast(self, "当前环境未安装 QtWebEngine，已保持离线矢量底图", "warning")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("在线卫星底图")
        dlg.resize(1000, 650)
        dlg.setStyleSheet(f"QDialog {{ background:{theme.SURFACE}; }}")
        lay = QVBoxLayout(dlg)
        view = QWebEngineView()
        view.setUrl("https://map.baidu.com/")
        lay.addWidget(view)
        dlg.exec()


def hline_row():
    from PySide6.QtWidgets import QFrame

    line = QFrame()
    line.setObjectName("Divider")
    line.setFixedHeight(1)
    return line
