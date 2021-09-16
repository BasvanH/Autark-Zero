"""Mqtt Client Singleton class."""
import json
import logging
from random import randint

import config
import send_commands
from paho.mqtt import client as mqtt
from path_finding.obstacle import Obstacle
from path_finding.obstacle import ObstacleList
from shapely.geometry import Point
from singleton_metaclass import Singleton
from telemetry import Telemetry

config_parser = config.ConfigFile()


def _get_mqtt_client_name() -> str:
    return config_parser.general_getter("MQTT_CONFIG", "CLIENT_NAME") \
        + str(randint(0, 1000000))


def _get_mqtt_broker() -> str:
    return config_parser.general_getter("MQTT_CONFIG", "BROKER")


def _get_mqtt_topic_gps() -> str:
    return config_parser.general_getter("MQTT_TOPICS", "GPS")


def _get_mqtt_topic_commands() -> str:
    return config_parser.general_getter("MQTT_TOPICS", "OPENHAB_COMMANDS")


def _get_mqtt_topic_wind() -> str:
    return config_parser.general_getter("MQTT_TOPICS", "WINDMETER")


def _get_mqtt_topic_destination() -> str:
    return config_parser.general_getter("MQTT_TOPICS", "DESTINATION")


class MqttConnectorClass(metaclass=Singleton):
    """Mqtt Client class."""
    def __init__(self):
        """Init function."""
        self._connect()

    def _connect(self):
        self.client = mqtt.Client(_get_mqtt_client_name())
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.connect(_get_mqtt_broker())
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection event callback handler.

        Logs connection attempt result code and subscribes to
        relevant topics.
        """
        logging.getLogger("log.mqtt").info(
            f"MQTT client connected with result code {str(rc)}")
        topic_qos_pair_list = [(_get_mqtt_topic_gps(), 0),
                               (_get_mqtt_topic_commands(), 0),
                               (_get_mqtt_topic_wind(), 0),
                               (_get_mqtt_topic_destination(), 0)]
        self.client.subscribe(topic_qos_pair_list)

    def on_message(self, client, userdata, message) -> None:
        """MQTT message callback handler."""
        try:
            payload = json.loads(message.payload)
        except json.decoder.JSONDecodeError:
            logging.getLogger("log.mqtt").error("Can't parse: "
                                                + message.payload.decode())
            return

        if 'commands' in payload:
            self.on_message_command(client, userdata, message)
        elif message.topic == 'sensors/windmeter':
            self.on_message_wind(client, userdata, message)
        elif message.topic == 'object':
            self.on_message_object(client, userdata, message)
        elif message.topic == 'sensors/gps':
            self.on_message_gps(client, userdata, message)
        else:
            logging.getLogger("log.mqtt").error("Wrong topic: %s",
                                                message.topic)

    def on_message_wind(self, client, userdata, message) -> None:
        """Calls function in telemetry class to update variables."""
        tel = Telemetry()
        tel.on_message_wind(client, userdata, message)

    @staticmethod
    def on_message_command(client, userdata, message) -> None:
        """Calls Commands message handler."""
        send_commands.on_message(client, userdata, message)

    @staticmethod
    def on_message_object(_, __, message):
        """Adds obstacle instance to list."""
        payload = json.loads(message.payload)
        latitude = float(payload["latitude"])
        longitude = float(payload["longitude"])
        speed = float(payload["speed"])
        size = float(payload["size"])
        angle = float(payload["angle"])
        list_ = ObstacleList()
        list_.add_object(
            Obstacle(Point(longitude, latitude), speed, size, angle))

    @staticmethod
    def on_message_gps(client, userdata, message) -> None:
        """MQTT callback function meant for GPS data topic.

        On receiving new data, it updates the current location around
        which the geofence should be generated.

        Args:
            client: The client instance for this callback
            userdata: The private user data as set in Client() or user_data_set
            message: An instance of MQTTMessage. This is a class with members
               topic, payload, qos, retain.
        """
        import geofence
        payload = json.loads(message.payload)
        latitude = float(payload["latitude"])
        longitude = float(payload["longitude"])
        geofence.current_location = Point(longitude, latitude)
