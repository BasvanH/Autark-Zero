"""Class for tests."""
import unittest

import numpy as np
from shapely.geometry import Point

from ..boat import Boat
from ..path_finder import checkCollision
from ..path_finder import computeDirection


class TestPathFinder(unittest.TestCase):
    """Class for tests."""
    def compute_direction_basic_tacking(self):
        """Simple test."""
        bearing_angle = 130
        wind_dir = 195
        wind_speed = 25
        boat_speed = 0

        # Basic test, no boat speed, no weird angle
        dir_left, dir_right = computeDirection(bearing_angle, wind_dir,
                                               wind_speed, boat_speed)
        self.assertAlmostEqual(dir_left, 160)
        self.assertAlmostEqual(dir_right, 230)

        wind_dir = 350
        bearing_angle = 320
        # Basic test, no boat speed, weird angle
        dir_left, dir_right = computeDirection(bearing_angle, wind_dir,
                                               wind_speed, boat_speed)
        self.assertAlmostEqual(dir_left, 315)
        self.assertAlmostEqual(dir_right, 25)

    def compute_direction_complex_tacking(self):
        """Simple test."""
        bearing_angle = 130
        wind_dir = 195
        wind_speed = 25
        boat_speed = 5

        # Basic test, boat speed, no weird angle
        dir_left, dir_right = computeDirection(bearing_angle, wind_dir,
                                               wind_speed, boat_speed)
        self.assertAlmostEqual(dir_left, 171.19, places=1)
        self.assertAlmostEqual(dir_right, 241.19, places=1)

        wind_dir = 350
        bearing_angle = 320
        # Basic test, boat speed, weird angle
        dir_left, dir_right = computeDirection(bearing_angle, wind_dir,
                                               wind_speed, boat_speed)
        self.assertAlmostEqual(dir_left, 321.89, places=1)
        self.assertAlmostEqual(dir_right, 31.89, places=1)

    def compute_direction_basic_noTacking(self):
        """Simple test."""
        bearing_angle = 105
        wind_dir = 195
        wind_speed = 25
        boat_speed = 0

        # Basic test, no boat speed, no weird angle
        dir_left, dir_right = computeDirection(bearing_angle, wind_dir,
                                               wind_speed, boat_speed)
        self.assertAlmostEqual(dir_left, 195, places=1)
        self.assertAlmostEqual(dir_right, 195, places=1)

        wind_dir = 350
        bearing_angle = 80
        # Basic test, no boat speed, weird angle
        dir_left, dir_right = computeDirection(bearing_angle, wind_dir,
                                               wind_speed, boat_speed)
        self.assertAlmostEqual(dir_left, 350, places=1)
        self.assertAlmostEqual(dir_right, 350, places=1)

    def compute_direction_complex_noTacking(self):
        """Simple test."""
        bearing_angle = 114
        wind_dir = 195
        wind_speed = 25
        boat_speed = 5

        # Basic test, boat speed, no weird angle
        dir_left, dir_right = computeDirection(bearing_angle, wind_dir,
                                               wind_speed, boat_speed)
        self.assertAlmostEqual(dir_left, 206.52, places=1)
        self.assertAlmostEqual(dir_right, 206.52, places=1)

        wind_dir = 350
        bearing_angle = 80
        # Basic test, boat speed, weird angle
        dir_left, dir_right = computeDirection(bearing_angle, wind_dir,
                                               wind_speed, boat_speed)
        self.assertAlmostEqual(dir_left, 338.69, places=1)
        self.assertAlmostEqual(dir_right, 338.69, places=1)

    def check_collision_basic_collision(self):
        """Simple test."""
        p1 = Point(43.519186, 28.947210)
        p2 = Point(43.44928, 28.67030)
        # p3 = Point(43.417136, 28.880129)
        boat = Boat(23, Point(43.557784, 28.730186),
                    Point(43.417136, 28.880129))
        boat.extend(Point(53.417136, 45.880129))
        boat.extend(Point(43.417136, 28.880129))
        boats = np.array([boat])
        res = checkCollision(p1, p2, boats, 32)
        self.assertAlmostEqual(
            res.get('collision_coords').lat, 43.485350025428275)
        self.assertAlmostEqual(
            res.get('collision_coords').lon, 28.81755292942671)

        # check if same id condition holds
        res = checkCollision(p1, p2, boats, boat._id)
        self.assertEqual(res.get('collision'), False)

    def check_collision_basic_nocollision(self):
        """Simple test."""
        p1 = Point(40.519186, 28.47210)
        p2 = Point(39.44928, 27.67030)
        # p3 = Point(43.417136, 28.880129)
        # p4 = Point(43.417136, 28.880129)
        boat = Boat(23, Point(43.557784, 28.730186),
                    Point(43.417136, 28.880129))
        boat.extend(Point(43.417136, 28.880129))
        boats = np.array([boat])
        res = checkCollision(p1, p2, boats, boat._id)
        self.assertAlmostEqual(res.get('collision'), False, places=1)


def suite():
    """Suite."""
    suite = unittest.TestSuite()
    suite.addTest(TestPathFinder('compute_direction_basic_tacking'))
    suite.addTest(TestPathFinder('compute_direction_complex_tacking'))
    suite.addTest(TestPathFinder('compute_direction_complex_noTacking'))
    suite.addTest(TestPathFinder('compute_direction_complex_noTacking'))
    suite.addTest(TestPathFinder('check_collision_basic_collision'))
    suite.addTest(TestPathFinder('check_collision_basic_nocollision'))
    # suite.addTest(TestPathFinder('compute_maximal_distance_basic'))
    return suite


if __name__ == '__main__':
    """If."""
    # runner = unittest.TextTestRunner()
    # runner.run(suite())
    unittest.main()
