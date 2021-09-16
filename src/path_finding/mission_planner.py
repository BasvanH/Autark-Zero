"""Class used for controlling the boat."""
import json
import logging
import os
import subprocess
import typing
from time import sleep

from config import ConfigFile
from config import DataType
from geo_utils import bearing
from geo_utils import haversine_dist
from shapely.geometry import Point

from .boat import Boat
from .path_finder import checkCollision
from .path_finder import checkTime
from .path_finder import computeDirection
from .path_finder import find_path_to_destination
from .path_finder import line_point_intersection
from .strategy import Strategy

config_parser = ConfigFile()


def _get_distance_till_heading_straight() -> int:
    return config_parser.general_getter("MISSION_PLANNER",
                                        "DISTANCE_UNTIL_HEADING_STRAIGHT",
                                        DataType.INT)


def _get_limit_ardu_waypoints() -> int:
    return config_parser.general_getter("MISSION_PLANNER",
                                        "LIMIT_ARDUPILOT_WAYPOINTS",
                                        DataType.INT)


def _get_min_distance_waypoint() -> int:
    return config_parser.general_getter("MISSION_PLANNER",
                                        "MINIMUM_DISTANCE_WAYPOINT",
                                        DataType.INT)


def _get_resolution_ocean_trip() -> int:
    return config_parser.general_getter("MISSION_PLANNER",
                                        "RESOLUTION_OCEAN_TRIP", DataType.INT)


def _get_time_offset_collision() -> int:
    return config_parser.general_getter("MISSION_PLANNER",
                                        "TIME_OFFSET_COLLISION", DataType.INT)


logger = logging.getLogger("log.mission_planner")


class MissionPlanner:
    """Class used for controlling the boat."""
    def add_new_mission(self, boat_id: int, p1: Point, p2: Point):
        """It creates a new boat instance.

        Args:
            - boat_id: Id of the new boat
            - p1: Origin coords of the boat
            - p2: Coords of the FINAL destination
            - boats: Array of boats
        """
        boat_curr = Boat(boat_id, p1, p2)
        boat_curr._destination = p2
        boat_curr._final_destination = p2
        boat_curr._origin = p1
        boat_curr._last_known_loc = p1
        boat_curr._bearing = bearing(p1, p2)
        boat_curr._point_to_go = p2
        boat_curr = self.plan_trip(p1, p2, boat_curr)
        if len(boat_curr._mid_points) > 1:
            boat_curr._sea = True
        return boat_curr

    def _update_mission(self, index: int, wind_dir: float, wind_speed: float,
                        boat_speed: float) -> None:
        """Update mission, pop waypoint(s), add more if necessary.

        Args:
            - index: Waypoint index received from ArduPilot.
            - wind_dir: Direction of wind.
            - wind_speed: Speed of wind.
            - boat_speed: Speed of boat.
        """
        boat = Boat()
        while boat._wp_index < index and len(boat._path) > 0:
            boat._wp_index += 1
            boat._point_to_go = boat._path.popleft()
            boat._past_wp.append(boat._point_to_go)

        if boat._wp_index != index and len(boat._path) == 0:
            logger.error("Somehow ArduPilot has EXTRA waypoints.")

        if len(boat._path) < 3 and boat._path[len(boat._path)
                                              - 1] != boat._final_destination:
            self.generate_waypoints(boat, wind_dir, wind_speed, boat_speed)

    def _create_next_waypoint(self, boat: Boat, wind_dir: float,
                              wind_speed: float, boat_speed: float):
        """Internal function which is not supposed to be called, it creates new wp.

        It implements the logic for creating the next waypoint.
        Args:
            - boat: Current boat
            - wind_dir: Direction of the wind between 0 and 360
            - wind_speed: Speed of the wind in knots
            - boats: Array of boats
            - telemetry: singleton instace for retrieving data like boat speed

        Return is : - (bool, waypoint) type: true if it can add a new
        waypoints, false otherwise.
                    - (bool, Boat) type: if the boat has to waits, the instance
                    is returned with the wait_time field set and without a new
                    waypoint.
        """
        bearing_angle = bearing(boat._last_known_loc, boat._destination)
        possible_angles = computeDirection(bearing_angle, wind_dir, wind_speed,
                                           boat_speed)
        if possible_angles[0] == possible_angles[1]:
            strategy = Strategy.NO_TACKING
            boat._tacking = False
            boat._bearing = possible_angles[0]
        else:
            boat._tacking = True
            boat._bearing = possible_angles[0] + 35
            boat._tacking_down_limit = possible_angles[0]
            boat._tacking_upper_limit = possible_angles[1]
            strategy = Strategy.TACKING

        if strategy == Strategy.TACKING:
            maximal_dist = find_path_to_destination(boat._last_known_loc,
                                                    boat._destination)
        else:
            maximal_dist = find_path_to_destination(boat._last_known_loc,
                                                    boat._destination)

        if haversine_dist(boat._last_known_loc,
                          maximal_dist) < _get_min_distance_waypoint():
            logger.warn("maximal dist too short")
            return (True, boat)

        # TODO: activate engine, put sail parallel to the wind dir?
        # 2 options: either it's a channel and we should really turn on
        #  the engine or it's a bigass obstacle and we need to go around it
        final_waypoint = maximal_dist

        dict = checkCollision(boat._last_known_loc, final_waypoint, boat_speed)

        if dict["collision"] is False:
            return (False, maximal_dist)
        else:
            if dict["obstacle"]._speed == 0:
                boat._bearing = dict["new_angle"]
                return self._create_next_waypoint(boat, wind_dir, wind_speed,
                                                  boat_speed)
            else:
                time = checkTime(boat._last_known_loc,
                                 dict["collision_coords"], dict['obstacle'],
                                 boat_speed)
                if time < _get_time_offset_collision():
                    boat._wait_time = time
                    return (True, boat)
                else:
                    boat._bearing = dict["new_angle"]
                    return self._create_next_waypoint(boat, wind_dir,
                                                      wind_speed, boat_speed)

    def generate_waypoints(self, boat: Boat, wind_dir: float,
                           wind_speed: float, boat_speed: float) -> Boat:
        """Function for controlling the create_next_waypoint function.

        Args:
            - boat: Boat instace.
            - wind_dir: Direction of the wind between 0 and 360 degrees.
            - wind_speed: Speed of the wind in knots.
            - boat_speed: Speed of the boat
        Returns the updated boat instance.
        """
        flag = False
        paths = typing.Deque[Point]()
        init_loc = boat._last_known_loc
        if len(boat._mid_points) == 0:
            logger.info("FINAL DESTINATION REACHED")
            return boat
        ct = 0
        boat._destination = boat._mid_points.popleft()
        if len(boat._path) == 0:
            ct += 1
            logger.info(f"########## RUN NUMBER {ct} ##########")
            (flag, wp) = self._create_next_waypoint(boat, wind_dir, wind_speed,
                                                    boat_speed)
            if flag is not True:
                paths.append(wp)
            else:
                wp = init_loc
        else:
            wp = boat._path[len(boat._path) - 1]
        boat._last_known_loc = wp

        while len(paths) <= _get_limit_ardu_waypoints():
            ct += 1
            logger.info(f"########## RUN NUMBER {ct} ##########")
            (flag, wp) = self._create_next_waypoint(boat, wind_dir, wind_speed,
                                                    boat_speed)
            if flag is True:
                break

            # If the boat will pass the destination within 30 meters, there is
            # no point in heading back towards it
            offset_dest = line_point_intersection(boat._last_known_loc, wp,
                                                  boat._destination)
            logger.info("closest dist to dest {0} {1} {2}".format(
                haversine_dist(offset_dest, boat._destination), offset_dest.x,
                offset_dest.y))
            if haversine_dist(
                    offset_dest,
                    boat._destination) < _get_min_distance_waypoint():
                break
            paths.append(wp)
            boat._last_known_loc = wp
            # if haversine_dist(wp, boat._destination) < 300:
            #     paths.append(boat._destination)
            #     break

        boat._last_known_loc = init_loc
        if len(paths) == 0:
            logger.warning("sleeping for", wp._wait_time,
                           "before computing again",
                           "due to collision possibility")
            sleep(wp._wait_time)
            recv = self.generate_waypoints(boat, wind_dir, wind_speed,
                                           boat_speed)
            return recv
        else:
            while len(paths) > 0:
                boat._path.append(paths.popleft())
        return boat

    def dump_path(self, boat: Boat):
        """Function that empties the current path."""
        while len(boat._path) > 0:
            boat._previous_path.append(boat._path.popleft())

    def plan_trip(self, curr_location: Point, destination: Point,
                  boat: Boat) -> Boat:
        """Uses eurostat searoute to compute the shortesh distance for ocean travel.

        Args:
            - curr_location: Current GPS location of the boat.
            - destination: Destination point.
        Returns list of midpoints, latitude and longitude are inverted.
        """
        boat.extend_mid_point(destination)
        return boat
        os.chdir(os.getcwd() + "/searoute/releases/searoute-2.1")
        file = open("test_input.csv", "w+")
        s = "route name,olon,olat,dlon,dlat\n"
        file.write(s)

        file.write(f"route,{curr_location.x},{curr_location.y},"
                   + f"{destination.x},{destination.y}")

        resolution_str = "-res " + str(_get_resolution_ocean_trip())
        bash_cmd = ("java -jar " + "searoute.jar -i " + "test_input.csv "
                    + resolution_str)
        file.close()
        process = subprocess.Popen(bash_cmd,
                                   stdout=subprocess.PIPE,
                                   cwd=os.getcwd(),
                                   shell=True,
                                   env=os.environ)
        output, error = process.communicate()
        if error is None:
            for line in output.decode()[:-1].split('\n'):
                logger.info(line)

            output_file = open("out.geojson", "r+")
            res = output_file.read()
            res = json.loads(res)
            os.chdir("../../../")
            # skip first element as it's always the origin.
            for i, item in enumerate(
                    res.get("features")[0].get("geometry").get("coordinates")
                [0]):
                if i != 0:
                    boat.extend_mid_point(Point(item[0], item[1]))
            output_file.close()
            return boat
        else:
            print(destination)

            logger.error(error)
            logger.info(output)
            boat.extend_mid_point(destination)
            return boat

    # TODO:
    # Idea is that the boat with higher priority will get an
    #  extra waypoint at the beginning.
    # After it gets past the before mentioned waypoint, upon
    #  waypoint deletion, it will notify
    # the boat that is waiting to start the planning again.
