"""协作日志只记录实际发生的调度、接替及扑灭事件。"""
import unittest
from PySide6.QtCore import QCoreApplication
from app.simulation import SimEngine, ROBOT_OVERHEAT_TEMP


class CollaborationEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        self.e = SimEngine()
        self.e.timer.stop()

    def tearDown(self):
        self.e.timer.stop()

    def test_multi_fire_and_handoff_log(self):
        e = self.e
        first = e.ignite_random_fire((.3, .4))
        second = e.ignite_random_fire((.7, .4))
        for fire in (first, second):
            events = [x for x in e.collaboration_events if x['fire_id'] == fire.id]
            self.assertEqual(sum(x['kind'] == '发现' for x in events), 1)
            dispatched = [x for x in events if x['kind'] == '派遣']
            self.assertEqual(len(dispatched), 5)
            self.assertEqual({x['robots'][0] for x in dispatched},
                             {r.id for r in e.active_fire_robots(fire.id)})
        unit = next(r for r in e.active_fire_robots(first.id) if r.kind == 'UGV')
        unit.temp = ROBOT_OVERHEAT_TEMP + 1
        e._step_sim()
        handoff = next(x for x in e.collaboration_events if x['kind'] == '接替' and x['robots'][0] == unit.id)
        self.assertEqual(handoff['fire_id'], first.id)
        replacement = next(r for r in e.robots if r.id == handoff['robots'][1])
        self.assertEqual(replacement.assigned_fire_id, first.id)
        self.assertEqual(replacement.task, handoff['text'].split('：', 1)[1])
        self.assertTrue(any(x['kind'] == '退出' and x['robots'] == (unit.id,) for x in e.collaboration_events))

    def test_water_exhaustion_records_handoff(self):
        e = self.e
        fire = e.ignite_random_fire((.5, .5))
        unit = next(r for r in e.active_fire_robots(fire.id) if r.kind == 'UGV')
        original_task = unit.task
        unit.x, unit.y = unit.target_x, unit.target_y
        unit.route_goal = None
        unit.water_l = 0
        e._step_sim()
        self.assertTrue(any(x['kind'] == '退出' and x['fire_id'] == fire.id
                            and x['robots'] == (unit.id,) and '水量耗尽' in x['text']
                            for x in e.collaboration_events))
        handoff = next(x for x in e.collaboration_events if x['kind'] == '接替' and x['robots'][0] == unit.id)
        replacement = next(r for r in e.robots if r.id == handoff['robots'][1])
        self.assertEqual(replacement.task, original_task)

    def test_scout_wait_does_not_repeat_each_step(self):
        e = self.e
        for r in e.robots:
            if r.kind == 'UAV':
                r.status = 'offline'
        fire = e.trigger_suspicious_fire((.5, .5))
        for _ in range(3):
            e._step_sim()
        self.assertEqual(len([x for x in e.collaboration_events if x['kind'] == '等待侦察'
                              and x['fire_id'] == fire.id]), 1)

    def test_shortage_is_deduplicated_and_reset_clears_history(self):
        e = self.e
        for r in e.robots:
            r.status = 'offline'
        fire = e.ignite_random_fire((.5, .5))
        for _ in range(4):
            e._step_sim()
        events = [x for x in e.collaboration_events if x['kind'] == '等待补派' and x['fire_id'] == fire.id]
        self.assertEqual(len(events), 1)
        e.reset_session()
        self.assertEqual(e.collaboration_events, [])
        self.assertEqual(e._collaboration_shortages, {})

    def test_extinguish_record_before_assignment_is_cleared(self):
        e = self.e
        fire = e.ignite_random_fire((.5, .5))
        for r in e.active_fire_robots(fire.id):
            r.x, r.y = r.target_x, r.target_y
            r.route_goal = None
        fire.intensity = .1
        e._step_sim()
        event = next(x for x in e.collaboration_events if x['kind'] == '扑灭' and x['fire_id'] == fire.id)
        self.assertEqual(fire.state, 'extinguished')
        self.assertTrue(event['robots'])
        self.assertTrue(all(not r.assigned_fire_id for r in e.robots if r.id in event['robots']))


if __name__ == '__main__':
    unittest.main()
