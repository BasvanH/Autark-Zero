"""This file contains utilities for manipulating GPS coordinates.

Methods are partly or wholly based on this lovely website
https://www.movable-type.co.uk/scripts/latlong.html

All measurements are as follows unless otherwise specified:

- Distances are in metres
- Latitude is in decimal degree format and ranges from
-90 to 90 (South to North)
- Longitude is in decimal degree format and ranges from
-180 to 180 (West to East)

"""
from math import asin
from math import atan2
from math import cos
from math import pi
from math import radians
from math import sin
from math import sqrt

from shapely.geometry import Point

# Distance represented by one latitude degree
LATITUDE_DIST = 111000

# Distance represented by one longitude degree at the equator
EQUATOR_LONGITUDE_DIST = 111321

# Mean radius of the Earth
EARTH_RADIUS = 6371000


def haversine_dist(p1: Point, p2: Point) -> float:
    """Calculate the Haversine distance between two points.

    Compute the distance between two points using the Haversine formula

    Args:
        - p1: First point
        - p2: Second point
    """
    a = (sin(radians(p1.y - p2.y) / 2) **
         2) + (cos(radians(p1.y)) * cos(radians(p2.y)) *
               (sin(radians(p1.x - p2.x) / 2) ** 2))
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS * c


def bearing(p1: Point, p2: Point) -> float:
    """Calculate the bearing to get from p1 to p2 (initial bearing).

    Args:
        - p1: Point to start from
        - p2: Point to end at
    """
    y = sin(radians(p2.x - p1.x)) * cos(radians(p2.y))
    x = cos(radians(p1.y)) * sin(radians(p2.y)) - sin(radians(p1.y)) * cos(
        radians(p2.y)) * cos(radians(p2.x - p1.x))
    theta = atan2(y, x)
    return ((theta * 180 / pi + 360) % 360)


def distance_points(p1: Point, p2: Point) -> float:
    """Calculate the classic distance between 2 points.

    Assumes a flat plane and uses the Pythagorean theorem.

    Args:
        - p1: First point
        - p2: Second point
    """
    res = sqrt((p2.y - p1.y) ** 2 + (p2.x - p1.x) ** 2)
    return res


def distance_points2(p1: Point, bearing: float, distance: float) -> Point:
    """Returns a point interpolated using the given data.

    More accurately, it returns where one would arrive if they were to travel
    the given distance from the given point at the given initial bearing.

    Args:
        - p1: Point to start at
        - bearing: Initial bearing to travel along
        - distance: Distance to travel
    """
    angular = distance / EARTH_RADIUS
    lhsd = sin(radians(p1.y)) * cos(angular)
    rhsd = cos(radians(p1.y)) * sin(angular) * cos(radians(bearing))
    omega = asin(lhsd + rhsd)

    alpha = radians(p1.x) + atan2(
        sin(radians(bearing)) * sin(angular) * cos(radians(p1.y)),
        cos(angular) - sin(radians(p1.y)) * sin(omega))

    return Point(((alpha * 180 / pi + 360) % 360),
                 ((omega * 180 / pi + 360) % 360))
