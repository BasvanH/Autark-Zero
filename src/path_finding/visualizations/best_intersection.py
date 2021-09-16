"""Finds the best option for the next waypoint."""
import geopandas as gpd
import shapely.geometry as sp
from matplotlib import pyplot as plt
from path_finding.path_finder import _find_intersection_to_destination
from path_finding.path_finder import _generate_waypoint_choices
from path_finding.path_finder import _get_best_next_waypoint
from path_finding.path_finder import _get_waypoint
from path_finding.path_finder import getPolygon
from shapely.geometry import Point

origin = Point(4.661788405110263, 52.404488319225315)
destination = Point(4.679982508895097, 52.412416699424895)

border = getPolygon(origin, 3)
boundary = gpd.GeoSeries(border.exterior if isinstance(border, sp.Polygon) else
                         [x.exterior for x in border.geoms])
ax = boundary.plot(color='red')

opoint = gpd.GeoSeries(origin)
dpoint = gpd.GeoSeries(destination)
ax = dpoint.plot(color='blue', facecolor='none', ax=ax)
ax = opoint.plot(color='green', facecolor='none', ax=ax)

extra_box = sp.box(4.668466196669055, 52.407664958949056, 4.6704661966690555,
                   52.40966495894905)

ax = gpd.GeoSeries(extra_box.exterior).plot(color='green', ax=ax)

intersection = _get_waypoint(origin, destination)

for point in _generate_waypoint_choices(origin, intersection):
    ax = gpd.GeoSeries(point).plot(color='green', ax=ax)
    path = _find_intersection_to_destination(point, destination)

    ax = gpd.GeoSeries(sp.LineString([point, path])).plot(color='purple',
                                                          ax=ax)

next_ = _get_best_next_waypoint(origin, destination)
ax = gpd.GeoSeries(next_).plot(color='purple', ax=ax)
ax = gpd.GeoSeries(sp.LineString([intersection, next_]))\
        .plot(color='yellow', ax=ax)

next_two = _get_best_next_waypoint(next_, destination)

ax = gpd.GeoSeries(next_two).plot(color='purple', ax=ax)
ax = gpd.GeoSeries(sp.LineString([next_, next_two]))\
        .plot(color='yellow', ax=ax)

intersection_line = sp.LineString([origin, intersection])
intersection_line_series = gpd.GeoSeries(intersection_line)

ax = intersection_line_series.plot(color='yellow', ax=ax)
plt.show()
