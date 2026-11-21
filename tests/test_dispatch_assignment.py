"""自动调度、多火点扑救与补给的仿真回归测试。"""
import unittest
from PySide6.QtCore import QCoreApplication
from app.simulation import SimEngine


class DispatchAssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        self.engine = SimEngine()
        self.engine.timer.stop()

    def tearDown(self):
        self.engine.timer.stop()

    def test_fire_automatically_assigned_and_extinguished(self):
        e = self.engine
        fire = e.ignite_random_fire((0.5, 0.5))
        assigned = [r for r in e.robots if r.assigned_fire_id == fire.id]
        self.assertEqual(sum(r.kind == 'UAV' for r in assigned), 2)
        self.assertEqual(sum(r.kind == 'UGV' for r in assigned), 3)
        for _ in range(180):
            e._step_sim()
            if fire.state == 'extinguished':
                break
        self.assertEqual(fire.state, 'extinguished')
        self.assertGreater(fire.water_used_l, 0)
        self.assertTrue(all(not r.assigned_fire_id for r in assigned))
        self.assertTrue(all(r.mission == 'returning' for r in assigned))

    def test_multiple_fires_have_distinct_forces_and_are_extinguished(self):
        e = self.engine
        fires = [e.ignite_random_fire(pos) for pos in ((.25, .25), (.75, .75), (.5, .5))]
        teams = [{r.id for r in e.robots if r.assigned_fire_id == fire.id} for fire in fires]
        self.assertTrue(all(len(team) == 5 for team in teams))
        self.assertFalse(teams[0] & teams[1] or teams[1] & teams[2] or teams[0] & teams[2])
        for _ in range(200):
            e._step_sim()
            if all(f.state == 'extinguished' for f in fires):
                break
        self.assertTrue(all(f.state == 'extinguished' and f.water_used_l > 0 for f in fires))

    def test_suspicious_fire_recon_then_automatic_response(self):
        e = self.engine
        fire = e.trigger_suspicious_fire((0.5, 0.5))
        self.assertEqual(fire.state, 'suspicious')
        self.assertTrue(any(r.mission == 'recon' and r.assigned_fire_id == fire.id for r in e.robots))
        for _ in range(200):
            e._step_sim()
            if fire.state == 'extinguished':
                break
        self.assertEqual(fire.state, 'extinguished')
        self.assertGreater(fire.water_used_l, 0)

    def test_empty_tank_does_not_suppress_and_triggers_refill(self):
        e = self.engine
        fire = e.ignite_random_fire((0.5, 0.5))
        unit = next(r for r in e.robots if r.assigned_fire_id == fire.id)
        for r in e.robots:
            if r is not unit:
                r.status = 'offline'
        unit.x, unit.y = unit.target_x, unit.target_y
        unit.water_l = 0
        before = fire.intensity
        e._step_sim()
        self.assertEqual(fire.suppression_rate, 0)
        self.assertGreater(fire.intensity, before)
        self.assertEqual(unit.mission, 'returning')
        self.assertTrue(unit.needs_refill)
        self.assertEqual(unit.assigned_fire_id, '')
        for _ in range(150):
            e._step_sim()
            if not unit.needs_refill:
                break
        self.assertFalse(unit.needs_refill)
        self.assertGreater(unit.water_l, 0)


if __name__ == '__main__':
    unittest.main()
