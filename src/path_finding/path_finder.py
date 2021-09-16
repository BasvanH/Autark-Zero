"""Sailing logic class."""
import logging
from math import atan2
from math import cos
from math import isclose
from math import pi
from math import radians
from math import sin
from typing import Any
from typing import Dict
from typing import Tuple

import geopandas as gpd
import numpy as np
import shapely.geometry as sp
from config import ConfigFile
from config import DataType
from geo_utils import bearing
from geo_utils import distance_points2
from geo_utils import haversine_dist
from geojson.geometry import Polygon
from path_finding.obstacle import Obstacle
from path_finding.obstacle import ObstacleList
from shapely.affinity import rotate
from shapely.affinity import translate
from shapely.geometry import box
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import shape
from shapely.ops import split
from shapely.ops import unary_union
from waterbodies import BoundingBox
from waterbodies import get_waterbodies

from .boat import Boat

# Put into a class? Now it is stuck to just one mission
CURRENT_ANGLE = 45
LAST_POINT = Point(0, 0)

config_parser = ConfigFile()


def _get_collision_distance_threshold() -> int:
    """Get the collision threshold.

    If a collision is to occur, it will be considered if the distance
    between the obstacle and the boat, once the obstacle arrives at
    the collision point, is lower than this (this value is in meters)
    """
    return config_parser.general_getter("PATH_FINDER",
                                        "COLLISION_DISTANCE_THRESHOLD",
                                        DataType.INT)


def _get_direction_change_angle() -> int:
    """Get degrees by which the angle is changed."""
    return config_parser.general_getter("PATH_FINDER",
                                        "DIRECTION_CHANGE_ANGLE", DataType.INT)


def _get_obstacle_line_project_dist() -> int:
    """Get the length of the project line for an object's path."""
    return config_parser.general_getter("PATH_FINDER",
                                        "OBSTACLE_LINE_PROJECTION_DISTANCE",
                                        DataType.INT)


def _get_obstacle_origin_reverse_epsilon() -> int:
    """Get the obstacle's reverse epsilon.

    Length of backwards projected line for an object's path.
    This prevents issues with floating point precision with intersections.
    (this value is in meters)
    """
    return config_parser.general_getter("PATH_FINDER",
                                        "OBSTACLE_ORIGIN_REVERSE_EPSILON",
                                        DataType.INT)


logger = logging.getLogger("log.path_finder")


def get_angle() -> float:
    """Get the current angle, should be fixed as it is pretty broken."""
    global CURRENT_ANGLE
    CURRENT_ANGLE = -CURRENT_ANGLE
    return CURRENT_ANGLE


def computeDirection(bearing_angle: float, wind_dir: float, wind_speed: float,
                     boat_speed: float):
    """Calculate the angle between the desired direction and the wind.

        Sorry for the dumb work arounds done.
    Args:
        - bearing_angle: return of the bearing func
         (between current location and final destination)
        - wind_dir: Wind direction according to the local sensor
        - wind_speed: Wind speed according to the local sensor
        - boat_speed: Speed of the boat

    Returns:
        1. upwind sailing, so it returns a tuple with the 2 possiblities it can
           take.
        2. no upwind sailing, go straight and adapt sail to catch more
           wind.
        In this case the 2 values are equal and represent the true wind
        direction so the sail can adapt the angle.
    """
    x_wind = wind_speed * cos(radians(wind_dir))
    y_wind = wind_speed * sin(radians(wind_dir))
    wind_vector = np.array([x_wind, y_wind])

    x_boat = boat_speed * cos(radians(bearing_angle))
    y_boat = boat_speed * sin(radians(bearing_angle))
    bearing_vector = np.array([x_boat, y_boat])

    wind_vector -= bearing_vector
    true_dir = ((atan2(wind_vector[1], wind_vector[0]) * 180 / pi + 360) % 360)
    # actual value of the wind, might be useless
    if abs(bearing_angle - true_dir) < 90 or abs(bearing_angle
                                                 - true_dir) > 270:
        return ((true_dir - 35) % 360, (true_dir + 35) % 360)
    else:
        return (bearing_angle, bearing_angle)


def _compute_single_collision(current_location: Point, destination: Point,
                              speed: float,
                              obstacle: Obstacle) -> Tuple[bool, float]:
    """
    Compute if and where a collision will occur.

    Returns a tuple indicating if a collision will occur and
    (if applicable) the distance difference between the obstacle
    and the boat when the boat arrives at the intersection point.

    Args:
        - current_location: Current location of the boat being guided
        - destination: The immediate location which we want to arrive at
        - speed: The speed with which we are travelling
        - obstacle: The obstacle with which a potential collision should
        be computed
    """
    # No movement quick computation
    if isclose(obstacle.speed, 0, abs_tol=0.0001):
        obstacle_polygon = obstacle.geometry_to_polygon()
        path_line = LineString([current_location, destination])

        if path_line.intersects(obstacle_polygon):
            return (True, 0)
        return (False, 0)

    # Construct requisite points and path lines
    obstacle_origin = distance_points2(obstacle.origin_point(), obstacle.angle,
                                       -_get_obstacle_origin_reverse_epsilon())
    obstacle_projected_destination = \
        distance_points2(obstacle_origin, obstacle.angle,
                         _get_obstacle_line_project_dist())
    boat_path = LineString([current_location, destination])
    obstacle_path = LineString(
        [obstacle_origin, obstacle_projected_destination])

    if boat_path.intersects(obstacle_path):
        # Compute time until boat's arrival to destination
        intersection_point = boat_path.intersection(obstacle_path)
        boat_intersection_dist = haversine_dist(current_location,
                                                intersection_point)
        boat_arrival_time = boat_intersection_dist / speed
        logger.info(f"INTERSECTION DETECTED WITH {intersection_point}")

        # Translate obstacle to its position on boat's arrival
        obstacle_new_position = distance_points2(
            obstacle_origin, obstacle.angle,
            obstacle.speed * boat_arrival_time)
        shift_x = obstacle_new_position.x - obstacle_origin.x
        shift_y = obstacle_new_position.y - obstacle_origin.y

        shifted_obstacle = translate(obstacle.geometry_to_polygon(), shift_x,
                                     shift_y)

        # Evaluate distance on boat arrival at intersection point
        if shifted_obstacle.contains(obstacle_new_position):
            return (True, 0)
        else:
            dist = shifted_obstacle.distance(obstacle_new_position)
            return (True, dist)

    return (False, 0)


def checkCollision(current_location: Point, destination: Point, speed: float):
    """
    Check for collision with known obstacles and suggest new direction.

    This computes a new angle (returned as a float representing a bearing)
    in which to sail in so that all known obstacles are avoided.

    Args:
        - current_location: Current location of the boat being guided
        - destination: The immediate location which we want to arrive at
        - speed: The speed with which we are travelling (in meters per second)
    """
    obstacle_list = ObstacleList()
    distance = 0.
    collision_detected = False
    for obstacle in obstacle_list:
        will_collide, dist_difference = \
            _compute_single_collision(current_location, destination,
                                      speed, obstacle)
        if will_collide and \
           (dist_difference < _get_collision_distance_threshold()):
            collision_detected = True
            distance = dist_difference
            t = obstacle
            break
    d: Dict[(str, Any)] = dict()
    bearing_angle = bearing(current_location, destination)

    # TODO: Rewrite to be recursive and check validity of new angle
    if collision_detected:
        d["collision"] = True
        d["collision_coords"] = distance_points2(current_location,
                                                 bearing_angle, distance)
        d["obstacle"] = t
        d["new_angle"] = bearing_angle + _get_direction_change_angle()
        return d

    d["collision"] = False
    d["new_angle"] = bearing_angle
    return d


def checkTime(p1: Point, p2: Point, obstacle: Obstacle, s1: float) -> float:
    """Time difference bewtween time needed for each of the 2 boats.

    to reach the collision point.

        For now this function is quite trivial, tuning should be considered
        later.
        First optimization is to add an offset proportionally direct with
        the distance, as speed might change significantly over time.
    Args:
        - p1: position of first boat
        - p2: collision point
        - p3: position of second boat
    Return float type, can be negative (first boat gets there faster then
    the second).
    """
    dx1 = haversine_dist(p1, p2)
    dx2 = haversine_dist(obstacle.origin_point(), p2)
    s2 = obstacle.speed

    t1 = dx1 / s1
    t2 = dx2 / s2
    return abs(t1 - t2)


def getBoundingBox(curr_location: Point, offset) -> BoundingBox:
    """Get best BoundingBox for current location.

    Args:
        - curr_location: current location
        - offset: int value
    """
    long_delta = 10 ** -offset
    lat_delta = 10 ** -offset
    loc = BoundingBox(curr_location.y - lat_delta,
                      curr_location.x - long_delta,
                      curr_location.y + lat_delta,
                      curr_location.x + long_delta)
    return loc


def getPolygon(curr_location: Point, offset) -> Polygon:
    """Returns best Polygon given a location.

    Args:
        - curr_location: current location
        - offset: int value
    """
    loc = getBoundingBox(curr_location, offset)
    polygons = get_waterbodies(loc)
    return unary_union([shape(x) for x in polygons])


def _get_intersecting_boundary_line(curr_location: Point, angle: float,
                                    boundary) -> LineString:
    minx, miny, maxx, maxy = boundary.bounds.values[0]
    bounding_box = box(minx, miny, maxx, maxy)

    k = np.tan(np.radians(angle))
    m = curr_location.y - k * curr_location.x
    y0 = k * minx + m
    y1 = k * maxx + m
    x0 = (miny - m) / k
    x1 = (maxy - m) / k

    points = [
        sp.Point(minx, y0),
        sp.Point(maxx, y1),
        sp.Point(x0, miny),
        sp.Point(x1, maxy)
    ]

    points_sorted_by_distance = sorted(points, key=bounding_box.distance)
    return LineString(points_sorted_by_distance[:2])


def intersection_water_boundary(curr_location: Point, angle: float, boundary):
    """Calculates the intersection with the boundary of the water."""
    line = _get_intersecting_boundary_line(curr_location, angle, boundary)
    intersections = boundary.intersection(line)
    before, _, after = split(line, curr_location.buffer(0.000001))

    # Find the last intersection before we reach the origin
    first_intersection = [
        point for point in intersections[0]
        if before.distance(point) < 0.000001
    ]

    # The first intersection after passing it
    second_intersection = [
        point for point in intersections[0] if after.distance(point) < 0.000001
    ]

    if len(first_intersection) == 0:
        return [second_intersection[0], second_intersection[0]]
    if len(second_intersection) == 0:
        return [first_intersection[-1], first_intersection[-1]]

    return [first_intersection[-1], second_intersection[0]]


def _generate_intersection_line(curr_location: Point, destination: Point):
    """Generate the line directly towards the location."""
    return LineString([curr_location, destination])


def _get_intersection(curr_location: Point, destination: Point, boundary):
    """Generate the intersection to the destination and the boundary."""
    line = _generate_intersection_line(curr_location, destination)
    return boundary.intersection(line)


def _generate_waypoint_choices(origin: Point, intersection: Point):
    line = sp.LineString([origin, intersection])
    return [line.interpolate(i, True) for i in [0.5, 0.6, 0.7, 0.8, 0.9]]


def _get_best_next_waypoint(location: Point, destination: Point):
    intersection = _get_waypoint(location, destination)
    choices = _generate_waypoint_choices(location, intersection)

    intersections = [
        _find_intersection_to_destination(p, destination) for p in choices
    ]
    p = sorted(intersections, key=destination.distance)[0]

    line = sp.LineString([location, p])
    return line.interpolate(0.95, True)


def _find_intersection_to_destination(location: Point,
                                      destination: Point) -> sp.Point:
    global LAST_POINT
    border = getPolygon(location, 3)

    if isinstance(border, sp.Polygon):
        boundary = gpd.GeoSeries(border.exterior)
    elif isinstance(border, sp.MultiPolygon):
        boundary = gpd.GeoSeries([pol.exterior for pol in border.geoms])
    else:
        # Some debug information to see why it crashes
        return location

    # First try if we can get a direct route
    direct = _get_intersection(location, destination, boundary)

    if direct.is_empty.values[0]:
        logger.info(f"direct route {destination.y} {destination.x}")
        return destination

    # Find all the intersections
    points = intersection_water_boundary(location, get_angle(), boundary)
    destination_distance = destination.distance
    p = None

    if destination_distance(points[0]) < destination_distance(points[1]):
        p = points[0]
        q = points[1]
    else:
        p = points[1]
        q = points[0]

    total = LAST_POINT.distance(p) + LAST_POINT.distance(q)
    if (LAST_POINT.distance(p) / total) < 0.001:
        p = q
    LAST_POINT = p
    return p


def _get_waypoint(location: Point, destination: Point):
    point = _find_intersection_to_destination(location, destination)
    line = sp.LineString([location, point])
    bearing_angle = bearing(location, destination)
    boat = Boat()
    # print("STRATEGY", strategy.NO_TACKING, strategy.TACKING)
    if boat._tacking is True:
        new_angle = _modify_angle(boat, bearing_angle)
        line = rotate(line, new_angle, location)
    return line.interpolate(0.95, True)


def _modify_angle(boat: Boat, bearing: float):
    upper_limit = boat._tacking_upper_limit
    downside_limit = boat._tacking_down_limit
    if abs(bearing - upper_limit) > abs(bearing - downside_limit):
        return downside_limit
    else:
        return upper_limit


def find_path_to_destination(location: Point, destination: Point) -> Point:
    """Computes path to destionation from current location."""
    point = _get_best_next_waypoint(location, destination)
    return point


def line_point_intersection(location: Point, destination: Point,
                            p1: Point) -> Point:
    """Computes intersection coords of a point with a line."""
    line = LineString([location, destination])
    projection = line.project(p1)
    return line.interpolate(projection)
