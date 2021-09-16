"""Defines the functions to find the geofence according to MAVLink limits."""
from time import sleep
from typing import List
from typing import Tuple

import config
from geo_utils import haversine_dist
from geo_utils import LATITUDE_DIST
from mavlink_client import MavlinkClient
from shapely.geometry import Point
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shared_data import OsmNodeData
from waterbodies import BoundingBox
from waterbodies import get_waterbodies

config_parser = config.ConfigFile()
current_location = None


def get_lat_delta() -> float:
    """Fetching the latitude delta for creating the bounding box.

    Latitude delta for creating bounding box given a GPS point.
    """
    return config_parser.general_getter("GEOFENCE", "LATITUDE_DELTA",
                                        config.DataType.FLOAT)


def get_long_delta() -> float:
    """Fetching the longitude delta for creating the bounding box.

    Longitude delta for creating bounding box given a GPS point.
    """
    return config_parser.general_getter("GEOFENCE", "LONGITUDE_DELTA",
                                        config.DataType.FLOAT)


def get_tol_dist() -> int:
    """Fetches the tolerance distance.

    Distance (in metres) for polygon simplification tolerance
    Set to zero for no simplification
    """
    return config_parser.general_getter("GEOFENCE",
                                        "SIMPLIFICATION_TOLERANCE_DISTANCE",
                                        config.DataType.INT)


def get_refresh_delay() -> int:
    """Fetches the refresh delay.

    Time (in seconds) between each iteration of geofence generation
    based on GPS data received from MQTT.
    """
    return config_parser.general_getter("GEOFENCE", "REFRESH_DELAY",
                                        config.DataType.INT)


def get_min_refresh_dist() -> int:
    """Fetches the minimum refresh distance.

    Distance (in meters) representing the minimum required distance between
    the old location and the current location in order to trigger a geofence
    refresh.
    """
    return config_parser.general_getter("GEOFENCE", "MINIMUM_REFRESH_DISTANCE",
                                        config.DataType.INT)


# TODO:
# - Migrate to NumPy arrays because speed
# - Split for loops to separate threads


def _fetch_single_geometry(latitude: float, longitude: float) -> BaseGeometry:
    """Fetches water boundaries as a single geometry.

    All points lying in a bounding box of area (2*lat_delta *
    2*long_delta), centered around the given coordinates
    are retrieved and combined into a single polygon.

    Args:
        - latitude: The latitude of the given coordinate
        - longitude: The longitude of the given coordinate

    """
    bounding_box = BoundingBox(latitude - get_lat_delta(),
                               longitude - get_long_delta(),
                               latitude + get_lat_delta(),
                               longitude + get_long_delta())
    relation_polygon_list = get_waterbodies(bounding_box)
    return unary_union([shape(relation) for relation in relation_polygon_list])


def _preprocess_geometry(geom: BaseGeometry, latitude: float,
                         longitude: float) -> List[Tuple[float, float]]:
    """
    Processes the given geometry into a list of points.

    This attempts to convert the given geometry into a semi-representative
    list of points (as latitude longitude pairs). It first (optionally)
    simplifies then constructs a list of the resultant points.

    Args:
        - geom: An object representing a geometry to process
        - latitude: The latitude of the given coordinate
        - longitude: The longitude of the given coordinate
    """
    # Simplify if option is enabled
    if get_tol_dist() != 0:
        tol = get_tol_dist() / LATITUDE_DIST
        geom = geom.simplify(tol, True)

    # Construct point list defining polygon exterior
    # [:-1] indexing is to skip repeating the first point
    polygon_points = []
    if geom.geom_type == "MultiPolygon":
        for polygon in geom:
            curr_loc = Point(longitude, latitude)
            if curr_loc.within(polygon):
                polygon_points += polygon.exterior.coords[:-1]
    elif geom.geom_type == "Polygon":
        polygon_points = geom.exterior.coords[:-1]

    return polygon_points


def fetch_geofence(latitude: float,
                   longitude: float,
                   num_points: int = 70) -> List[OsmNodeData]:
    """Fetch a geofence centered around the given point.

    The returned order of points is suitable for drawing the geofence polygon.

    See the _fetch_nearest_points documentation for additional details.

    Args:
        - latitude: The latitude of the given coordinate
        - longitude: The longitude of the given coordinate
        - num_points: The number of points to return
    """
    water_geometry = _fetch_single_geometry(latitude, longitude)
    polygon_points = _preprocess_geometry(water_geometry, latitude, longitude)

    # Return directly if points are fewer than limit
    # Shapely shapes store long-lat instead of lat-long
    # so points need to be flipped
    if len(polygon_points) <= num_points:
        return list(
            map(lambda pt: OsmNodeData(pt[1], pt[0], 0, 0), polygon_points))

    # Filter down to limit based on nearest points
    # Shapely shapes store long-lat instead of lat-long
    # so points need to be flipped here too
    nearest_points = []
    for idx, coordinate in enumerate(polygon_points):
        poly_long, poly_lat = coordinate
        nearest_points.append(
            OsmNodeData(
                poly_lat, poly_long, idx,
                haversine_dist(Point(poly_long, poly_lat),
                               Point(longitude, latitude))))
    nearest_points = sorted(nearest_points,
                            key=lambda data: data.origin_dist)[0:num_points]
    nearest_points.sort(key=lambda data: data.order)
    return nearest_points


def generate_fence_from_mqtt() -> None:
    """Generate and upload a geofence based on received GPS data from MQTT.

    This runs an infinite loop that generates and attempts to upload a
    geofence periodically based on data received from MQTT.
    It is meant to run in a separate thread.
    """
    previous_location = None
    while True:
        sleep(get_refresh_delay())

        # Skip iteration if no data or changed distance is small
        if current_location is None:
            continue
        if previous_location is not None:
            travelled_dist = haversine_dist(previous_location,
                                            current_location)
            if travelled_dist < get_min_refresh_dist():
                continue

        # Update previous location and generate+transmit fence
        import shared_data
        previous_location = current_location
        shared_data.current_geofence = fetch_geofence(current_location.y,
                                                      current_location.x)
        mavlink_con = MavlinkClient()
        mavlink_con.transmit_geofence(shared_data.current_geofence,
                                      current_location.y, current_location.x)
