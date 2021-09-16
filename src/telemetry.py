"""This module is used for getting telemetry from Ardupilot."""
import json
import logging
import time

import config
import mavlink_client
from path_finding.mission_planner import MissionPlanner
from singleton_metaclass import Singleton

config_parser = config.ConfigFile()
MQTT_TOPIC_COMPASS = config_parser.general_getter("MQTT_TOPICS", "COMPASS")
MQTT_TOPIC_GPS = config_parser.general_getter("MQTT_TOPICS", "GPS")
MQTT_TOPIC_SPEED = config_parser.general_getter("MQTT_TOPICS", "SPEED")

logger = logging.getLogger("log.telemetry")


class Telemetry(metaclass=Singleton):
    """Singleton class for telemetry."""
    def __init__(self):
        """Get mav_con instant and setup values."""
        self._heading = 0
        self._speed = 0
        self._id = 0
        self._miss = MissionPlanner()
        self._gps_lat = 0
        self._gps_lon = 0
        self._wind_speed = 0
        self._wind_direction = 0
        self._satellites_visible = None

    def get_speed(self):
        """Return the Speed of the boat in KPH."""
        return self._speed

    def get_gps(self):
        """Return GPS Position."""
        return self._gps_lon, self._gps_lat

    def get_heading(self):
        """Return Geo Compass Reading."""
        return self._heading

    def get_id(self):
        """Returns the id."""
        return self._id

    def send_telemetry(self, mqtt_client):
        """Runs in a thread, this function receives and sending telemetry."""
        # Get MAVLink client singleton instance.
        master = mavlink_client.MavlinkClient().mav_con

        while True:
            time.sleep(0.1)
            try:
                message = master.recv_match(blocking=True).to_dict()
                if message["mavpackettype"] == "VFR_HUD":
                    self.send_vfr(message, mqtt_client)
                elif message["mavpackettype"] == "GPS_RAW_INT":
                    self.send_gps(message, mqtt_client)
                elif message["mavpackettype"] == "MISSION_ITEM_REACHED":
                    self.waypoint_reached(message)
            except Exception as error:
                logger.error(error)
                continue

    def waypoint_reached(self, message):
        """Callback when a waypoint is reached."""
        self._miss._update_mission(message["seq"], self._wind_direction,
                                   self._wind_speed, self._speed)

    def send_gps(self, message, mqtt_client):
        """Extract and send GPS data."""
        # Convert from ArduPilot's degE7 format
        # (https://mavlink.io/en/messages/common.html#GPS_RAW_INT)
        self._gps_lat = float(message["lat"]) / 1e7
        self._gps_lon = float(message["lon"]) / 1e7
        self._satellites_visible = message["satellites_visible"]

        payload = {
            "latitude": self._gps_lat,
            "longitude": self._gps_lon,
            "satellites_visible": self._satellites_visible
        }
        mqtt_client = mqtt_client.client
        mqtt_client.publish(MQTT_TOPIC_GPS, json.dumps(payload), 0, True)

    def send_vfr(self, message, mqtt_client):
        """Extract and send VFR data."""
        self._heading = message["heading"]
        self._speed = message["groundspeed"]
        payload = {"heading": self._heading, "gspeed": self._speed}
        mqtt_client = mqtt_client.client
        mqtt_client.publish(MQTT_TOPIC_COMPASS, json.dumps(payload), 0, True)
        mqtt_client.publish(MQTT_TOPIC_SPEED, json.dumps(payload), 0, True)

    def on_message_wind(self, _, __, message):
        """Updates local variables."""
        self._wind_direction = message["direction"]
        self._wind_speed = message["speed"]
