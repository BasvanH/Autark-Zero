"""Basic map of the path finding algorithm."""
import geopandas as gpd
import shapely.geometry as sp
from matplotlib import pyplot as plt
from path_finding.path_finder import _generate_intersection_line
from path_finding.path_finder import _get_intersecting_boundary_line
from path_finding.path_finder import _get_intersection
from path_finding.path_finder import _get_waypoint
from path_finding.path_finder import getPolygon
from path_finding.path_finder import intersection_water_boundary
from shapely.geometry import Point

location = Point(5.691775981279707, 51.8951268856301)

# Change to 5.8... for a non-direct route
destination = Point(5.800248510652084, 51.89444326288273)
border = getPolygon(location, 3)
boundary = gpd.GeoSeries(border.exterior if isinstance(border, sp.Polygon) else
                         [x.exterior for x in border.geoms])

boat = gpd.GeoSeries(location)
ax = boat.plot(color='blue', facecolor='none')

minx, miny, maxx, maxy = boundary.bounds.values[0]
bounding_box = sp.box(minx, miny, maxx, maxy)
bounding_box_series = gpd.GeoSeries(bounding_box.exterior)

# Simple line intersection
line = _generate_intersection_line(location, destination)
line_series = gpd.GeoSeries(line)
intersection = _get_intersection(location, destination, boundary)
intersection_series = gpd.GeoSeries(intersection)

extended_line_series = gpd.GeoSeries(
    _get_intersecting_boundary_line(location, -45, boundary))

intersection_angle = intersection_water_boundary(location, 45, boundary)
intersection_angle_series = gpd.GeoSeries(intersection_angle)

# Final route
final_route = _get_waypoint(location, destination)
final_route_series = gpd.GeoSeries(final_route)

ax = boundary.plot(color="red", ax=ax)
ax = bounding_box_series.plot(color='black', ax=ax)
ax = line_series.plot(color='green', ax=ax)
ax = extended_line_series.plot(color='purple', ax=ax)
ax = intersection_series.plot(color='yellow', ax=ax)
ax = intersection_angle_series.plot(color='blue', ax=ax)
ax = final_route_series.plot(color='orange', ax=ax)
plt.show()
