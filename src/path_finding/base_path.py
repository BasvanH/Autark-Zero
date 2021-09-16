"""In this find you can find the interface for path finding."""
import typing
from typing import List

from shapely.geometry import Point


class BasePath:
    """Contains the interface with basic methods and attributes."""
    def __init__(self, origin, destination) -> None:
        """Creates an instance of the BasePath."""
        self._origin = origin
        self._last_known_loc = origin
        self._destination = destination
        self._path = typing.Deque[Point]()
        self._previous_path = typing.Deque[Point]()

    def __iter__(self):
        """Returns itself as iterator."""
        return self

    def __next__(self):
        """Finds the next waypoint on the route."""
        if not self._path:
            raise StopIteration()

        next_ = self._path[0]
        self._last_known_loc = next_

        if self._last_known_loc == self._destination:
            raise StopIteration()

        return self._last_known_loc

    def _find_next_waypoint(self, last_known_loc: Point,
                            destination: Point) -> Point:
        """Find the route to the destination."""
        raise NotImplementedError()

    def get_origin(self) -> Point:
        """Gets the origin point."""
        return self._origin

    def get_destination(self) -> Point:
        """Gets the destination point."""
        return self._destination

    def get_path(self) -> typing.Deque[Point]:
        """Gets a copy of the path."""
        return self._path.copy()

    def get_previous_path(self) -> typing.Deque[Point]:
        """Gets a copy of the previous path."""
        return self._previous_path.copy()

    def extend(self, point) -> None:
        """Adds a Point to the path."""
        return self._path.append(point)

    def extend_previous(self, point) -> None:
        """Adds a Point to the previous path."""
        return self._previous_path.append(point)

    def pop(self) -> Point:
        """Returns the first element on the route."""
        return self._path.popleft()

    def add_to_front(self, point: Point) -> None:
        """Adds an intermediate waypoint to the front."""
        self._path.appendleft(point)

    def insert(self, i: int, x: Point) -> None:
        """Wrapper around the insert of the internal list."""
        self._path.insert(i, x)

    def get_route(self) -> List[Point]:
        """Forces the computation of the entire route."""
        return [x for x in self]
