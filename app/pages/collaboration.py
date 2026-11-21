"""多机器人协作：真实演练状态与协作日志。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QHeaderView, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QVBoxLayout,
)

from .. import theme
from ..simulation import SimEngine
from ..widgets import Pill, StatCard, label
from .base import Panel, ScrollPage


class CollaborationPage(ScrollPage):
    def __init__(self, engine: SimEngine, parent=None):
        super().__init__(engine, "多机器人协作", "按火点查看空地装备的实时任务，以及自动调度和接替过程")
        self.add_action(Pill("自动协作 · 仿真", "info"))

        stats = QHBoxLayout()
        stats.setSpacing(12)
        self.s_fires = StatCard("活跃火点", "0", "个", "flame", theme.RED, theme.RED_SOFT)
        self.s_air = StatCard("投入无人机", "0", "台", "drone", theme.BLUE, theme.BLUE_SOFT)
        self.s_ground = StatCard("投入地面机器人", "0", "台", "robot", theme.ACCENT, theme.ACCENT_SOFT)
        self.s_working = StatCard("正在喷水", "0", "台", "activity", theme.CYAN, theme.BLUE_SOFT)
        for card in (self.s_fires, self.s_air, self.s_ground, self.s_working):
            card.setMinimumHeight(100)
            stats.addWidget(card, 1)
        self.root.addLayout(stats)

        body = QHBoxLayout()
        body.setSpacing(14)
        left = QVBoxLayout()
        left.setSpacing(14)

        teams = Panel("火点协作编组", "实时读取已分配装备；不同火点互不抢占", "users")
        teams.add_action(Pill("自动调度", "success", dot=False))
        self.team_table = self._table(["火点", "状态", "无人机", "地面机器人", "赶赴 / 侦察", "现场喷水", "待补派"])
        self.team_table.setMinimumHeight(210)
        teams.add(self.team_table)
        self.team_empty = label("暂无活跃火点，系统持续监测。", "caption", color=theme.MUTED)
        teams.add(self.team_empty)
        left.addWidget(teams)

        equipment = Panel("装备协作明细", "选中的火点正在执行任务的装备与阶段", "robot")
        self.unit_table = self._table(["火点", "装备", "类型", "协作任务", "阶段", "电量 / 温度"])
        self.unit_table.setMinimumHeight(275)
        equipment.add(self.unit_table)
        self.unit_empty = label("暂无正在执行火点任务的装备。", "caption", color=theme.MUTED)
        equipment.add(self.unit_empty)
        left.addWidget(equipment)
        body.addLayout(left, 5)

        right = QVBoxLayout()
        log_panel = Panel("协作日志", "按时间倒序 · 记录实际派遣、侦察、到场、接替和扑灭", "activity")
        self.fire_filter = QComboBox()
        self.fire_filter.addItem("全部火点", "")
        self.fire_filter.setMinimumWidth(125)
        self.fire_filter.currentIndexChanged.connect(self._refresh)
        log_panel.add_action(self.fire_filter)
        self.log_table = self._table(["演练时间", "火点", "事件", "涉及装备", "协作过程"])
        self.log_table.setMinimumHeight(480)
        log_panel.add(self.log_table, 1)
        self.log_empty = label("暂无协作记录。发现火情后将自动记录。", "caption", color=theme.MUTED)
        log_panel.add(self.log_empty)
        log_panel.add(label("最多保留本次演练最近 200 条；日志不代表真实通信或路径冲突消解。", "caption", color=theme.MUTED))
        right.addWidget(log_panel, 1)
        body.addLayout(right, 6)
        self.root.addLayout(body)
        self._filter_signature = None
        self._snapshot = None
        engine.tick.connect(self._refresh)
        self._refresh()

    @staticmethod
    def _table(headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setWordWrap(False)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(len(headers) - 1, QHeaderView.ResizeMode.Stretch)
        return table

    @staticmethod
    def _set_rows(table: QTableWidget, rows: list[list[str]]) -> None:
        table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                table.setItem(row, col, item)
            table.setRowHeight(row, 34)

    def _refresh(self, *_):
        e = self.engine
        active = sorted((f for f in e.fires if f.state != "extinguished"), key=lambda f: (f.ignited_at, f.id))
        units = e.active_fire_robots()
        self.s_fires.set_value(str(len(active)))
        self.s_air.set_value(str(sum(r.kind == "UAV" for r in units)))
        self.s_ground.set_value(str(sum(r.kind == "UGV" for r in units)))
        self.s_working.set_value(str(sum(e.spray_target(r) is not None for r in units)))

        fire_ids = sorted({f.id for f in active} | {event["fire_id"] for event in e.collaboration_events if event["fire_id"]})
        if tuple(fire_ids) != self._filter_signature:
            selected = self.fire_filter.currentData() or ""
            self.fire_filter.blockSignals(True)
            self.fire_filter.clear()
            self.fire_filter.addItem("全部火点", "")
            for fid in fire_ids:
                self.fire_filter.addItem(fid, fid)
            self.fire_filter.setCurrentIndex(max(0, self.fire_filter.findData(selected)))
            self.fire_filter.blockSignals(False)
            self._filter_signature = tuple(fire_ids)
        selected = self.fire_filter.currentData() or ""

        team_rows = []
        unit_rows = []
        states = {"suspicious": "待侦察", "spreading": "蔓延中", "suppressing": "扑救中", "contained": "已控制"}
        for fire in active:
            if selected and fire.id != selected:
                continue
            team = [r for r in units if r.assigned_fire_id == fire.id]
            air = sum(r.kind == "UAV" for r in team)
            ground = sum(r.kind == "UGV" for r in team)
            working = sum(e.spray_target(r) is not None for r in team)
            travelling = sum(r.mission in ("en_route", "recon") and not r.route_failed for r in team)
            if fire.state == "suspicious":
                missing = "侦察无人机 1" if not any(r.mission == "recon" for r in team) else "—"
            else:
                missing = f"无人机 {max(0, 2 - air)} / 地面 {max(0, 3 - ground)}"
            team_rows.append([fire.id, states.get(fire.state, fire.state), str(air), str(ground),
                              str(travelling), str(working), missing])
            for r in sorted(team, key=lambda unit: (unit.kind, unit.id)):
                stage = ("路径不可达" if r.route_failed else "急停" if e.estop else
                         "现场喷水" if e.spray_target(r) else
                         {"recon": "侦察中", "en_route": "赶赴中", "spraying": "等待喷水"}.get(r.mission, r.status_text))
                unit_rows.append([fire.id, r.id, "无人机" if r.kind == "UAV" else "地面机器人",
                                  r.task, stage, f"{r.battery:.0f}% / {r.temp:.1f}℃"])
        self._set_rows(self.team_table, team_rows)
        self._set_rows(self.unit_table, unit_rows)
        self.team_empty.setVisible(not team_rows)
        self.unit_empty.setVisible(not unit_rows)

        events = [item for item in e.collaboration_events if not selected or item["fire_id"] == selected]
        log_rows = [[f"T+{int(item['sim_time'])}s", item["fire_id"] or "—", item["kind"],
                     " → ".join(item["robots"]) or "—", item["text"]] for item in events]
        signature = tuple(tuple(row) for row in log_rows)
        if signature != self._snapshot:
            self._set_rows(self.log_table, log_rows)
            self.log_empty.setVisible(not log_rows)
            self._snapshot = signature
