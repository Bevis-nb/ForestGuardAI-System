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


    def assess(self, fire, minutes: int, wind_deg: float, wind_speed: float,
               humidity: float) -> dict:
        """演示性概率场和下风向隔离带；不是经验证的火场预测。"""
        grid = self.grid(minutes, wind_deg, wind_speed, humidity, fire.origin)
        # 隔离带放在中等概率区的下风缘，垂直于蔓延方向。
        angle = math.radians(wind_deg)
        dx, dy = math.cos(angle), math.sin(angle)
        w, h = len(grid[0]), len(grid)
        distances = [((x / w - fire.origin[0]) * dx + (y / h - fire.origin[1]) * dy)
                     for y, row in enumerate(grid) for x, value in enumerate(row)
                     if value >= 0.4]
        distance = max(0.04, max(distances, default=0.04))
        cx, cy = fire.origin[0] + dx * distance, fire.origin[1] + dy * distance
        half = min(0.18, 0.06 + distance * 0.45)
        def clamp(value):
            return max(0.0, min(1.0, value))
        # 带状隔离线以弧形包围下风向火头；采样点也用于全火点避让检测。
        bend = min(0.07, 0.02 + distance * 0.2)
        line = tuple((clamp(cx + dy * half * u + dx * bend * (1 - u * u)),
                      clamp(cy - dx * half * u + dy * bend * (1 - u * u)))
                     for u in (i / 6 for i in range(-6, 7)))
        # 地图尺度 1200m × 800m，像元统计面积仅为演示估计。
        area = sum(v >= 0.4 for row in grid for v in row) * (1200 * 800 / (w * h)) / 10000
        return {"grid": grid, "line": line, "area": area,
                "width_m": 12 if fire.intensity >= 70 else (8 if fire.intensity >= 35 else 6)}


    def assess_all(self, fires, minutes: int, wind_deg: float, wind_speed: float,
                   humidity: float) -> dict:
        """合并活跃火点概率场，并避开其他预测燃烧区调整建议隔离线。

        概率采用逐像元最大值（不作独立性假设）；隔离带为简化示意，
        找不到不穿越燃烧区的线时保留原线并标记需人工复核。
        """
        active = [f for f in fires if f.state != "extinguished"]
        assessments = {f.id: self.assess(f, minutes, wind_deg, wind_speed, humidity)
                       for f in active}
        if not assessments:
            return {"grid": [], "fires": {}, "area": 0.0}
        grids = [item["grid"] for item in assessments.values()]
        h, w = len(grids[0]), len(grids[0][0])
        combined = [[max(grid[y][x] for grid in grids) for x in range(w)]
                    for y in range(h)]
        dx, dy = math.cos(math.radians(wind_deg)), math.sin(math.radians(wind_deg))
        for fire in active:
            item = assessments[fire.id]
            base_line = item["line"]
            # 弧线外移时逐段采样全部火点的中高概率区，防止穿越相邻火场。
            found = None
            for step in range(31):
                offset = step * 0.015
                line = tuple((point[0] + dx * offset, point[1] + dy * offset)
                             for point in base_line)
                if any(not (0 <= x <= 1 and 0 <= y <= 1) for x, y in line):
                    break
                safe = True
                for start, end in zip(line, line[1:]):
                    for i in range(5):
                        t = i / 4
                        x = start[0] * (1 - t) + end[0] * t
                        y = start[1] * (1 - t) + end[1] * t
                        if combined[min(h - 1, int(y * h))][min(w - 1, int(x * w))] >= 0.4:
                            safe = False
                            break
                    if not safe:
                        break
                if safe:
                    found = line
                    break
            item["line_conflict"] = found is None
            item["line"] = found if found is not None else base_line
        area = sum(v >= 0.4 for row in combined for v in row) * (1200 * 800 / (w * h)) / 10000
        return {"grid": combined, "fires": assessments, "area": area}


# ---------------------------------------------------------------------------
# 运行状态
# ---------------------------------------------------------------------------
BASES = [
    ("B-01", "北山基地", 0.12, 0.22),
    ("B-02", "西林基地", 0.14, 0.78),
    ("B-03", "东坡基地", 0.86, 0.24),
    ("B-04", "南谷基地", 0.84, 0.80),
]


@dataclass
class FireIncident:
    """一次火情事件：强度 / 面积 / 控制率随时间演化，可被扑灭。"""
    id: str = "A-03"
    origin: tuple[float, float] = (0.655, 0.545)
    intensity: float = 70.0        # 0~100，0 表示已扑灭
    area: float = 12.8             # ha
    containment: float = 18.0      # %
    state: str = "spreading"       # spreading / suppressing / contained / extinguished
    ignited_at: float = 0.0        # sim 秒
    peak_intensity: float = 70.0
    peak_area: float = 12.8
    water_used_l: float = 0.0
    spread_rate: float = 0.0       # 每 tick 强度增量
    suppression_rate: float = 0.0  # 每 tick 强度削减
    extinguished_at: float = -1.0
    history: list[float] = field(default_factory=list)
    area_history: list[float] = field(default_factory=list)


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
    # --- 灭火演示任务状态机 ---
    mission: str = "idle"        # idle / en_route / spraying / returning / refilling
    home_x: float = 0.2
    home_y: float = 0.2
    target_x: float = 0.5
    target_y: float = 0.5
    heading: float = 0.0         # 弧度，0=向东
    spraying: bool = False
    water_l: float = 0.0         # 当前载水量（升）
    water_cap: float = 0.0
    suppression_power: float = 0.0  # 每 tick 压制强度
    arrived: bool = False
    eta_seconds: float = 0.0
    eta_status: str = "准时"     # 早到 / 准时 / 晚到
    assigned_fire_id: str = ""
    needs_refill: bool = False

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
    recon_confirmed = Signal(object)
    fire_appeared = Signal(object)

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
        # 告警阈值（可在系统设置中调整）
        self.th_temp = 65.0
        self.th_smoke = 180.0
        self.th_risk = 80.0
        self.silent = False
        self._th_state: dict[str, bool] = {}
        self.slope = 0.34
        self.risk = 82.0
        self.fire_area = 0.0
        self.containment = 100.0
        self.fire_confidence = 96.0
        self.fire_origin = (0.655, 0.545)
        # --- 灭火演示：火情状态机 / 调度 / 速度 ---
        self.fires: list[FireIncident] = []
        self._next_fire_in = 1
        self.auto_ignite_enabled = False  # 登录后由主窗口延迟开启
        self.fire = FireIncident(id="A-00", intensity=0.0, area=0.0, containment=100.0, state="extinguished")
        self.fire_history: list[FireIncident] = []
        self.fire_counter = 0
        self.sim_time = 0.0          # 累计仿真秒
        self.sim_speed = 1           # 1 / 2 / 4 倍速
        self.auto_dispatch = True
        self.dispatch_plan: list[dict] = []
        self.last_report: dict | None = None
        self._milestones: set[int] = set()
        self._dispatch_timer = 0.0
        self.auto_avoid = True
        self.estop = False
        self.formation = "楔形推进"
        self.coverage = 3.6
        self.plan = self.planner.plan((0.16, 0.78), (0.52, 0.62), self.wind_deg,
                                     self.wind_speed, self.slope, self.fire_origin)
        self.baseline = self.planner.plan((0.16, 0.78), (0.52, 0.62), self.wind_deg,
                                          self.wind_speed, self.slope, self.fire_origin, algo="A*")
        self.robots = self._make_robots()
        self.alerts: list[dict] = []
        self.events: list[dict] = []
        self.tasks = self._make_tasks()
        self.temp_history = [26.1, 26.6, 27.2, 27.0, 27.8, 28.1, 28.4]
        self.risk_history = [54, 58, 63, 68, 72, 78, 82]
        self.containment_history = [4, 6, 8, 11, 14, 16, 18]
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def reset_session(self) -> None:
        """开始新的演练：就地重置装备，保留 UI 持有的 Robot 对象引用。"""
        for robot, initial in zip(self.robots, self._make_robots()):
            robot.__dict__.update(initial.__dict__)
        self.fires.clear()
        self.fire_history.clear()
        self.fire_counter = 0
        self.fire = FireIncident(id="A-00", intensity=0.0, area=0.0,
                                 containment=100.0, state="extinguished")
        self.fire_area = 0.0
        self.containment = 100.0
        self.fire_origin = (0.655, 0.545)
        self.sim_time = 0.0
        self.dispatch_plan = []
        self.last_report = None
        self._milestones.clear()
        self._th_state.clear()
        self.alerts.clear()
        self.events.clear()
        self.paused = False
        self.estop = False
        self.auto_ignite_enabled = False
        self._next_fire_in = 1
        self.tick.emit()

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
        base_prefixes = ["A", "B", "C", "D"]
        robots: list[Robot] = []
        for b_idx, (bid, bname, bx, by) in enumerate(BASES):
            prefix = base_prefixes[b_idx]
            for i, (rid, name, kind, model) in enumerate(specs):
                full_id = f"{prefix}-{rid}"
                r = Robot(full_id, f"{bname[:2]}·{name}", kind, model)
                r.x, r.y = bx, by
                r.home_x, r.home_y = bx, by
                r.battery = [86, 74, 63, 91, 68, 82, 57, 45][i]
                r.signal = [96, 91, 88, 94, 89, 84, 92, 79][i]
                r.payload = [40, 35, 20, 15, 78, 74, 66, 58][i]
                r.water_cap = 35.0 if kind == "UAV" else 220.0
                r.water_l = r.water_cap * (r.payload / 100.0)
                r.suppression_power = 0.45 if kind == "UAV" else 1.25
                r.temp = 25.0
                r.status = "on_mission" if (b_idx in (0, 2) and i == 0) else "standby"
                r.mission = "patrol" if (b_idx in (0, 2) and i == 0) else "idle"
                r.task = "全林区覆盖巡逻" if r.mission == "patrol" else f"{bname}待命"
                r.altitude = 80 + i * 6 if kind == "UAV" else 0
                r.speed = 4.2 if kind == "UAV" else 1.1
                r.history = [25.0] * 6
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
        steps = max(1, int(self.sim_speed))
        for _ in range(steps):
            self._step_sim()
        self.tick.emit()

    def _step_sim(self):
        self.sim_time += 1.0
        self.temperature = round(min(36.0, self.temperature + self.rng.uniform(-0.06, 0.1)), 1)
        self.humidity = round(max(18.0, self.humidity + self.rng.uniform(-0.35, 0.3)), 1)
        self.wind_speed = round(max(1.2, min(9.5, self.wind_speed + self.rng.uniform(-0.18, 0.2))), 1)
        self.wind_deg = (self.wind_deg + self.rng.uniform(-1.6, 1.6)) % 360

        # 自动随机时间生成火点（支持多火点）
        if self.auto_ignite_enabled:
            self._next_fire_in -= 1
            if self._next_fire_in <= 0 and len([x for x in self.fires if x.state != "extinguished"]) < 3:
                self._next_fire_in = self.rng.randint(18, 32)
                self.ignite_random_fire(auto_notify=True)

        # 保持固定 2 架健康无人机执行全林区覆盖巡逻（100s 全覆盖）
        for r in self.robots:
            if r.kind == "UAV" and r.mission == "patrol" and (r.temp > 45.0 or r.battery < 25.0):
                self._assign_nearest_base(r)
        patrol_uavs = [r for r in self.robots if r.kind == "UAV" and r.mission == "patrol"]
        if len(patrol_uavs) < 2:
            for r in self.robots:
                if r.kind == "UAV" and r.mission == "idle" and r.status != "offline" and r.battery >= 25.0 and r.temp <= 45.0:
                    r.mission = "patrol"
                    r.status = "on_mission"
                    r.task = "全林区覆盖巡逻"
                    patrol_uavs.append(r)
                    if len(patrol_uavs) >= 2:
                        break

        # 推进机器人移动与灭火作业
        suppression_by_fire: dict[str, float] = {}
        active_fires_now = [f for f in self.fires if f.state != "extinguished"]
        for r in self.robots:
            if r.status == "offline":
                continue
            near_fire = any(math.hypot(r.x - f.origin[0], r.y - f.origin[1]) < 0.14 for f in active_fires_now)
            if near_fire and r.status == "on_mission":
                r.temp = min(68.0, r.temp + self.rng.uniform(1.5, 2.8))
            elif r.status in ("standby", "charging"):
                r.temp = max(25.0, r.temp - 2.5)
            else:
                r.temp = max(25.0, r.temp - 1.2)

            if r.status == "on_mission":
                r.battery = max(6.0, r.battery - self.rng.uniform(0.04, 0.12))
                r.speed = max(0.2, min(6.0, r.speed + self.rng.uniform(-0.15, 0.15)))
                r.history = (r.history + [r.temp])[-14:]
            elif r.status == "charging":
                r.battery = min(100.0, r.battery + 0.45)
                r.water_l = min(r.water_cap, r.water_l + 6.0)
                r.payload = round(100.0 * r.water_l / max(1.0, r.water_cap), 1)
                if r.needs_refill and r.water_l >= r.water_cap and r.battery >= 40:
                    r.needs_refill = False
                    r.status = "standby"
                    r.mission = "idle"
                    r.task = "补给完成 · 待命"
            self._advance_robot(r)
            if r.spraying and not self.estop:
                f_obj = next((f for f in self.fires if f.id == r.assigned_fire_id
                              and f.state != "extinguished"), None)
                if f_obj is None or r.mission != "spraying" or math.hypot(r.x - f_obj.origin[0], r.y - f_obj.origin[1]) > 0.06:
                    r.spraying = False
                else:
                    demand = 1.8 if r.kind == "UGV" else 0.6
                    used = min(r.water_l, demand)
                    if used > 0:
                        suppression_by_fire[f_obj.id] = suppression_by_fire.get(f_obj.id, 0.0) + r.suppression_power * (used / demand)
                        r.water_l = max(0.0, r.water_l - used)
                        r.payload = round(100.0 * r.water_l / max(1.0, r.water_cap), 1)
                        f_obj.water_used_l += used
                    if r.water_l <= 1e-6:
                        r.spraying = False
                        r.assigned_fire_id = ""
                        r.needs_refill = True
                        self._assign_nearest_base(r)
                        self.push_event(f"{r.id} 水量耗尽，返回所属基地补给", "warning")

        # 多火点蔓延与扑救对抗算法
        active_fires = [f for f in self.fires if f.state != "extinguished"]
        for f in active_fires:
            if self.estop:
                continue
            wind_factor = 0.25 + (self.wind_speed / 10.0) * 0.45
            humidity_factor = max(0.3, 1.2 - self.humidity / 100.0)
            spread = wind_factor * humidity_factor * 0.50
            sup = suppression_by_fire.get(f.id, 0.0)
            f.spread_rate = round(spread, 2)
            f.suppression_rate = round(sup, 2)
            net = spread - sup
            f.intensity = max(0.0, min(100.0, f.intensity + net))
            f.peak_intensity = max(f.peak_intensity, f.intensity)
            if net > 0:
                f.area = round(f.area + net * 0.12, 2)
                f.peak_area = max(f.peak_area, f.area)
                if f.state != "suspicious":
                    f.state = "spreading"
            elif f.intensity > 0:
                f.area = round(max(0.2, f.area + net * 0.08), 2)
                f.state = "contained" if f.intensity < 30 else "suppressing"

            f.containment = round(max(5.0, min(100.0, 100.0 - f.intensity * 0.92)), 1)
            f.history = (f.history + [f.intensity])[-30:]
            f.area_history = (f.area_history + [f.area])[-30:]

            if f.intensity <= 0.0:
                f.intensity = 0.0
                f.containment = 100.0
                f.state = "extinguished"
                f.extinguished_at = self.sim_time
                duration = max(1, int(self.sim_time - f.ignited_at))
                self.fire_history.append(f)
                self.push_alert(
                    f"火点 {f.id} 已完全扑灭！",
                    f"耗时 {duration}s · 峰值过火 {f.peak_area:.1f} ha · 耗水 {f.water_used_l:.0f} L",
                    "success", "灭火捷报",
                )
                self.push_event(f"火点 {f.id} 明火已扑灭，相关装备自动返回就近空闲基地", "success")
                for r in self.robots:
                    if r.assigned_fire_id == f.id:
                        r.spraying = False
                        r.assigned_fire_id = ""
                        self._assign_nearest_base(r)

        # 已扑灭火点 4 秒后从地图自动消失
        self.fires = [
            f for f in self.fires
            if not (f.state == "extinguished" and f.extinguished_at >= 0 and self.sim_time - f.extinguished_at >= 4.0)
        ]

        still_active = [f for f in self.fires if f.state != "extinguished"]
        if self.auto_dispatch and not self.estop:
            for fire in still_active:
                if fire.state == "suspicious":
                    self._dispatch_scout(fire)
                else:
                    self._ensure_dispatch(fire.id)
        if still_active:
            self.fire = still_active[0]
            self.fire_origin = self.fire.origin
            self.fire_area = round(sum(f.area for f in still_active), 1)
            self.containment = round(sum(f.containment for f in still_active) / len(still_active), 1)
        else:
            self.fire_area = 0.0
            self.containment = 100.0

        fire_risk_boost = (self.fire.intensity / 100.0) * 28.0 if still_active else -18.0
        target_risk = 32 + (self.temperature - 20) * 1.8 - (self.humidity - 20) * 0.6 + self.wind_speed * 1.6 + fire_risk_boost
        self.risk = round(max(10.0, min(99.0, self.risk + (target_risk - self.risk) * 0.14)), 1)

        self.temp_history = (self.temp_history + [self.temperature])[-16:]
        self.risk_history = (self.risk_history + [self.risk])[-16:]
        self.containment_history = (self.containment_history + [self.containment])[-16:]
        for t in self.tasks:
            if t["status"] == "执行中":
                t["progress"] = min(100, t["progress"] + self.rng.randint(1, 3))
        self._check_thresholds()

    def _check_thresholds(self) -> None:
        """阈值越限（上升沿）时推送告警，避免重复刷屏。"""
        checks = (
            ("temp", self.temperature >= self.th_temp,
             "地表温度超阈值", f"实测 {self.temperature:.1f} ℃ · 阈值 {self.th_temp:.0f} ℃", "warning"),
            ("risk", self.risk >= self.th_risk,
             "火险指数超阈值", f"当前 {self.risk:.0f} · 阈值 {self.th_risk:.0f}", "critical"),
        )
        for key, hit, title, detail, level in checks:
            prev = self._th_state.get(key, hit)
            self._th_state[key] = hit
            if not hit or prev:
                continue
            if self.silent and level != "critical":
                continue
            self.push_alert(title, detail, level, "阈值监测")

    def _assign_nearest_base(self, r: Robot):
        """任务完成或需充电时，只返回该装备所属的固定基地。"""
        bname = next((b[1] for b in BASES if abs(b[2] - r.home_x) < 0.05 and abs(b[3] - r.home_y) < 0.05), "所属基地")
        r.mission = "returning"
        r.status = "returning"
        r.task = f"返回{bname}"

    def _advance_robot(self, r: Robot):
        if self.estop or r.status not in ("on_mission", "returning"):
            return
        if r.mission == "patrol":
            # 100 秒全林区覆盖巡逻航线（往复扫描）
            t = ((self.sim_time + (0 if r.id.endswith("1") else 50)) % 100) / 100.0
            cx = 0.10 + 0.80 * abs(2 * ((t * 5) % 1.0) - 1.0)
            cy = 0.14 + 0.72 * t
            dx, dy = cx - r.x, cy - r.y
            dist = max(0.001, math.hypot(dx, dy))
            step = 0.014 if r.kind == "UAV" else 0.008
            r.heading = math.atan2(dy, dx)
            r.x = min(0.92, max(0.06, r.x + (dx / dist) * min(step, dist)))
            r.y = min(0.92, max(0.06, r.y + (dy / dist) * min(step, dist)))
            return
        if r.mission == "recon":
            tx, ty = r.target_x, r.target_y
            dx, dy = tx - r.x, ty - r.y
            dist = math.hypot(dx, dy)
            if dist > 0.03:
                r.heading = math.atan2(dy, dx)
                r.x = min(0.94, max(0.04, r.x + (dx / dist) * 0.026))
                r.y = min(0.94, max(0.04, r.y + (dy / dist) * 0.026))
            else:
                r.mission = "idle"
                r.arrived = True
                recon_fire = next((f for f in self.fires if f.id == r.assigned_fire_id), None)
                if recon_fire and recon_fire.state == "suspicious":
                    recon_fire.state = "spreading"
                    self.push_alert(
                        f"无人机 {r.id} 现场勘察确认：火点 {recon_fire.id} 属实！",
                        f"热成像温度 418℃，建议立即调度灭火编队前往扑救",
                        "critical", f"{r.id} 空中侦察",
                    )
                    self.push_event(f"{r.id} 抵近勘察确认火点 {recon_fire.id} 属实，启动自动调度", "warning")
                    r.assigned_fire_id = ""
                    r.status = "standby"
                    self._ensure_dispatch(recon_fire.id)
                    self.recon_confirmed.emit(recon_fire)
            return

        if r.mission in ("en_route", "spraying"):
            tx, ty = r.target_x, r.target_y
            dx, dy = tx - r.x, ty - r.y
            dist = math.hypot(dx, dy)
            step = 0.022 if r.kind == "UAV" else 0.013
            if dist > 0.025:
                r.heading = math.atan2(dy, dx)
                r.x = min(0.94, max(0.04, r.x + (dx / dist) * step))
                r.y = min(0.94, max(0.04, r.y + (dy / dist) * step))
                r.arrived = False
                r.spraying = False
                r.eta_seconds = round(dist / max(0.005, step), 1)
                r.eta_status = "早到" if r.eta_seconds < 8 else ("准时" if r.eta_seconds < 18 else "晚到")
            else:
                r.arrived = True
                r.mission = "spraying"
                r.eta_seconds = 0.0
                r.eta_status = "已到达"
                r.spraying = True
                # 到达火线后小幅环绕/微调位置
                target_fire = next((f for f in self.fires if f.id == r.assigned_fire_id), None)
                if target_fire:
                    r.heading = math.atan2(target_fire.origin[1] - r.y, target_fire.origin[0] - r.x)
        elif r.mission == "returning":
            dx, dy = r.home_x - r.x, r.home_y - r.y
            dist = math.hypot(dx, dy)
            step = 0.020 if r.kind == "UAV" else 0.012
            if dist > 0.02:
                r.heading = math.atan2(dy, dx)
                r.x += (dx / dist) * step
                r.y += (dy / dist) * step
            else:
                r.x, r.y = r.home_x, r.home_y
                r.mission = "idle"
                r.status = "charging" if r.needs_refill else "standby"
                r.task = "基地补给中" if r.needs_refill else "待命"
                r.spraying = False
        else:
            if r.kind == "UAV":
                r.x = min(0.92, max(0.05, r.x + self.rng.uniform(-0.004, 0.004)))
                r.y = min(0.92, max(0.05, r.y + self.rng.uniform(-0.004, 0.004)))
            else:
                r.x = min(0.9, max(0.08, r.x + self.rng.uniform(-0.002, 0.002)))
                r.y = min(0.9, max(0.08, r.y + self.rng.uniform(-0.002, 0.002)))

    def trigger_suspicious_fire(self, origin: tuple[float, float] | None = None) -> FireIncident:
        """流程二：发现可疑火点 → 预警通知 → 派无人机前往勘察。"""
        if origin is None:
            ox = round(self.rng.uniform(0.28, 0.80), 3)
            oy = round(self.rng.uniform(0.26, 0.76), 3)
            origin = (ox, oy)
        self.fire_counter += 1
        fid = f"A-{self.fire_counter:02d}"
        intensity = round(self.rng.uniform(48.0, 68.0), 1)
        area = round(self.rng.uniform(4.2, 9.5), 1)
        self.fire_origin = origin
        self.fire = FireIncident(
            id=fid, origin=origin, intensity=intensity, area=area,
            containment=15.0, state="suspicious", ignited_at=self.sim_time,
            peak_intensity=intensity, peak_area=area,
            history=[intensity], area_history=[area],
        )
        self.fires.append(self.fire)
        self.fire_area = area
        self.containment = 15.0
        self._milestones.clear()
        self.last_report = None
        self.replan()

        scout = self._dispatch_scout(self.fire)
        detail = (f"已指派 {scout.id} 前往勘察" if scout else "暂无可用无人机，系统将自动重试")
        self.push_alert(
            f"火灾预警：发现可疑火点 {fid}",
            f"卫星/传感器发现异常热斑 ({origin[0]:.2f}, {origin[1]:.2f})，{detail}",
            "warning", "火灾预警系统",
        )
        return self.fire

    def _dispatch_scout(self, fire: FireIncident) -> Robot | None:
        if any(r.assigned_fire_id == fire.id and r.mission == "recon" and r.status != "offline"
               for r in self.robots):
            return None
        uavs = [r for r in self.robots if r.kind == "UAV" and r.status in ("standby", "on_mission")
                and r.mission in ("idle", "patrol") and not r.assigned_fire_id and r.battery >= 18.0]
        if not uavs:
            return None
        scout = min(uavs, key=lambda r: math.hypot(r.x - fire.origin[0], r.y - fire.origin[1]))
        scout.status = "on_mission"
        scout.mission = "recon"
        scout.task = f"勘察可疑火点 {fire.id}"
        scout.target_x, scout.target_y = fire.origin
        scout.assigned_fire_id = fire.id
        scout.spraying = False
        self.push_event(f"预警：{scout.id} 正在飞往可疑火点 {fire.id} 进行现场核查…", "info")
        return scout

    def recommend_dispatch(self, fire_id: str | None = None, *, store: bool = True) -> list[dict]:
        """生成指定活跃火点的推荐方案；store=False 用于只读预览。"""
        target_id = fire_id or self.fire.id
        fire = next((f for f in self.fires if f.id == target_id and f.state != "extinguished"), None)
        if fire is None:
            if store:
                self.dispatch_plan = []
            return []
        fx, fy = fire.origin
        candidates = [r for r in self.robots if r.status in ("standby", "on_mission")
                      and r.mission in ("idle", "patrol") and not r.assigned_fire_id
                      and r.battery >= 18.0 and r.water_l > 1.8]
        plan: list[dict] = []

        def score_robot(r: Robot, role: str) -> tuple[float, dict]:
            dist = math.hypot(r.x - fx, r.y - fy)
            dist_score = max(0.0, 100.0 * (1.0 - dist / 1.2))
            cap_score = (100.0 if r.kind == "UAV" else 35.0) if role == "recon" else (100.0 if r.kind == "UGV" else 55.0)
            total = 0.40 * cap_score + 0.25 * dist_score + 0.20 * r.battery + 0.15 * r.payload
            return round(total, 1), {"cap": round(cap_score, 0), "dist": round(dist, 2), "bat": round(r.battery, 0), "pay": round(r.payload, 0)}

        uavs = sorted([r for r in candidates if r.kind == "UAV"], key=lambda r: score_robot(r, "recon")[0], reverse=True)
        ugvs = sorted([r for r in candidates if r.kind == "UGV"], key=lambda r: score_robot(r, "suppress")[0], reverse=True)

        selected: list[tuple[Robot, str, str, tuple[float, float]]] = []
        if len(uavs) >= 1:
            selected.append((uavs[0], "recon", "空中侦察 · 热源锁定", (fx - 0.015, fy - 0.015)))
        if len(uavs) >= 2:
            selected.append((uavs[1], "recon", "空中洒水 · 压制火头", (fx + 0.015, fy - 0.015)))
        offsets = [(-0.02, 0.01), (0.02, 0.01), (0.0, 0.02)]
        h_dir = "东侧" if fx < 0.5 else "西侧"
        v_dir = "南线" if fy < 0.5 else "北线"
        ugv_tasks = ["火线正面强攻", f"{h_dir}隔离带阻断", f"{v_dir}洒水降温"]
        for idx, r in enumerate(ugvs[:3]):
            ox, oy = offsets[idx]
            selected.append((r, "suppress", ugv_tasks[idx], (fx + ox, fy + oy)))

        for r, role, task_name, (tx, ty) in selected:
            sc, bd = score_robot(r, role)
            plan.append({
                "robot_id": r.id, "name": r.name, "kind": r.kind, "fire_id": fire.id,
                "task": task_name, "score": sc,
                "tx": min(0.92, max(0.06, tx)), "ty": min(0.92, max(0.06, ty)),
                "reason": f"综合 {sc} 分（能力 {bd['cap']:.0f} · 距火点 {bd['dist']:.2f} · 电量 {bd['bat']:.0f}% · 载荷 {bd['pay']:.0f}%）",
            })
        if store:
            self.dispatch_plan = plan
        return plan

    def confirm_dispatch(self, selected_ids: list[str] | None = None, *,
                         fire_id: str | None = None, plan: list[dict] | None = None) -> list[dict]:
        """下发已确认方案，始终绑定方案所属火点，不覆盖其他火点的装备。"""
        target_id = fire_id or (plan[0].get("fire_id") if plan else None) or self.fire.id
        fire = next((f for f in self.fires if f.id == target_id and f.state != "extinguished"), None)
        if fire is None:
            return []
        if plan is None:
            plan = self.dispatch_plan
            if not plan or any(p.get("fire_id") != target_id for p in plan):
                plan = self.recommend_dispatch(target_id)
        id_map = {r.id: r for r in self.robots}
        chosen = []
        for p in plan:
            if p.get("fire_id") != target_id or (selected_ids is not None and p["robot_id"] not in selected_ids):
                continue
            r = id_map.get(p["robot_id"])
            if not r or r.status == "offline" or (r.assigned_fire_id and r.assigned_fire_id != target_id):
                continue
            r.status = "on_mission"
            r.mission = "en_route"
            r.task = p["task"]
            r.target_x = p["tx"]
            r.target_y = p["ty"]
            r.assigned_fire_id = target_id
            r.arrived = False
            r.spraying = False
            chosen.append(p)
        self.dispatch_plan = chosen
        if chosen:
            names = "、".join(p["robot_id"] for p in chosen)
            self.push_event(f"自动调度：{names} 前往扑救火点 {target_id}", "success")
            self.tick.emit()
        return chosen

    def ignite_random_fire(self, origin: tuple[float, float] | None = None, auto_notify: bool = False) -> FireIncident:
        """随机生成火点并自动调度，支持多火点。"""
        if origin is None:
            ox = round(self.rng.uniform(0.24, 0.80), 3)
            oy = round(self.rng.uniform(0.24, 0.76), 3)
            origin = (ox, oy)
        self.fire_counter += 1
        fid = f"A-{self.fire_counter:02d}"
        intensity = round(self.rng.uniform(58.0, 86.0), 1)
        area = round(self.rng.uniform(5.5, 13.0), 1)
        self.fire_origin = origin
        new_fire = FireIncident(
            id=fid,
            origin=origin,
            intensity=intensity,
            area=area,
            containment=10.0,
            state="spreading",
            ignited_at=self.sim_time,
            peak_intensity=intensity,
            peak_area=area,
            history=[intensity],
            area_history=[area],
        )
        self.fires.append(new_fire)
        self.fire = new_fire
        self.fire_area = round(sum(f.area for f in self.fires if f.state != "extinguished"), 1)
        self.containment = 10.0
        self._milestones.clear()
        self.last_report = None
        self.replan()
        self.push_alert(
            f"发现新火点 {fid}！",
            f"热成像定位 ({origin[0]:.2f}, {origin[1]:.2f}) · 初始强度 {intensity:.0f}% · 面积 {area:.1f} ha",
            "critical", "火灾预警系统",
        )
        self.push_event(f"火点 {fid} 触发警报，正在自动调度装备", "warning")
        if self.auto_dispatch and not self.estop:
            self._ensure_dispatch(fid)
        if auto_notify:
            self.fire_appeared.emit(new_fire)
        return new_fire

    def active_fire_robots(self, fire_id: str | None = None) -> list[Robot]:
        """返回正在执行活跃火点任务的装备，可按火点筛选。"""
        active_ids = {f.id for f in self.fires if f.state != "extinguished"}
        return [r for r in self.robots
                if r.assigned_fire_id in active_ids
                and (fire_id is None or r.assigned_fire_id == fire_id)
                and r.status == "on_mission" and r.mission in ("recon", "en_route", "spraying")]

    def _ensure_dispatch(self, fire_id: str) -> list[dict]:
        """为火点补足空地编队；无可用装备时后续仿真步自动重试。"""
        assigned = [r for r in self.robots if r.assigned_fire_id == fire_id
                    and r.mission in ("en_route", "spraying") and r.status != "offline"]
        needs = {"UAV": max(0, 2 - sum(r.kind == "UAV" for r in assigned)),
                 "UGV": max(0, 3 - sum(r.kind == "UGV" for r in assigned))}
        if not any(needs.values()):
            return []
        plan = self.recommend_dispatch(fire_id, store=False)
        selected = []
        for item in plan:
            if needs[item["kind"]] > 0:
                selected.append(item)
                needs[item["kind"]] -= 1
        return self.confirm_dispatch(fire_id=fire_id, plan=selected) if selected else []

    def evaluate_and_dispatch(self) -> list[dict]:
        """为当前活跃火点生成并执行自主调度，不影响其他火点的任务。"""
        return self._ensure_dispatch(self.fire.id)

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
               slope: float | None = None, algo: str = "RL-A*",
               start: tuple[float, float] | None = None,
               goal: tuple[float, float] | None = None) -> PathPlan:
        if wind_deg is not None:
            self.wind_deg = wind_deg
        if wind_speed is not None:
            self.wind_speed = wind_speed
        if slope is not None:
            self.slope = slope
        fx, fy = self.fire_origin
        st = start or (0.16, 0.78)
        gl = goal or (round(max(0.08, fx - 0.06), 3), round(min(0.88, fy + 0.05), 3))
        self.plan = self.planner.plan(st, gl, self.wind_deg,
                                      self.wind_speed, self.slope, self.fire_origin, algo)
        self.baseline = self.planner.plan(st, gl, self.wind_deg,
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
        if not any(f.state != "extinguished" for f in self.fires):
            return 0.0, 0.0, 100.0
        fire = min(99.4, self.fire_confidence + math.sin(self.started_at.second / 4) * 1.2)
        smoke = min(99.0, 88.0 + math.cos(self.started_at.second / 5) * 2.4)
        normal = max(0.6, 100 - fire - smoke * 0.18)
        return fire, smoke, max(0.4, normal)
