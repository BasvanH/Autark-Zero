"""A testing suite for examining the effect of obstacles."""
import geopandas as gpd
import shapely.geometry as sp
from matplotlib import pyplot as plt
from path_finding import obstacle
from path_finding.path_finder import _generate_intersection_line
from path_finding.path_finder import _get_intersecting_boundary_line
from path_finding.path_finder import _get_intersection
from path_finding.path_finder import _get_waypoint
from path_finding.path_finder import checkCollision
from path_finding.path_finder import getPolygon
from path_finding.path_finder import intersection_water_boundary
from shapely.geometry import Point
from waterbodies import BoundingBox

# Define starting and ending points
location = Point(4.66502557, 52.40543554)
destination = Point(4.66664, 52.40847)

# Create waterbody outlines
border = getPolygon(location, 3)
boundary = gpd.GeoSeries(border.exterior if isinstance(border, sp.Polygon) else
                         [x.exterior for x in border.geoms])

boat = gpd.GeoSeries(location)
ax = boat.plot(color='blue', facecolor='none')

# Create bounds of plot
minx, miny, maxx, maxy = boundary.bounds.values[0]
bounding_box = sp.box(minx, miny, maxx, maxy)
bounding_box_series = gpd.GeoSeries(bounding_box.exterior)

# Create and draw obstacle
LAT_OFFSET = 0.0001
LONG_OFFSET = 0.0001
loc_dest_line = sp.LineString([location, destination])
obstacle_point = loc_dest_line.interpolate(0.65, normalized=True)
obstacle_box = BoundingBox(obstacle_point.y - LAT_OFFSET,
                           obstacle_point.x - LONG_OFFSET,
                           obstacle_point.y + LAT_OFFSET,
                           obstacle_point.x + LONG_OFFSET)
obstacle_thing = obstacle.Obstacle(obstacle_box, 0, 174)
obstacle_box_series = gpd.GeoSeries(
    sp.box(obstacle_box[1], obstacle_box[0], obstacle_box[3], obstacle_box[2]))

# Add obstacle to obstacle list and draw new path
obstacle_list = obstacle.ObstacleList()
obstacle_list.add_object(obstacle_thing)
new_angle = checkCollision(location, destination, 10)

# Simple line intersection
line = _generate_intersection_line(location, destination)
line_series = gpd.GeoSeries(line)
intersection = _get_intersection(location, destination, boundary)
intersection_series = gpd.GeoSeries(intersection)

extended_line_series = gpd.GeoSeries(
    _get_intersecting_boundary_line(location, new_angle, boundary))

intersection_angle = intersection_water_boundary(location, new_angle, boundary)
intersection_angle_series = gpd.GeoSeries(intersection_angle)

# Final route
final_route = _get_waypoint(location, destination)
final_route_series = gpd.GeoSeries(final_route)

ax = boundary.plot(color='red', ax=ax)
ax = bounding_box_series.plot(color='black', ax=ax)
ax = line_series.plot(color='green', ax=ax)
ax = extended_line_series.plot(color='purple', ax=ax)
ax = intersection_series.plot(color='yellow', ax=ax)
ax = intersection_angle_series.plot(color='blue', ax=ax)
ax = final_route_series.plot(color='orange', ax=ax)
ax = obstacle_box_series.plot(color='pink', ax=ax)
plt.show()
