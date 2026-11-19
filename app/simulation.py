"""森林防火演练用的轻量仿真引擎。

说明：本模块提供的是**可解释的算法演示实现**（A*、拍卖竞价、贝叶斯式火势
蔓延推演），不依赖 GPU / 真实模型权重，方便在没有硬件接入时完整演示
"自主导航 → 多机协作 → 火情分析 → 人机交互" 的闭环。真实部署时可将
``SimEngine`` 的方法替换为 ROS2 / 深度学习推理服务的数据接口。
"""
from __future__ import annotations

import heapq
import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from PySide6.QtCore import QObject, QTimer, Signal

GRID_W, GRID_H = 64, 40


# ---------------------------------------------------------------------------
# A* 路径规划（含风场 / 坡度 / 热源代价）
# ---------------------------------------------------------------------------
@dataclass
class PathPlan:
    path: list[tuple[float, float]]
    length_m: float
    eta_s: float
    risk: float
    energy: float
    algo: str


class GridPlanner:
    def __init__(self, seed: int = 7):
        self.rng = random.Random(seed)
        self.blocked = self._make_obstacles()

    def _make_obstacles(self) -> set[tuple[int, int]]:
        blocked: set[tuple[int, int]] = set()
        # 两片密林 + 一条带垭口（y=14..22 可通行）的山脊，作为不可通行区域
        for cx, cy, r in ((15, 10, 4.2), (46, 29, 4.6)):
            for x in range(GRID_W):
                for y in range(GRID_H):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                        blocked.add((x, y))
        for y in list(range(0, 14)) + list(range(23, GRID_H)):
            x = int(30 + 3.2 * math.sin(y / 4.5))
            for dx in (-1, 0, 1):
                blocked.add((x + dx, y))
        # 保证起点与终点周边可通行
        for cx, cy in ((10, 30), (39, 22)):
            for x in range(cx - 2, cx + 3):
                for y in range(cy - 2, cy + 3):
                    blocked.discard((x, y))
        return blocked

    def plan(self, start, goal, wind_deg: float = 225, wind_speed: float = 4.5,
             slope: float = 0.3, fire: tuple[float, float] = (0.66, 0.55),
             algo: str = "RL-A*") -> PathPlan:
        sx, sy = int(start[0] * GRID_W), int(start[1] * GRID_H)
        gx, gy = int(goal[0] * GRID_W), int(goal[1] * GRID_H)
        fx, fy = fire[0] * GRID_W, fire[1] * GRID_H
        wrad = math.radians(wind_deg)
        wind_vec = (math.cos(wrad), math.sin(wrad))
        # 强化学习策略学习到的代价权重（更重视风场与热源规避）
        rl = algo == "RL-A*"
        w_wind = 0.40 if rl else 0.0
        w_slope = 0.26 if rl else 0.0
        w_fire = 0.60 if rl else 0.18

        def heuristic(ax, ay):
            return math.hypot(ax - gx, ay - gy)

        def cost(x, y, nx, ny):
            base = 1.0
            if (nx, ny) in self.blocked:
                return None
            # 风场：顺风省力，逆风耗能
            dx, dy = nx - x, ny - y
            norm = math.hypot(dx, dy) or 1.0
            align = (dx / norm) * wind_vec[0] + (dy / norm) * wind_vec[1]
            base += -w_wind * align * min(wind_speed / 8.0, 1.4)
            # 坡度
            base += slope * w_slope * (1 if ny > y else 0.55)
            # 热源斥力
            d = math.hypot(nx - fx, ny - fy)
            if d < 9:
                base += (9 - d) * w_fire
            # 强化学习策略额外学习到「安全走廊」：贴近障碍物时抬高代价
            if rl:
                near = False
                for ox in (-1, 0, 1):
                    for oy in (-1, 0, 1):
                        if (nx + ox, ny + oy) in self.blocked:
                            near = True
                            break
                    if near:
                        break
                if near:
                    base += 0.85
            return max(0.25, base)

        open_heap = [(heuristic(sx, sy), 0.0, (sx, sy))]
        came: dict[tuple[int, int], tuple[int, int]] = {}
        gscore = {(sx, sy): 0.0}
        visited = set()
        found = False
        while open_heap:
            _, g, cur = heapq.heappop(open_heap)
            if cur in visited:
                continue
            visited.add(cur)
            if cur == (gx, gy):
                found = True
                break
            x, y = cur
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < GRID_W and 0 <= ny < GRID_H):
                    continue
                c = cost(x, y, nx, ny)
                if c is None:
                    continue
                ng = g + c * (1.414 if dx and dy else 1.0)
                if ng < gscore.get((nx, ny), 1e18):
                    gscore[(nx, ny)] = ng
                    came[(nx, ny)] = (x, y)
                    heapq.heappush(open_heap, (ng + heuristic(nx, ny), ng, (nx, ny)))

        if not found:
            pts = [(start[0], start[1]), (goal[0], goal[1])]
            return PathPlan(pts, 820, 96, 0.42, 18, algo)

        cells = [(gx, gy)]
        while cells[-1] != (sx, sy):
            cells.append(came[cells[-1]])
        cells.reverse()
        path = [(x / GRID_W, y / GRID_H) for x, y in cells]

        # 折线简化
        simplified = [path[0]]
        for i in range(1, len(path) - 1):
            p0, p1, p2 = simplified[-1], path[i], path[i + 1]
            a1 = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
            a2 = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            if abs(a1 - a2) > 0.18:
                simplified.append(p1)
        simplified.append(path[-1])
        # 平滑插值，便于绘制曲线
        smooth: list[tuple[float, float]] = []
        for i in range(len(simplified) - 1):
            a, b = simplified[i], simplified[i + 1]
            for t in range(6):
                k = t / 6
                smooth.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
        smooth.append(simplified[-1])

        length = sum(
            math.hypot((smooth[i + 1][0] - smooth[i][0]) * 1200,
                       (smooth[i + 1][1] - smooth[i][1]) * 800)
            for i in range(len(smooth) - 1)
        )
        # 沿路径评估热源距离与风场对齐度，用于风险 / 能耗 / 耗时
        fire_near = 0.0
        clear_near = 0.0
        align_sum = 0.0
        blocked = self.blocked
        for i, (px, py) in enumerate(smooth):
            d = math.hypot(px * GRID_W - fx, py * GRID_H - fy)
            fire_near += math.exp(-d / 7.0)
            cx, cy = int(px * GRID_W), int(py * GRID_H)
            dmin = 3.0
            for ox in range(-3, 4):
                for oy in range(-3, 4):
                    if (cx + ox, cy + oy) in blocked:
                        dmin = min(dmin, math.hypot(ox, oy))
            clear_near += math.exp(-dmin / 1.4)
            if i:
                dx = (px - smooth[i - 1][0]) * GRID_W
                dy = (py - smooth[i - 1][1]) * GRID_H
                norm = math.hypot(dx, dy) or 1.0
                align_sum += (dx / norm) * wind_vec[0] + (dy / norm) * wind_vec[1]
        n = max(1, len(smooth))
        fire_prox = fire_near / n
        clear_prox = clear_near / n
        align_avg = align_sum / max(1, n - 1)
        risk = min(0.97, 0.14 + 0.50 * fire_prox + 0.26 * clear_prox
                   + 0.14 * slope + 0.06 * min(1.0, wind_speed / 10))
        speed = 1.6 + wind_speed * 0.10 * (0.7 + align_avg)
        eta = length / max(speed, 0.6)
        energy = length * 0.012 * (1 + slope * 0.3) * (1.08 - 0.22 * align_avg)
        return PathPlan(smooth, length, eta, risk, energy, algo)


# ---------------------------------------------------------------------------
# 贝叶斯式火势蔓延推演
# ---------------------------------------------------------------------------
class FireSpreadModel:
    """以风向、坡度、植被干燥度为证据，推演火线概率场。"""

    def __init__(self, seed: int = 11):
        self.rng = random.Random(seed)

    def grid(self, minutes: int = 30, wind_deg: float = 225, wind_speed: float = 4.5,
             humidity: float = 32, origin: tuple[float, float] = (0.6, 0.52)) -> list[list[float]]:
        w, h = 48, 30
        ox, oy = origin[0] * w, origin[1] * h
        wrad = math.radians(wind_deg)
        wx, wy = math.cos(wrad), math.sin(wrad)
        spread = (minutes / 30.0) ** 0.85 * (0.55 + wind_speed / 9.0) * (1.35 - humidity / 100.0)
        out = [[0.0] * w for _ in range(h)]
        for y in range(h):
            for x in range(w):
                dx, dy = x - ox, y - oy
                d = math.hypot(dx, dy)
                if d < 1e-3:
                    out[y][x] = 1.0
                    continue
                along = (dx / d) * wx + (dy / d) * wy
                directional = 1.0 + 0.85 * along
                radius = 3.2 + spread * 7.5 * directional
                p = math.exp(-((d / radius) ** 2) * 1.55)
                # 地形噪声（林相不均匀）
                p *= 0.82 + 0.36 * math.sin(x * 0.55 + y * 0.31)
                out[y][x] = max(0.0, min(1.0, p))
        return out


# ---------------------------------------------------------------------------
# 运行状态
# ---------------------------------------------------------------------------
@dataclass
class Robot:
    id: str
    name: str
    kind: str                    # UAV / UGV
    model: str
    status: str = "on_mission"   # on_mission / standby / charging / returning / offline
    battery: float = 80.0
    signal: float = 92.0
    payload: float = 60.0
    temp: float = 26.0
    speed: float = 0.0
    altitude: float = 0.0
    x: float = 0.2
    y: float = 0.2
    task: str = "待命"
    history: list[float] = field(default_factory=list)

    @property
    def status_text(self) -> str:
        return {
            "on_mission": "执行任务",
            "standby": "待命",
            "charging": "充电中",
            "returning": "返航中",
            "offline": "离线",
        }.get(self.status, "未知")

    @property
    def status_kind(self) -> str:
        return {
            "on_mission": "success",
            "standby": "info",
            "charging": "warning",
            "returning": "purple",
            "offline": "critical",
        }.get(self.status, "info")


class SimEngine(QObject):
    tick = Signal()
    alert_added = Signal(dict)
    event_added = Signal(dict)

    def __init__(self, seed: int = 2026):
        super().__init__()
        self.rng = random.Random(seed)
        self.planner = GridPlanner()
        self.spread_model = FireSpreadModel()
        self.started_at = datetime.now()
        self.paused = False
        self.mode = "空地协同"
        self.wind_deg = 228.0
        self.wind_speed = 4.6
        self.humidity = 31.0
        self.temperature = 28.4
        self.slope = 0.34
        self.risk = 82.0
        self.fire_area = 12.8
        self.containment = 18.0
        self.fire_confidence = 96.0
        self.fire_origin = (0.655, 0.545)
        self.auto_avoid = True
        self.estop = False
        self.formation = "楔形推进"
        self.coverage = 3.6
        self.plan = self.planner.plan((0.16, 0.78), (0.52, 0.62), self.wind_deg,
                                     self.wind_speed, self.slope, self.fire_origin)
        self.baseline = self.planner.plan((0.16, 0.78), (0.52, 0.62), self.wind_deg,
                                          self.wind_speed, self.slope, self.fire_origin, algo="A*")
        self.robots = self._make_robots()
        self.alerts = self._make_alerts()
        self.events = self._make_events()
        self.tasks = self._make_tasks()
        self.temp_history = [26.1, 26.6, 27.2, 27.0, 27.8, 28.1, 28.4]
        self.risk_history = [54, 58, 63, 68, 72, 78, 82]
        self.containment_history = [4, 6, 8, 11, 14, 16, 18]
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    # ---------------- 初始化数据 ----------------
    def _make_robots(self) -> list[Robot]:
        specs = [
            ("UAV-01", "苍鹰一号", "UAV", "FG-A7 六旋翼"),
            ("UAV-02", "苍鹰二号", "UAV", "FG-A7 六旋翼"),
            ("UAV-03", "云雀三号", "UAV", "FG-A5 四旋翼"),
            ("UAV-04", "云雀四号", "UAV", "FG-A5 四旋翼"),
            ("UGV-01", "獾式一号", "UGV", "FG-R3 履带底盘"),
            ("UGV-02", "獾式二号", "UGV", "FG-R3 履带底盘"),
            ("UGV-03", "獾式三号", "UGV", "FG-R3 履带底盘"),
            ("UGV-04", "獾式四号", "UGV", "FG-R4 轮履两用"),
        ]
        positions = [
            (0.30, 0.30), (0.42, 0.24), (0.52, 0.36), (0.24, 0.52),
            (0.22, 0.70), (0.32, 0.76), (0.42, 0.68), (0.50, 0.76),
        ]
        tasks = ["火线侦察", "热源定位", "空中中继", "通信中继",
                 "地面扑打", "隔离带作业", "水带铺设", "洒水降温"]
        robots: list[Robot] = []
        for i, (rid, name, kind, model) in enumerate(specs):
            r = Robot(rid, name, kind, model)
            r.x, r.y = positions[i]
            r.battery = [86, 74, 63, 91, 68, 82, 57, 45][i]
            r.signal = [96, 91, 88, 94, 89, 84, 92, 79][i]
            r.payload = [40, 35, 20, 15, 78, 74, 66, 58][i]
            r.temp = [24.5, 25.1, 24.9, 23.8, 41.2, 44.6, 39.8, 47.3][i]
            r.status = ["on_mission", "on_mission", "on_mission", "standby",
                        "on_mission", "on_mission", "standby", "charging"][i]
            r.task = tasks[i]
            r.altitude = 80 + i * 6 if kind == "UAV" else 0
            r.speed = 4.2 if kind == "UAV" else 1.1
            r.history = [self.rng.uniform(0.6, 1.0) * v for v in (0.8, 0.9, 1.0, 0.95, 1.05, 1.0)]
            robots.append(r)
        return robots

    def _make_alerts(self) -> list[dict]:
        now = datetime.now()
        return [
            {"time": (now - timedelta(minutes=2, seconds=12)).strftime("%H:%M:%S"),
             "level": "critical", "title": "东北坡出现明火", "detail": "热成像通道 3 检测到 412℃ 热源，置信度 96%",
             "source": "UAV-02 / 热成像"},
            {"time": (now - timedelta(minutes=7, seconds=40)).strftime("%H:%M:%S"),
             "level": "warning", "title": "烟雾浓度超阈值", "detail": "PM2.5 达到 218 μg/m³，超过预警线 180",
             "source": "地面站 07"},
            {"time": (now - timedelta(minutes=15, seconds=5)).strftime("%H:%M:%S"),
             "level": "info", "title": "UAV-03 完成建图闭环", "detail": "SLAM 回环检测成功，地图精度提升至 0.08 m",
             "source": "SLAM 服务"},
            {"time": (now - timedelta(minutes=26, seconds=31)).strftime("%H:%M:%S"),
             "level": "warning", "title": "阵风 7 级", "detail": "西南风 8.2 m/s，火势蔓延风险上升",
             "source": "气象站"},
        ]

    def _make_events(self) -> list[dict]:
        return [
            {"time": datetime.now().strftime("%H:%M:%S"), "level": "success",
             "text": "空地协同编队完成队形收敛，覆盖宽度 120 m"},
            {"time": (datetime.now() - timedelta(seconds=26)).strftime("%H:%M:%S"), "level": "info",
             "text": "UGV-02 竞拍成功，承接「隔离带作业」任务"},
            {"time": (datetime.now() - timedelta(seconds=54)).strftime("%H:%M:%S"), "level": "info",
             "text": "路径冲突 T-14 经协商机制自动消解（让行方案 B）"},
        ]

    def _make_tasks(self) -> list[dict]:
        return [
            {"id": "T-21", "name": "火线北侧压制", "pos": "B-07 / 124.6 ha", "priority": "紧急",
             "reward": 92, "robot": "UGV-01", "status": "执行中", "progress": 68},
            {"id": "T-22", "name": "东侧隔离带开挖", "pos": "B-11 / 86.2 ha", "priority": "高",
             "reward": 78, "robot": "UGV-02", "status": "执行中", "progress": 41},
            {"id": "T-23", "name": "空中热源复核", "pos": "A-03 / 32.4 ha", "priority": "高",
             "reward": 64, "robot": "UAV-02", "status": "执行中", "progress": 77},
            {"id": "T-24", "name": "水带铺设至 3 号水源", "pos": "C-02 / 51.0 ha", "priority": "中",
             "reward": 51, "robot": "UGV-03", "status": "待分配", "progress": 0},
            {"id": "T-25", "name": "南线洒水降温", "pos": "C-06 / 44.8 ha", "priority": "中",
             "reward": 46, "robot": "UGV-04", "status": "待分配", "progress": 0},
        ]

    # ---------------- 定时推进 ----------------
    def _on_tick(self):
        if self.paused:
            return
        self.temperature = round(min(36.0, self.temperature + self.rng.uniform(-0.06, 0.1)), 1)
        self.humidity = round(max(18.0, self.humidity + self.rng.uniform(-0.35, 0.3)), 1)
        self.wind_speed = round(max(1.2, min(9.5, self.wind_speed + self.rng.uniform(-0.18, 0.2))), 1)
        self.wind_deg = (self.wind_deg + self.rng.uniform(-1.6, 1.6)) % 360
        target_risk = 52 + (self.temperature - 20) * 2.6 - (self.humidity - 20) * 0.9 + self.wind_speed * 2.4
        self.risk = round(max(10.0, min(99.0, self.risk + (target_risk - self.risk) * 0.12)), 1)
        if not self.estop:
            self.fire_area = round(self.fire_area + self.rng.uniform(0.01, 0.12), 2)
            self.containment = round(min(96.0, self.containment + self.rng.uniform(0.05, 0.28)), 1)
        for r in self.robots:
            if r.status == "offline":
                continue
            if r.status == "on_mission":
                r.battery = max(6.0, r.battery - self.rng.uniform(0.05, 0.16))
                r.temp = max(20.0, min(58.0, r.temp + self.rng.uniform(-0.25, 0.3)))
                r.speed = max(0.2, min(6.0, r.speed + self.rng.uniform(-0.15, 0.15)))
                r.history = (r.history + [r.temp])[-14:]
            elif r.status == "charging":
                r.battery = min(100.0, r.battery + 0.35)
            self._advance_robot(r)
        self.temp_history = (self.temp_history + [self.temperature])[-16:]
        self.risk_history = (self.risk_history + [self.risk])[-16:]
        self.containment_history = (self.containment_history + [self.containment])[-16:]
        for t in self.tasks:
            if t["status"] == "执行中":
                t["progress"] = min(100, t["progress"] + self.rng.randint(0, 2))
        self.tick.emit()

    def _advance_robot(self, r: Robot):
        if r.status not in ("on_mission", "returning"):
            return
        if r.kind == "UAV":
            r.x = min(0.92, max(0.05, r.x + self.rng.uniform(-0.006, 0.008)))
            r.y = min(0.92, max(0.05, r.y + self.rng.uniform(-0.005, 0.006)))
        else:
            r.x = min(0.9, max(0.08, r.x + self.rng.uniform(-0.003, 0.004)))
            r.y = min(0.9, max(0.08, r.y + self.rng.uniform(-0.003, 0.004)))

    # ---------------- 业务动作 ----------------
    def push_event(self, text: str, level: str = "info") -> None:
        ev = {"time": datetime.now().strftime("%H:%M:%S"), "level": level, "text": text}
        self.events = ([ev] + self.events)[:40]
        self.event_added.emit(ev)

    def push_alert(self, title: str, detail: str, level: str = "warning", source: str = "指挥终端") -> None:
        al = {"time": datetime.now().strftime("%H:%M:%S"), "level": level,
              "title": title, "detail": detail, "source": source}
        self.alerts = ([al] + self.alerts)[:20]
        self.alert_added.emit(al)

    def replan(self, wind_deg: float | None = None, wind_speed: float | None = None,
               slope: float | None = None, algo: str = "RL-A*") -> PathPlan:
        if wind_deg is not None:
            self.wind_deg = wind_deg
        if wind_speed is not None:
            self.wind_speed = wind_speed
        if slope is not None:
            self.slope = slope
        self.plan = self.planner.plan((0.16, 0.78), (0.52, 0.62), self.wind_deg,
                                      self.wind_speed, self.slope, self.fire_origin, algo)
        self.baseline = self.planner.plan((0.16, 0.78), (0.52, 0.62), self.wind_deg,
                                          self.wind_speed, self.slope, self.fire_origin, algo="A*")
        return self.plan

    def run_auction(self, task_index: int) -> Robot:
        task = self.tasks[task_index]
        candidates = [r for r in self.robots if r.status in ("on_mission", "standby")]
        if not candidates:
            return self.robots[0]

        def bid(r: Robot) -> float:
            dist = math.hypot(r.x - 0.6, r.y - 0.55)
            capability = 1.0 if (task["name"].find("空中") >= 0) == (r.kind == "UAV") else 0.55
            return task["reward"] * capability + r.battery * 0.35 - dist * 42 + r.payload * 0.1

        best = max(candidates, key=bid)
        task["robot"] = best.id
        task["status"] = "已派发"
        task["progress"] = 0
        best.task = task["name"]
        self.push_event(f"{task['id']}「{task['name']}」拍卖结束，{best.id} 以 {bid(best):.1f} 分中标", "success")
        return best

    def spread(self, minutes: int) -> list[list[float]]:
        return self.spread_model.grid(minutes, self.wind_deg, self.wind_speed,
                                      self.humidity, self.fire_origin)

    def wind_label(self) -> str:
        dirs = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
        idx = int((self.wind_deg + 22.5) // 45) % 8
        return f"{dirs[idx]}风 {self.wind_speed:.1f} m/s"

    def risk_level(self) -> tuple[str, str]:
        if self.risk >= 80:
            return "极高风险", "critical"
        if self.risk >= 60:
            return "高风险", "warning"
        if self.risk >= 40:
            return "中风险", "info"
        return "低风险", "success"

    def vision_scores(self) -> tuple[float, float, float]:
        fire = min(99.4, self.fire_confidence + math.sin(self.started_at.second / 4) * 1.2)
        smoke = min(99.0, 88.0 + math.cos(self.started_at.second / 5) * 2.4)
        normal = max(0.6, 100 - fire - smoke * 0.18)
        return fire, smoke, max(0.4, normal)
