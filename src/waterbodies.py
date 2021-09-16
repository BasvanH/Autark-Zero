"""Code to generate waterbody outlines.

This file makes use of the Overpass Query language to generate
polygons which can indicate whether the water is in a given region.

Args:
   author: Valentijn van de Beek (@valentijn)
"""
import logging
from collections import namedtuple
from typing import List
from typing import Tuple

import geopandas as gpd
import overpass
import shapely.geometry as sp
import shapely.ops as op
from geojson.base import GeoJSON
from geojson.geometry import Polygon

api = overpass.API()
BoundingBox = namedtuple(
    "BoundingBox",
    ["south_latitude", "west_longitude", "north_latitude", "east_longitude"])
seen_locations: List[Tuple[sp.box, List[Polygon]]] = []


def _fetch_location_data(loc: BoundingBox) -> GeoJSON:
    """Fetches all the location data in an area.

    Fetches all the elements in the given area that are related
    to water or water ways.

    Args:
       - loc: A bounding box defining the area to fetch data in
    """
    query_string = f'''
    relation["natural"="water"]
    (
        {loc.south_latitude},
        {loc.west_longitude},
        {loc.north_latitude},
        {loc.east_longitude}
    );
    '''
    res = api.get(query_string, verbosity="qt body geom skel")

    if not res:
        return _fetch_location_coast(loc)
    return res


def _fetch_location_coast(loc: BoundingBox) -> GeoJSON:
    """Fetches information data specifically pertaining to ways.

    Fetches ways defining coastlines.

    Args:
        - loc: A bounding box defining the area to fetch data in
    """
    query_string = f'''
    way["natural"="coastline"]
    (
        {loc.south_latitude},
        {loc.west_longitude},
        {loc.north_latitude},
        {loc.east_longitude}
    );
    '''
    return api.get(query_string, verbosity="qt body geom skel")


def _fetch_polygons(loc: BoundingBox) -> List[Polygon]:
    """Locates the polygons in an area.

    Parses the Overpass data into the polygons that can be used for
    either QT map or ArduPilot.

    Args:
        - loc: A bounding box defining the area to fetch data in
    """
    data = _fetch_location_data(loc)
    return [feature["geometry"] for feature in data["features"]]


def get_waterbodies(loc: BoundingBox) -> List[Polygon]:
    """Finds the outlines of all bodies of water in area.

    A simple wrapper around the OSM tools which caches the request
    before sending it.

    The assumption here is that there has not been
    an earthquake which drastically changed the geography since first
    launching the program.

    Args:
        - loc: A bounding box defining the area to fetch data in
    """
    # Create a box around the used location and see if there already
    # is a shape which encompasses it entirely
    box = sp.box(loc[1], loc[0], loc[3], loc[2])
    for (location, cached) in seen_locations:
        if box.within(location):
            return cached

    # Create an encompassing box
    res = []
    try:
        res = _fetch_polygons(loc)
    except Exception as e:
        logging.getLogger("log.error").error(e)
        return []

    border = op.unary_union([sp.shape(pol) for pol in res])

    if isinstance(border, sp.Polygon):
        boundary = gpd.GeoSeries(border.exterior)
    elif isinstance(border, sp.MultiPolygon):
        boundary = gpd.GeoSeries([pol.exterior for pol in border.geoms])
    elif isinstance(border, sp.MultiLineString):
        boundary = gpd.GeoSeries(border.convex_hull.exterior)
    else:
        # Some debug information to see why it crashes
        logging.getLogger("log.error").error(
            "Fetching body water outlined failed")
        logging.getLogger("log.error").error(border)
        logging.getLogger("log.error").error(type(border))
        return []

    minx, miny, maxx, maxy = boundary.bounds.values[0]
    new_box = sp.box(minx, miny, maxx, maxy)
    seen_locations.append((new_box, res))

    return res


if __name__ == "__main__":
    """Debug main to visualise retrieved data."""
    from matplotlib import pyplot as plt
    from shapely.geometry import shape
    from shapely.ops import cascaded_union

    pol = get_waterbodies(BoundingBox(52.399583, 4.654362, 52.412963,
                                      4.684574))
    border = cascaded_union([shape(x) for x in pol])
    boundary = gpd.GeoSeries(border)
    boundary.plot(color="red")
    plt.show()
