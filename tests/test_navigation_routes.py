"""每设备路线设置、运动与不可达行为。"""
import math
import unittest
from PySide6.QtCore import QCoreApplication
from app.simulation import SimEngine


class NavigationRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        self.e = SimEngine()
        self.e.timer.stop()

    def tearDown(self):
        self.e.timer.stop()

    def test_per_robot_algorithm_and_shared_motion(self):
        e = self.e
        a, b = e.robots[0], e.robots[1]
        for robot in (a, b):
            robot.status, robot.mission = "on_mission", "en_route"
            robot.target_x, robot.target_y = .5, .5
        fire = e.ignite_random_fire((.5, .5))
        for robot in (a, b):
            robot.assigned_fire_id = fire.id
            robot.target_x, robot.target_y = .5, .5
            robot.mission = "en_route"
        e.configure_robot_route(a.id, "Dijkstra", 200, 5, .2)
        e.configure_robot_route(b.id, "A*", 220, 3, .4)
        self.assertEqual(a.route_plan.algo, "Dijkstra")
        self.assertEqual(b.route_plan.algo, "A*")
        before_b = list(b.route)
        route = e.remaining_route(a)
        self.assertGreater(len(route), 2)
        start = (a.x, a.y)
        e._advance_robot(a)
        self.assertNotEqual((a.x, a.y), start)
        # Movement must lie on one of the planned polyline segments.
        self.assertTrue(any(abs(math.dist(x, (a.x, a.y)) + math.dist((a.x, a.y), y) - math.dist(x, y)) < 1e-8
                            for x, y in zip(route, route[1:])))
        e.configure_robot_route(a.id, "RL-A*", 180, 10, .7)
        self.assertEqual(a.route[0], (a.x, a.y))
        self.assertEqual(a.route_plan.algo, "RL-A*")
        self.assertEqual(b.route, before_b)
        self.assertEqual(b.route_algo, "A*")

    def test_unreachable_goal_stops_instead_of_straight_line(self):
        e = self.e
        r = next(robot for robot in e.robots if robot.kind == "UGV")
        fire = e.ignite_random_fire((.25, .25))
        r.assigned_fire_id = fire.id
        r.status, r.mission = "on_mission", "en_route"
        r.target_x, r.target_y = fire.origin
        r.route_goal = None
        e._ensure_robot_route(r)
        self.assertTrue(r.route_failed)
        self.assertEqual(e.remaining_route(r), [])
        before = r.x, r.y
        for _ in range(5):
            e._advance_robot(r)
        self.assertEqual((r.x, r.y), before)
        self.assertFalse(r.spraying)

    def test_return_uses_selected_algorithm_and_changes_goal(self):
        e = self.e
        r = e.robots[0]
        fire = e.ignite_random_fire((.5, .5))
        r = e.active_fire_robots(fire.id)[0]
        e.configure_robot_route(r.id, "Dijkstra", 230, 4, .3)
        e._advance_robot(r)
        e.return_robot(r)
        self.assertEqual(r.route_goal, (r.home_x, r.home_y))
        self.assertEqual(r.route_plan.algo, "Dijkstra")
        self.assertEqual(r.assigned_fire_id, "")
        self.assertEqual(e.remaining_route(r)[0], (r.x, r.y))


if __name__ == "__main__":
    unittest.main()
