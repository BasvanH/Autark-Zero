"""Class for tests."""
import unittest

from shapely.geometry import Point

from ..base_path import BasePath


def getTuple(p: Point):
    """Converts point to tuple."""
    return (p.x, p.y)


class TestBasePath(unittest.TestCase):
    """Class for tests."""
    origin = Point(0, 0)
    destination = Point(5, 5)

    def test_simple(self):
        """Simple test."""
        path = BasePath(self.origin, self.destination)
        self.assertEqual(self.origin, path._origin)
        self.assertEqual(self.destination, path._destination)
        self.assertEqual(self.origin, path._last_known_loc)
        self.assertEqual(0, len(path._path))

    def test_get_origin(self):
        """Simple test."""
        path = BasePath(self.origin, self.destination)
        self.assertEqual((0, 0), (path.get_origin().x, path.get_origin().y))

    def test_get_destination(self):
        """Simple test."""
        path = BasePath(self.origin, self.destination)
        self.assertEqual((5, 5),
                         (path.get_destination().x, path.get_destination().y))

    def test_get_path(self):
        """Simple test."""
        path_finder = BasePath(self.origin, self.destination)
        path = path_finder.get_path()
        self.assertEqual(0, len(path))
        path.append(Point(4, 12))
        self.assertEqual(0, len(path_finder.get_path()))

    def test_get_path_extra(self):
        """Simple test."""
        path_finder = BasePath(self.origin, self.destination)
        path_finder.extend(Point(4, 12))
        path = path_finder.get_path()
        self.assertEqual(1, len(path))
        path.append(Point(4, 12))
        self.assertEqual(1, len(path_finder.get_path()))

    def test_extend_path(self):
        """Simple test."""
        path_finder = BasePath(self.origin, self.destination)
        self.assertEqual(0, len(path_finder.get_path()))

        # These don't need to make sense at all...
        path_finder.extend(Point(4, 19))
        path_finder.extend(Point(9, 12))
        path_finder.extend(Point(4, 4))

        self.assertEqual(3, len(path_finder.get_path()))

    def test_pop(self):
        """Simple test."""
        path_finder = BasePath(self.origin, self.destination)

        # These don't need to make sense at all...
        path_finder.extend(Point(4, 19))
        path_finder.extend(Point(9, 12))
        path_finder.extend(Point(4, 4))

        self.assertEqual((4, 19), getTuple(path_finder.pop()))
        self.assertEqual((9, 12), getTuple(path_finder.pop()))
        self.assertEqual((4, 4), getTuple(path_finder.pop()))

    def test_add_to_front(self):
        """Simple test."""
        path_finder = BasePath(self.origin, self.destination)

        # These don't need to make sense at all...
        path_finder.extend(Point(4, 19))
        path_finder.extend(Point(9, 12))
        path_finder.extend(Point(4, 4))

        self.assertEqual((4, 19), getTuple(path_finder.pop()))
        self.assertEqual((9, 12), getTuple(path_finder.pop()))

        path_finder.add_to_front(Point(9, 4))
        path_finder.add_to_front(Point(5, 5))

        self.assertEqual((5, 5), getTuple(path_finder.pop()))
        self.assertEqual((9, 4), getTuple(path_finder.pop()))
        self.assertEqual((4, 4), getTuple(path_finder.pop()))

    def test_get_route(self):
        """Simple test."""
        path_finder = BasePath(self.origin, self.destination)

        path_finder.extend(Point(4, 19))
        path_finder.extend(Point(9, 12))
        path_finder.extend(Point(4, 4))
        path_finder.add_to_front(Point(9, 4))
        path_finder.add_to_front(Point(5, 5))

        # self.assertRaises(NotImplementedError, path_finder.get_route)


if __name__ == "__main__":
    unittest.main()
