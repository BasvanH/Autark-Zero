"""Defines functionality for sending commands to ArduPilot."""
import json
import logging
from enum import Enum
from typing import List

import config
from mavlink_client import MavlinkClient
from paho.mqtt import client as mqtt
from pymavlink import mavutil
from pymavlink import mavwp
from pymavlink.dialects.v20 import ardupilotmega as mavlink2
from pymavlink.dialects.v20 import common as mavlink
from shapely.geometry import Point
from singleton_metaclass import Singleton
from telemetry import Telemetry

config_parser = config.ConfigFile()

DEBUG_MQTT_CLIENT_NAME = config_parser.general_getter("MQTT_CONFIG",
                                                      "CLIENT_NAME")
DEBUG_MQTT_BROKER = config_parser.general_getter("MQTT_CONFIG", "BROKER")
DEBUG_MQTT_TOPIC = config_parser.general_getter("MQTT_TOPICS",
                                                "OPENHAB_COMMANDS")


def _get_get_home_attempt_limit() -> int:
    """Fetch home attempt limit.

    Upper limit on number of chained attempts to retrieve home position.
    """
    return config_parser.general_getter("MAVLINK", "GET_HOME_ATTEMPT_LIMIT",
                                        config.DataType.INT)


class Mode(Enum):
    """
    AP modes.

    Only Allow for relevant MODES.

    'https://ardupilot.org/rover/docs/rover-control-modes.html'
    """
    # RC control.
    ACRO = "ACRO"
    # Auto mode the vehicle will follow a pre-programmed mission.
    AUTO = "AUTO"
    # Guided mode is designed to allow ground stations.
    GUIDED = "GUIDED"
    # Hold position.
    LOITER = "LOITER"
    # More Direct RC control.
    MANUAL = "MANUAL"


class Commands(Enum):
    """Commands."""
    RTL = "RTL"
    ADD_WAYPOINT = "ADD_WAYPOINT"
    CLEAR_WAYPOINTS = "CLEAR_WAYPOINTS"
    TACK = "TACK"
    ARM = "ARM"
    DISARM = "DISARM"
    ADD_WAYPOINTS = "ADD_WAYPOINTS"
    WRITE_LOG = "WRITE_LOG"
    MODE = "MODE"

    @classmethod
    def has_key(cls, cmd):
        """Checks cmd is supported."""
        return cmd in cls.__members__


class Commander(metaclass=Singleton):
    """Class that Handles commands to AP."""
    def __init__(self):
        """Init the Mavlink connection and MAVWP."""
        self.master = MavlinkClient()
        self.wp = mavwp.MAVWPLoader()
        self.sq = 0

    def set_mode(self, mode):
        """Set mode in AP.

        Validate if the mode is supported then generate message.
        Wait for ACK response.
        """
        try:
            m = Mode(mode)

            if m.value in self.master.mav_con.mode_mapping():
                mode_id = self.master.mav_con.mode_mapping()[m.value]
                self.master.mav_con.mav.set_mode_send(
                    self.master.mav_con.target_system,
                    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)

                # wait for response
                msg = self.master.mav_con.recv_match(type="COMMAND_ACK",
                                                     blocking=True,
                                                     timeout=5)
                if msg is not None:
                    if msg.result == 0:
                        logging.getLogger("log.mavlink").info(
                            "ACK received: Mode set to %s", m.value)
                    elif msg.result == 4:
                        logging.getLogger("log.mavlink").info(
                            "ACK received: Setting mode failed: %s", m.value)
                    elif msg.result == 2:
                        logging.getLogger("log.mavlink").error(
                            "ACK received: Setting mode denied: %s", m.value)
                    elif msg.result == 6:
                        logging.getLogger("log.mavlink").info(
                            "ACK received: Setting mode in progress : %s",
                            m.value)
                else:
                    logging.getLogger("log.mavlink").error(
                        "Mode change ACK timeout.")

        except ValueError:
            logging.getLogger("log.error").error("Unsupported Mode: %s", mode)

    def get_home(self, num_attempts: int = 0) -> Point:
        """Return current ArduPilot home position.

        Returns a Shapely point with customary flipped coordinates
        (x => longitude, y => latitude)

        Args:
            - num_attempts: Number of chained attempts so far.
            Used to limit number of retries
        """
        self.master.mav_con.mav.command_long_send(
            self.master.mav_con.target_system,
            self.master.mav_con.target_component,
            mavlink.MAV_CMD_GET_HOME_POSITION, 0, 0, 0, 0, 0, 0, 0, 0)

        home = self.master.mav_con.recv_match(type=['HOME_POSITION'],
                                              blocking=True,
                                              timeout=3)
        if home is None:
            if num_attempts < _get_get_home_attempt_limit():
                logging.getLogger("log.mavlink").error(
                    "Home position request failed, retrying...(req depth %s)",
                    num_attempts + 1)
                return self.get_home(num_attempts + 1)
            logging.getLogger("log.mavlink").error(
                "Home position request attempt limit reached")
            raise RuntimeError("Home position request attempt limit reached")
        return Point(float(home.longitude) / 1e7, float(home.latitude) / 1e7)

    def return_to_home(self) -> None:
        """Issue a return to launch command.

        See (https://ardupilot.org/rover/docs/rtl-mode.html)
        """
        self.master.mav_con.mav.command_long_send(
            self.master.mav_con.target_system,
            self.master.mav_con.target_component,
            mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0)
        logging.getLogger("log.mavlink").info("RTL command sent")

    def add_path(self, lat: float, lon: float) -> None:
        """Generate and upload a path to the given point.

        Utilises the pathfinding functionality to generate waypoints
        to upload as a mission.

        Args:
            - lat: Latitude of destination
            - lon: Longitude of destination
        """
        # Generate path
        dest = Point(lon, lat)
        telemetry = Telemetry()
        boat = telemetry._miss.add_new_mission(
            23, Point(telemetry._gps_lon, telemetry._gps_lat), dest)
        telemetry._miss.generate_waypoints(boat, telemetry._wind_direction,
                                           telemetry._wind_speed,
                                           telemetry._speed)

        # Attempt upload and log result
        path = list(boat._path.copy())
        upload_success = self.add_waypoints(path)
        if upload_success:
            logging.getLogger("log.mavlink").info(
                "Mission upload success - Destination (%s, %s)", lat, lon)
        else:
            logging.getLogger("log.mavlink").error(
                "Mission upload fail - Destination (%s, %s)", lat, lon)

    def add_waypoints(self, points: List[Point]) -> bool:
        """
        Upload the given list of points to ArduPilot as a mission.

        Return boolean indicating success or failure of operation.

        Args:
            points: Points defining path to travel along
        """
        # Populate waypoint loader list
        # First point is home location as per ArduPilot spec
        # https://mavlink.io/en/services/mission.html#flight-plan-missions
        self.clear_waypoints()
        points.insert(0, self.get_home())
        for i in points:
            self.wp.add_latlonalt(i.y, i.x, 0)
        self.master.mav_con.waypoint_count_send(self.wp.count())

        upload_success = False
        counter = len(points)
        last = -1
        while (not upload_success) and counter >= 0:
            msg = self.master.mav_con.recv_match(
                type=['MISSION_REQUEST', 'MISSION_ACK'],
                blocking=True,
                timeout=5)
            if msg is None:
                logging.getLogger("log.mavlink").error(
                    "Mission request timeout")
                break

            # Handle ACK message
            if msg.to_dict()["mavpackettype"] == 'MISSION_ACK':
                if msg.type == 0:
                    logging.getLogger("log.mavlink").info(
                        "Waypoints upload success (%s uploaded)", len(points))
                    upload_success = True
                elif msg.type == 13:
                    logging.getLogger("log.mavlink").warning(
                        "Upload failed (code %s)", msg.type)
                else:
                    logging.getLogger("log.mavlink").warning(
                        "ACK with code %s", msg.type)
                break

            if last == msg.seq:  # Skip already sent message
                continue
            wp_msg = self.wp.wp(msg.seq)
            wp_msg.seq = msg.seq  # Set correct sequence number
            self.master.mav_con.mav.send(wp_msg)
            last = msg.seq
            counter -= 1
        return upload_success

    def tack(self) -> None:
        """Issue a tack command.

        Tacking corresponds to auxiliary command 63
        (https://ardupilot.org/rover/docs/common-auxiliary-functions.html)
        """
        self.master.mav_con.mav.command_long_send(
            self.master.mav_con.target_system,
            self.master.mav_con.target_component,
            mavlink2.MAV_CMD_DO_AUX_FUNCTION, 1, 63, 2, 0, 0, 0, 0, 0)
        logging.getLogger("log.mavlink").info("Tack command sent")

    def clear_waypoints(self) -> None:
        """Clears all waypoints."""
        self.wp.clear()
        self.master.mav_con.waypoint_clear_all_send()

        ack_msg = self.master.mav_con.recv_match(type='MISSION_ACK',
                                                 blocking=True,
                                                 timeout=3)
        if ack_msg is None:
            logging.getLogger("log.mavlink").error(
                "Waypoint clear ACK timeout")
        else:
            if ack_msg.type == 0:
                logging.getLogger("log.mavlink").info(
                    "Waypoint clear ACK success")
            else:
                self.add_waypoints([])
                logging.getLogger("log.mavlink").debug(
                    "Waypoint clear ACK none Zero, Sending a blank mission.")

    def arm(self) -> None:
        """Arms the vehicle."""
        self.master.mav_con.mav.command_long_send(
            self.master.mav_con.target_system,
            self.master.mav_con.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0,
            0)
        logging.getLogger("log.mavlink").info("Arm command sent")

        # wait for response
        msg = self.master.mav_con.recv_match(type="COMMAND_ACK",
                                             blocking=True,
                                             timeout=5)

        if msg is not None:
            if msg.result == 0:
                logging.getLogger("log.mavlink").info("Arm success")
            else:
                logging.getLogger("log.mavlink").error(
                    "Arm not successful with result %s", msg.result)
        else:
            logging.getLogger("log.mavlink").error("Timeout, no ACK received.")

    def disarm(self) -> None:
        """Disables Nuclear Reactor."""
        self.master.mav_con.mav.command_long_send(
            self.master.mav_con.target_system,
            self.master.mav_con.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0,
            0)
        logging.getLogger("log.mavlink").info("Disarm command sent")

        # wait for response
        msg = self.master.mav_con.recv_match(type="COMMAND_ACK",
                                             blocking=True,
                                             timeout=5)

        if msg is not None:
            if msg.result == 0:
                logging.getLogger("log.mavlink").info("Disarm success")
            else:
                logging.getLogger("log.mavlink").error(
                    "Disarm not successful with result %s", msg.result)
        else:
            logging.getLogger("log.mavlink").error("Timeout, no ACK received.")


def on_message(client, userdata, message):
    """Handles MQTT commands."""
    if message.retain == 1:
        logging.getLogger("log.mqtt").info("Ignoring Retained Message")
        return

    payload = None
    try:
        payload = json.loads(message.payload)
    except json.decoder.JSONDecodeError as e:
        logging.getLogger('log.mqtt').error(e)
        return

    logging.getLogger("log.mqtt").info(payload["commands"] + " received")
    if payload["commands"] == Commands.RTL.value:
        Commander().return_to_home()
    elif payload["commands"] == Commands.ADD_WAYPOINT.value:
        try:
            Commander().add_path(payload["lat"], payload["lon"])
        except KeyError:
            logging.getLogger("log.mqtt").error("Wrong or Missing Waypoint")
    elif payload["commands"] == Commands.CLEAR_WAYPOINTS.value:
        Commander().clear_waypoints()
    elif payload["commands"] == Commands.TACK.value:
        Commander().tack()
    elif payload["commands"] == Commands.ARM.value:
        Commander().arm()
    elif payload["commands"] == Commands.DISARM.value:
        Commander().disarm()
    elif payload["commands"] == Commands.ADD_WAYPOINTS.value:
        points = [
            Point(4.75481445, 52.54781416),
            Point(4.75481945, 52.54791416)
        ]
        Commander().add_waypoints(points)
    elif payload["commands"] == Commands.MODE.value:
        try:
            Commander().set_mode(payload["mode"])
        except KeyError:
            logging.getLogger("log.mqtt").error("Wrong or mission mode.")
    else:
        logging.getLogger("log.mqtt").error("Command %s not supported",
                                            payload["commands"])


if __name__ == "__main__":
    """Run the module on its own for debugging."""

    # Set up MQTT client
    mqtt_client = mqtt.Client(DEBUG_MQTT_CLIENT_NAME)
    mqtt_client.on_message = on_message
    mqtt_client.connect(DEBUG_MQTT_BROKER)
    mqtt_client.subscribe(DEBUG_MQTT_TOPIC)
    mqtt_client.loop_start()
    print("MQTT client successfully connected")

    Commander()
    while True:
        pass
