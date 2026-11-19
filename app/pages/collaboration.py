"""多机器人协作页（对应系统设计 2.2）。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import icons, theme
from ..canvas import FormationView, LinkDiagram
from ..simulation import SimEngine
from ..widgets import (
    Pill,
    ProgressLine,
    StatCard,
    button,
    label as mk_label,
    toast,
)
from ..widgets import label
from .base import EventList, Panel, ScrollPage, hline, kv_chip


PRIORITY_KIND = {"紧急": "critical", "高": "warning", "中": "info"}


class CollaborationPage(ScrollPage):
    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(
            engine,
            "多机器人协作",
            "拍卖机制任务分配 · 空地联动闭环 · 分布式协商消解路径冲突",
        )
        self.add_action(Pill("MAS 协作在线", "success"))
        self.add_action(button("自动分配", "soft", "sparkles", height=34, on_click=self._auto_allocate))
        self.add_action(button("发起拍卖", "primary", "users", height=34, on_click=self._auction))

        self._build_stats()

        body = QHBoxLayout()
        body.setSpacing(14)

        # ---------------- 左：拍卖 + 协商 ----------------
        left = QVBoxLayout()
        left.setSpacing(14)

        auction = Panel("拍卖式任务分配", "分布式竞价 · 按位置/负载/能力动态派单", "users")
        auction.add_action(Pill("第 17 轮", "purple"))
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["任务", "区域 / 面积", "优先级", "收益", "中标单元", "状态"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFixedHeight(232)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        auction.add(self.table)
        hint = QHBoxLayout()
        hint.addWidget(label("中标收益 = 报价 × 能力匹配 + 电量权重 − 距离惩罚", "caption"))
        hint.addStretch(1)
        self.auction_state = label("等待发起下一轮拍卖", "caption", color=theme.MUTED)
        hint.addWidget(self.auction_state)
        auction.addLayout(hint)
        left.addWidget(auction, 1)

        negotiate = Panel("分布式协商 · 路径冲突消解", "基于优先级的让行协商，避免机间冲突", "link")
        negotiate.add_action(Pill("冲突 2", "warning"))
        self.neg_log = EventList(engine.events[:3], limit=4)
        negotiate.add(self.neg_log)
        negotiate.content.addStretch(1)
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(kv_chip("signal", "通信时延 42 ms"))
        row.addWidget(kv_chip("shield", "冲突消解率 100%"))
        row.addStretch(1)
        row.addWidget(button("查看协商拓扑", "ghost", height=28, size=11,
                             on_click=lambda: toast(self, "已生成 8 节点协商拓扑图")))
        negotiate.addLayout(row)
        left.addWidget(negotiate, 1)
        body.addLayout(left, 3)

        # ---------------- 右：联动 + 编队 ----------------
        right = QVBoxLayout()
        right.setSpacing(14)

        linkage = Panel("空中—地面联动", "「侦察—打击」闭环 · 秒级目标级联", "drone")
        linkage.add_action(Pill("链路正常", "success"))
        self.link_view = LinkDiagram(engine)
        self.link_view.setMinimumHeight(188)
        linkage.add(self.link_view, 1)
        flow = QHBoxLayout()
        flow.setSpacing(6)
        for i, (text, color) in enumerate((("无人机侦察", theme.BLUE),
                                           ("火源定位", theme.AMBER),
                                           ("任务下发", theme.PURPLE),
                                           ("地面扑打", theme.ACCENT))):
            chip = mk_label(text, None, color=color, size=11, weight=700)
            chip.setStyleSheet(
                f"color:{color}; background:{theme.SURFACE_ALT}; border-radius:8px;"
                f" padding:4px 8px; font-size:11px; font-weight:700;"
            )
            flow.addWidget(chip)
            if i < 3:
                arrow = mk_label("→", None, color=theme.MUTED_LIGHT, size=11)
                flow.addWidget(arrow)
        linkage.addLayout(flow)
        right.addWidget(linkage, 3)

        formation = Panel("灭火编队阵列", "多机同步推进，扩大覆盖面积", "robot")
        self.formation_combo = QComboBox()
        self.formation_combo.addItems(["楔形推进", "线性阵列", "弧形包围"])
        self.formation_combo.setFixedWidth(120)
        self.formation_combo.currentTextChanged.connect(self._on_formation)
        formation.add_action(self.formation_combo)
        self.formation_view = FormationView(engine)
        self.formation_view.setMinimumHeight(158)
        formation.add(self.formation_view, 1)
        self.coverage_bar = ProgressLine("覆盖面积", 36, theme.ACCENT, suffix=" %")
        self.coverage_bar.setToolTip("相对目标覆盖面积 10 ha")
        self.coverage_bar.setFixedHeight(26)
        formation.add(self.coverage_bar)
        self.coverage_label = label("", "caption")
        formation.add(self.coverage_label)
        right.addWidget(formation, 2)
        body.addLayout(right, 2)

        self.root.addLayout(body, 1)

        engine.tick.connect(self._refresh)
        self._fill_table()
        self._refresh()

    # ------------------------------------------------------------------
    def _build_stats(self):
        row = QHBoxLayout()
        row.setSpacing(14)
        self.s_online = StatCard("在线装备", "8", "台", "robot", theme.ACCENT, theme.ACCENT_SOFT,
                                 "100%", "flat", [6, 7, 7, 8, 8, 8, 8])
        self.s_tasks = StatCard("任务队列", "5", "项", "layers", theme.BLUE, theme.BLUE_SOFT,
                                "2 待分配", "flat", [3, 4, 5, 4, 6, 5, 5])
        self.s_rounds = StatCard("拍卖轮次", "17", "轮", "users", theme.PURPLE, theme.PURPLE_SOFT,
                                 "本轮 0.8s", "flat", [8, 9, 11, 12, 14, 15, 17])
        self.s_conflict = StatCard("协商冲突", "2", "次", "link", theme.AMBER, theme.AMBER_SOFT,
                                   "全部消解", "flat", [5, 4, 4, 3, 3, 2, 2])
        for c in (self.s_online, self.s_tasks, self.s_rounds, self.s_conflict):
            c.setFixedHeight(92)
            row.addWidget(c, 1)
        self.root.addLayout(row)

    def _fill_table(self):
        tasks = self.engine.tasks
        self.table.setRowCount(len(tasks))
        for i, t in enumerate(tasks):
            self.table.setItem(i, 0, QTableWidgetItem(f"{t['id']}  {t['name']}"))
            self.table.setItem(i, 1, QTableWidgetItem(t["pos"]))
            pri = QTableWidgetItem(t["priority"])
            color, _ = theme.SEVERITY[PRIORITY_KIND.get(t["priority"], "info")]
            pri.setForeground(QColor(color))
            self.table.setItem(i, 2, pri)
            self.table.setItem(i, 3, QTableWidgetItem(f"{t['reward']}"))
            self.table.setItem(i, 4, QTableWidgetItem(t["robot"]))
            self.table.setItem(i, 5, QTableWidgetItem(t["status"]))
            self.table.setRowHeight(i, 38)

    def _auction(self):
        pending = [i for i, t in enumerate(self.engine.tasks) if t["status"] in ("待分配", "已派发")]
        if not pending:
            toast(self, "当前没有待拍卖任务，可先下发新任务", "info")
            return
        idx = pending[0]
        best = self.engine.run_auction(idx)
        self._fill_table()
        self.auction_state.setText(f"{self.engine.tasks[idx]['id']} 由 {best.id} 中标 · 耗时 0.8 s")
        self.neg_log.set_events(self.engine.events[:4])
        toast(self, f"任务「{self.engine.tasks[idx]['name']}」由 {best.id} 中标")

    def _auto_allocate(self):
        count = 0
        for i, t in enumerate(self.engine.tasks):
            if t["status"] == "待分配":
                self.engine.run_auction(i)
                count += 1
        self._fill_table()
        self.neg_log.set_events(self.engine.events[:4])
        if count:
            toast(self, f"自动分配完成，共派发 {count} 项任务")
        else:
            toast(self, "所有任务均已分配，编队保持当前任务", "info")

    def _on_formation(self, text: str):
        self.engine.formation = text
        self.engine.push_event(f"灭火编队切换为「{text}」阵列，覆盖宽度同步调整", "info")
        self.neg_log.set_events(self.engine.events[:4])
        toast(self, f"编队已切换为 {text}")

    def _refresh(self):
        e = self.engine
        self.s_tasks.set_value(str(sum(1 for t in e.tasks if t["status"] == "待分配")))
        self.coverage = e.coverage
        self.coverage_bar.set_value(min(100, e.coverage / 10 * 100))
        self.coverage_label.setText(
            f"编队覆盖 {e.coverage:.1f} ha · 相邻重叠率 12% · 推进速度 1.1 m/s"
        )
        self.neg_log.set_events(e.events[:4])
        for row in range(self.table.rowCount()):
            t = e.tasks[row]
            if self.table.item(row, 5) and self.table.item(row, 5).text() != t["status"]:
                self.table.item(row, 5).setText(t["status"])


def hline_row():
    from PySide6.QtWidgets import QFrame

    line = QFrame()
    line.setObjectName("Divider")
    line.setFixedHeight(1)
    return line
