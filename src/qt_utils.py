"""Defines methods for generating data to be used with Qt."""
import logging
from typing import List

from geofence import fetch_geofence
from geojson.geometry import Polygon
from PySide2.QtPositioning import QGeoCoordinate
from PySide2.QtPositioning import QGeoPolygon
from shared_data import OsmNodeData


def geojson2qt(pol: Polygon) -> QGeoPolygon:
    """Convert a GeoJSON polygon to a QT polygon.

    Args:
      pol: A GeoJSON polygon to convert.

    Returns:
      A polygon in QT format.
    """
    polygon = QGeoPolygon()

    for i in range(len(pol["coordinates"])):
        coordinates = pol["coordinates"][i]
        for j in range(len(coordinates)):
            base_coords = coordinates[j]
            try:
                # GeoJSOn polygons are in reverse order for some reason.
                coord = QGeoCoordinate(base_coords[1], base_coords[0])
                polygon.addCoordinate(coord)
            except TypeError:
                # Print it out if we don't support a shape so we can fix it.
                logging.getLogger("log.error").error(
                    f"GeoJSON could not be converted to QGeoPolygon {pol}")

    return polygon


def osmnodedata2qt(pol: List[OsmNodeData]) -> QGeoPolygon:
    """Convert a polygon from a list of OsmNodeData to a QGeoPolygon.

    Args:
        - pol: A list representing the points to convert
    """
    polygon = QGeoPolygon()
    for point in pol:
        coord = QGeoCoordinate(point.latitude, point.longitude)
        polygon.addCoordinate(coord)
    if pol:
        # Add first point again to close polygon
        first = QGeoCoordinate(pol[0].latitude, pol[0].longitude)
        polygon.addCoordinate(first)
    return polygon


def get_ardupilot_polygons() -> List[QGeoPolygon]:
    """Fetch polygons representing the current ArduPilot geofence."""
    import shared_data
    if shared_data.current_geofence is None:
        return []
    polygon = osmnodedata2qt(shared_data.current_geofence)
    return [polygon]


def get_debug_fence_polygons(latitude: float,
                             longitude: float) -> List[QGeoPolygon]:
    """
    Fetch polygons representing an ArduPilot geofence centered around a point.

    Args:
        - latitude: Latitude of the point to compute fence with respect to
        - longitude: Longitude of the point to compute fence with respect to
    """
    fence = fetch_geofence(latitude, longitude)
    polygon = osmnodedata2qt(fence)
    return [polygon]
