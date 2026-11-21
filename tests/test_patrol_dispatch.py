"""巡逻航带完成前不被火情调度，安全返航后继续。"""
import unittest
import math
from PySide6.QtCore import QCoreApplication
from app.simulation import GRID_H, GRID_W, PATROL_WAYPOINTS, SimEngine


class PatrolDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        self.engine = SimEngine()
        self.engine.timer.stop()

    def tearDown(self):
        self.engine.timer.stop()

    def test_patrol_survives_fire_scout_and_completes_all_waypoints(self):
        e = self.engine
        patrols = [r for r in e.robots if r.mission == 'patrol']
        fire = e.ignite_random_fire((.5, .5))
        suspicious = e.trigger_suspicious_fire((.6, .5))
        self.assertTrue(all(r.mission == 'patrol' and not r.assigned_fire_id for r in patrols))
        self.assertTrue(e.active_fire_robots(fire.id))
        self.assertTrue(any(r.mission == 'recon' and r.assigned_fire_id == suspicious.id for r in e.robots))
        r = patrols[0]
        visited = []
        for _ in range(5000):
            old = r.patrol_index
            e._advance_robot(r)
            if r.patrol_index != old or r.mission != 'patrol':
                visited.append((r.x, r.y))
            if r.mission != 'patrol':
                break
        self.assertEqual(r.mission, 'returning')
        self.assertEqual(visited[:len(PATROL_WAYPOINTS)], list(PATROL_WAYPOINTS))
        self.assertGreater(len(visited), len(PATROL_WAYPOINTS))  # 火点绕行后补扫漏检栅格
        self.assertFalse(r.patrol_incomplete)
        self.assertEqual(r.task, '巡逻一轮完成 · 返回基地')

    def test_real_tick_patrol_scans_entire_map_with_demonstration_footprint(self):
        e = self.engine
        patrols = [r for r in e.robots if r.mission == 'patrol']
        samples = {r.id: [(r.x, r.y)] for r in patrols}
        completed = set()
        for _ in range(400):
            e._step_sim()
            for r in patrols:
                if r.id not in completed:
                    samples[r.id].append((r.x, r.y))
                    if not r.patrol_incomplete:
                        completed.add(r.id)
            if len(completed) == len(patrols):
                break
        self.assertEqual(completed, {r.id for r in patrols})
        # 演示中传感器半径设为 0.11 地图单位；检查整个栅格中心，非仅检查航点。
        for r in patrols:
            for y in range(GRID_H):
                for x in range(GRID_W):
                    center = ((x + .5) / GRID_W, (y + .5) / GRID_H)
                    self.assertTrue(any(math.dist(center, p) <= .11 for p in samples[r.id]),
                                    f"{r.id} 未覆盖栅格 {(x, y)}")

    def test_patrol_rotates_base_pairs_only_after_both_finish(self):
        e = self.engine
        self.assertEqual({rid[0] for rid in e.patrol_members}, {'A', 'C'})
        initial = set(e.patrol_members)
        for _ in range(450):
            e._step_sim()
            if len(e.patrol_completed) == 1:
                self.assertEqual(e.patrol_members, initial)
                self.assertEqual(e.patrol_round, 0)
            if e.patrol_round == 1 and e.patrol_members:
                break
        self.assertEqual(e.patrol_round, 1)
        self.assertEqual({rid[0] for rid in e.patrol_members}, {'B', 'D'})
        self.assertEqual(len(e.patrol_members), 2)
        for _ in range(450):
            e._step_sim()
            if e.patrol_round == 2 and e.patrol_members:
                break
        self.assertEqual(e.patrol_round, 2)
        self.assertEqual({rid[0] for rid in e.patrol_members}, {'A', 'C'})
        self.assertEqual(len(e.patrol_members), 2)
        e.reset_session()
        self.assertEqual(e.patrol_round, 0)
        self.assertEqual({rid[0] for rid in e.patrol_members}, {'A', 'C'})

    def test_offline_patrol_uses_same_base_and_preserves_progress(self):
        e = self.engine
        unit = next(r for r in e.robots if r.id in e.patrol_members)
        unit.patrol_index = 3
        unit.patrol_seen = {(1, 2), (3, 4)}
        unit.status = 'offline'
        e._step_sim()
        replacement = next(r for r in e.robots if r.id in e.patrol_members and r.home_x == unit.home_x)
        self.assertNotEqual(replacement.id, unit.id)
        self.assertEqual(replacement.mission, 'patrol')
        self.assertEqual(replacement.patrol_index, 3)
        self.assertTrue({(1, 2), (3, 4)} <= replacement.patrol_seen)
        self.assertFalse(unit.patrol_incomplete)

    def test_next_pair_waits_when_base_has_no_available_uav(self):
        e = self.engine
        e.patrol_completed = set(e.patrol_members)
        for r in e.robots:
            if r.kind == 'UAV' and r.home_x == .14:
                r.status = 'offline'
        e._manage_patrol_rotation()
        self.assertEqual(e.patrol_round, 1)
        self.assertEqual(e.patrol_members, set())
        e._manage_patrol_rotation()
        self.assertEqual(e.patrol_round, 1)
        r = next(r for r in e.robots if r.kind == 'UAV' and r.home_x == .14)
        r.status = 'standby'
        e._manage_patrol_rotation()
        self.assertEqual({rid[0] for rid in e.patrol_members}, {'B', 'D'})

    def test_interrupted_patrol_not_assigned_before_resume(self):
        e = self.engine
        r = next(r for r in e.robots if r.mission == 'patrol')
        r.patrol_index = 3
        r.x, r.y = .3, .4
        r.battery = 29
        e._step_sim()
        self.assertTrue(r.patrol_incomplete)
        self.assertEqual(r.status, 'returning')
        e.auto_dispatch = False
        r.x, r.y = r.home_x, r.home_y
        r.route_goal = None
        r.battery, r.water_l = 100, r.water_cap
        # 仅保留该设备，验证休整结束后按原进度续巡。
        for other in e.robots:
            if other is not r:
                other.status, other.mission = 'offline', 'idle'
        for _ in range(8):
            e._step_sim()
            if r.mission == 'patrol':
                break
        self.assertEqual(r.mission, 'patrol')
        self.assertEqual(r.patrol_index, 3)
        fire = e.ignite_random_fire((.5, .5))
        e.auto_dispatch = True
        e._ensure_dispatch(fire.id)
        self.assertFalse(r.assigned_fire_id)
        self.assertEqual(r.mission, 'patrol')


if __name__ == '__main__':
    unittest.main()
