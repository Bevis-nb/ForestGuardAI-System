"""自动调度、多火点扑救与补给的仿真回归测试。"""
import unittest
from PySide6.QtCore import QCoreApplication
from app.simulation import ROBOT_OVERHEAT_TEMP, ROBOT_RECOVERY_TEMP, SimEngine, robot_health_risk


class DispatchAssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        self.engine = SimEngine()
        self.engine.timer.stop()

    def tearDown(self):
        self.engine.timer.stop()

    def test_health_risk_orders_temperature_and_battery(self):
        unit = self.engine.robots[0]
        unit.battery, unit.temp = 80, 30
        self.assertEqual(robot_health_risk(unit), 0)
        unit.battery = 30
        self.assertEqual(robot_health_risk(unit), 0.5)
        unit.battery, unit.temp = 80, 50
        self.assertEqual(robot_health_risk(unit), 0.5)
        unit.battery, unit.temp = 20, 30
        self.assertEqual(robot_health_risk(unit), 1)
        unit.battery, unit.temp = 80, ROBOT_OVERHEAT_TEMP
        self.assertEqual(robot_health_risk(unit), 1)
        unit.battery, unit.temp = 10, 50
        self.assertGreater(robot_health_risk(unit), 1)

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
        self.assertTrue(all(r.assigned_fire_id != fire.id for r in e.robots))

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

    def test_live_active_force_count_across_fires_and_states(self):
        e = self.engine
        first = e.ignite_random_fire((.3, .3))
        second = e.ignite_random_fire((.7, .7))
        self.assertEqual(len(e.active_fire_robots()), 10)
        self.assertEqual(len(e.active_fire_robots(first.id)), 5)
        self.assertEqual(len(e.active_fire_robots(second.id)), 5)
        unit = e.active_fire_robots(first.id)[0]
        unit.status = 'offline'
        self.assertEqual(len(e.active_fire_robots(first.id)), 4)
        self.assertEqual(len(e.active_fire_robots()), 9)
        unit.status = 'on_mission'
        unit.mission = 'returning'
        self.assertEqual(len(e.active_fire_robots(first.id)), 4)
        first.state = 'extinguished'
        self.assertEqual(len(e.active_fire_robots(first.id)), 0)
        self.assertEqual(len(e.active_fire_robots()), 5)

    def test_overheated_firefighter_returns_and_same_task_is_reassigned(self):
        e = self.engine
        first = e.ignite_random_fire((.3, .3))
        second = e.ignite_random_fire((.7, .7))
        unit = next(r for r in e.active_fire_robots(first.id) if r.kind == "UGV")
        other_team = {r.id for r in e.active_fire_robots(second.id)}
        previous_team = {r.id for r in e.active_fire_robots(first.id)}
        old_task, old_target = unit.task, (unit.target_x, unit.target_y)
        unit.x, unit.y = unit.target_x, unit.target_y
        unit.mission, unit.spraying = "spraying", True
        unit.temp = ROBOT_OVERHEAT_TEMP
        e._step_sim()
        self.assertEqual(unit.mission, "returning")
        self.assertEqual(unit.status, "returning")
        self.assertFalse(unit.spraying)
        self.assertEqual(unit.assigned_fire_id, "")
        self.assertTrue(unit.thermal_rest)
        replacement = next(r for r in e.active_fire_robots(first.id) if r.id not in previous_team)
        self.assertEqual(replacement.kind, unit.kind)
        self.assertEqual(replacement.task, old_task)
        self.assertEqual((replacement.target_x, replacement.target_y), old_target)
        self.assertEqual({r.id for r in e.active_fire_robots(second.id)}, other_team)
        self.assertTrue(any("接替" in event["text"] for event in e.events))

    def test_cooling_requires_base_and_safe_temperature_before_reuse(self):
        e = self.engine
        fire = e.ignite_random_fire((.5, .5))
        unit = e.active_fire_robots(fire.id)[0]
        unit.x, unit.y = unit.target_x, unit.target_y
        unit.temp = ROBOT_OVERHEAT_TEMP + 1
        e._step_sim()
        e.auto_dispatch = False
        self.assertTrue(unit.thermal_rest)
        # Simulate arrival; a hot unit may not be recommended, even if manually marked standby.
        unit.status, unit.mission = "standby", "idle"
        self.assertNotIn(unit.id, {p["robot_id"] for p in e.recommend_dispatch(fire.id, store=False)})
        unit.status, unit.mission = "returning", "returning"
        unit.x, unit.y = unit.home_x, unit.home_y
        unit.temp = 52
        unit.water_l, unit.battery = unit.water_cap, 80
        e._step_sim()
        self.assertEqual(unit.status, "charging")
        self.assertTrue(unit.thermal_rest)
        e._step_sim()
        self.assertTrue(unit.thermal_rest)
        self.assertGreater(unit.temp, ROBOT_RECOVERY_TEMP)
        for _ in range(20):
            e._step_sim()
            if not unit.thermal_rest:
                break
        self.assertFalse(unit.thermal_rest)
        self.assertLessEqual(unit.temp, ROBOT_RECOVERY_TEMP)
        self.assertEqual(unit.status, "standby")
        self.assertEqual((unit.x, unit.y), (unit.home_x, unit.home_y))

    def test_recon_uav_is_replaced_after_overheating(self):
        e = self.engine
        fire = e.trigger_suspicious_fire((.5, .5))
        scout = next(r for r in e.robots if r.assigned_fire_id == fire.id and r.mission == "recon")
        scout.temp = ROBOT_OVERHEAT_TEMP
        e._step_sim()
        self.assertTrue(scout.thermal_rest)
        self.assertIn(scout.status, ("returning", "charging"))
        replacement = next(r for r in e.robots if r.assigned_fire_id == fire.id and r.mission == "recon")
        self.assertNotEqual(replacement.id, scout.id)

    def test_handoff_retries_if_no_healthy_unit_is_available(self):
        e = self.engine
        fire = e.ignite_random_fire((.5, .5))
        unit = next(r for r in e.active_fire_robots(fire.id) if r.kind == "UGV")
        task = unit.task
        spare = next(r for r in e.robots if r.kind == "UGV" and not r.assigned_fire_id)
        for r in e.robots:
            if r is not unit:
                r.status = "offline"
        unit.temp = ROBOT_OVERHEAT_TEMP
        e._step_sim()
        self.assertTrue(any(h["from_id"] == unit.id for h in e._pending_handoffs))
        spare.status, spare.mission = "standby", "idle"
        e._step_sim()
        self.assertEqual(spare.assigned_fire_id, fire.id)
        self.assertEqual(spare.task, task)
        self.assertFalse(any(h["from_id"] == unit.id for h in e._pending_handoffs))

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
