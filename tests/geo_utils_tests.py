"""Houses unit tests for geo utils methods."""
import unittest

from shapely.geometry import Point

from src import geo_utils


class TestGeoUtils(unittest.TestCase):
    """Test case class for geo utils."""
    def test_haversine_dist(self):
        """Tests the haversine_dist method."""
        dist = geo_utils.haversine_dist(Point(45.3425, 50.5678),
                                        Point(45.2573, 51.7325))
        self.assertAlmostEqual(dist, 129600, delta=100)

    def test_bearing(self):
        """Tests the bearing method."""
        bearing = geo_utils.bearing(Point(50, 50), Point(51, 50.5))
        self.assertAlmostEqual(bearing, 51.584, delta=0.01)

    def test_distance_points(self):
        """Tests the distance_points method."""
        dist = geo_utils.distance_points(Point(0, 0), Point(3, 4))
        self.assertEqual(dist, 5)

    def test_distance_points2(self):
        """Tests the distance_points2 method."""
        gen_point = geo_utils.distance_points2(Point(50, 50), 143, 56700)
        real_point = Point(50.4667, 49.58334)
        self.assertAlmostEqual(gen_point.x, real_point.x, delta=0.01)
        self.assertAlmostEqual(gen_point.y, gen_point.y, delta=0.01)


if __name__ == "__main__":
    unittest.main()
