"""Houses a classes representing navigational obstacles."""
from typing import List

from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
from singleton_metaclass import Singleton
from waterbodies import BoundingBox


class Obstacle:
    """Define a structure that stores data about an obstacle to be avoided."""
    def __init__(self, geometry: BoundingBox, speed: float,
                 angle: float) -> None:
        """
        Initialises an obstacle structure.

        This assumes a model where the obstacle is approximated by a circle
        with a given radius.

        Args:
            - geometry: Bounding box defining an area that the obstacle
            covers. Approximates location and size.
            - speed: Speed at which the object is travelling
            (in meters per second)
            - angle: Direction that the object is headed in
            (this value should be a bearing)
        """
        self.geometry = geometry
        self.speed = speed
        self.angle = angle

    def geometry_to_polygon(self) -> Polygon:
        """Convert the object's geometry to a shapely polygon."""
        polygon = Polygon([
            (self.geometry.west_longitude, self.geometry.south_latitude),
            (self.geometry.east_longitude, self.geometry.south_latitude),
            (self.geometry.west_longitude, self.geometry.north_latitude),
            (self.geometry.east_longitude, self.geometry.north_latitude)
        ])
        return polygon

    def origin_point(self) -> Point:
        """Compute a Shapely point representing the center of the obstacle."""
        mid_x = (self.geometry.west_longitude
                 + self.geometry.east_longitude) / 2
        mid_y = (self.geometry.north_latitude
                 + self.geometry.south_latitude) / 2
        return Point(mid_x, mid_y)


class ObstacleList(metaclass=Singleton):
    """Define a list of obstacles to be avoided."""
    def __init__(self) -> None:
        """Init function."""
        self._obstacle_list: List[Obstacle] = list()

    def __iter__(self):
        """Allows for iterating over list of obstacles."""
        for obstacle in self._obstacle_list:
            yield obstacle

    def add_object(self, obj: Obstacle) -> None:
        """Add object to list."""
        self._obstacle_list.append(obj)

    def delete_object(self, obj: Obstacle) -> None:
        """Delete object from list."""
        self._obstacle_list.remove(obj)
