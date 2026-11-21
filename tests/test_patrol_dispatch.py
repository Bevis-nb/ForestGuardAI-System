"""巡逻航带完成前不被火情调度，安全返航后继续。"""
import unittest
from PySide6.QtCore import QCoreApplication
from app.simulation import PATROL_WAYPOINTS, SimEngine


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
            if r.patrol_index != old or r.mission == 'idle':
                visited.append((r.x, r.y))
            if r.mission == 'idle':
                break
        self.assertEqual(r.mission, 'idle')
        self.assertEqual(visited, list(PATROL_WAYPOINTS))
        self.assertFalse(r.patrol_incomplete)
        self.assertEqual(r.task, '巡逻一轮完成 · 待命')

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
