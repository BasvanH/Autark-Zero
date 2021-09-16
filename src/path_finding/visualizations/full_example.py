"""Module for visual debug."""
import geopandas as gpd
import shapely.geometry as sp
from matplotlib import pyplot as plt
from path_finding.path_finder import find_path_to_destination
from path_finding.path_finder import getPolygon
from shapely.geometry import Point

origin = Point(4.661788405110263, 52.404488319225315)
destination = Point(4.672336340873712, 52.40536286709633)

border = getPolygon(origin, 3)
boundary = gpd.GeoSeries(border.exterior if isinstance(border, sp.Polygon) else
                         [x.exterior for x in border.geoms])
ax = boundary.plot(color='red')

opoint = gpd.GeoSeries(origin)
dpoint = gpd.GeoSeries(destination)
ax = dpoint.plot(color='blue', facecolor='none', ax=ax)
ax = opoint.plot(color='green', facecolor='none', ax=ax)

current = origin
i = 0
while current.distance(destination) > 0.0000001:
    if i == 20:
        break
    i += 1
    p = find_path_to_destination(current, destination)
    line = sp.LineString([current, p])
    ax = gpd.GeoSeries(line).plot(color='blue', ax=ax)
    current = p

plt.show()
