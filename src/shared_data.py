"""Houses definitions and data shared across various program components.

Used to prevent circular imports.
"""
from collections import namedtuple

current_geofence = None

OsmNodeData = namedtuple(
    "OsmNodeData",
    ["latitude", "longitude", "order", "origin_dist"],
)
