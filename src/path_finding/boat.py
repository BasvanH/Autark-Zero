"""Class for boat."""
import typing

from path_finding import base_path
from shapely.geometry import Point
from singleton_metaclass import Singleton


class Boat(base_path.BasePath, metaclass=Singleton):
    """Defines a structure that stores the boat Id.

    waypoints, last known location and direction headed,
    maybe other variables in the future.
    """
    def __init__(self, *args, **kwargs) -> None:
        """Add new waypoint.

        - lat: latitude of the new waypoint
        - long: longitude of the new waypoint
        """
        if kwargs is not None:
            id = kwargs.get("id")
            origin = kwargs.get("origin")
            destination = kwargs.get("destination")
            super().__init__(origin, destination)
            self._id = id
            self._mid_points = typing.Deque[Point]()
            self._wait_time = 0.
            self._tacking = False
            self._tacking_upper_limit = 0.
            self._tacking_down_limit = 0.
            self._final_destination = destination
            self._path: typing.Deque[Point] = typing.Deque()
            self._collision = False
            self._wp_index = 0
            self._past_wp: typing.List[Point] = list()
            self._bearing = 0.
        else:
            pass

    def extend_mid_point(self, p: Point) -> None:
        """Adds a Point to the mid points."""
        return self._mid_points.append(p)

    def pop_mid_point(self) -> Point:
        """Returns the first element on the mid point route."""
        return self._mid_points.popleft()

    def switch_point_to_go(self) -> None:
        """Changes the point_to_go field with the enxt mid point."""
        try:
            self._point_to_go = self.pop_mid_point()
        except IndexError:
            self._point_to_go = self._destination
