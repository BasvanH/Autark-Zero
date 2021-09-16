"""Singleton class for a MAVLink GCS connection."""
import logging
from typing import List

from pymavlink import mavutil
from pymavlink import mavwp
from pymavlink.dialects.v20 import ardupilotmega as mavlink2
from shared_data import OsmNodeData
from singleton_metaclass import Singleton


class MavlinkClient(metaclass=Singleton):
    """Creates a link to the ArduPilot using MAVLink."""
    def __init__(self, device: str = "udpin:127.0.0.1:14551") -> None:
        """Create a new MAVLink connection.

        Add a connection and wait for a heartbeat to fetch target
        system and target component.

        Args:
        - device: A string defining how to connect to the
            desired MAVLink-enabled device. See:
        https://github.com/ArduPilot/pymavlink/blob/fe0651f9be6d1efeaed3d4e53ef5ea533ee64c51/mavutil.py#L1635

        """
        # Start a connection listening to a UDP port
        self.mav_con = mavutil.mavlink_connection(device, input=True)
        mavutil.set_dialect("ardupilotmega")
        self.mav_con.wait_heartbeat()

        # Create geofence loader and set fence initially to off
        self.fence_loader = mavwp.MAVFenceLoader(self.mav_con.target_system,
                                                 self.mav_con.target_component)
        self.fence_enable = False

    def _enable_geofence(self) -> None:
        """Set various geofence-related ArduPilot params.

        The final parameter indicates the type of data
        provided. Parameters are NOT associated with a particular
        type, the given type just needs to match the size and type of
        data provided in the message.

        See:
          https://ardupilot.org/rover/docs/parameters.html#fence-parameters
        """
        self.mav_con.mav.param_set_send(
            self.mav_con.target_system,
            self.mav_con.target_component,
            b"FENCE_ENABLE",
            1,
            mavlink2.MAVLINK_TYPE_UINT8_T,
        )  # Enable geofence functionality
        self.mav_con.mav.param_set_send(
            self.mav_con.target_system,
            self.mav_con.target_component,
            b"FENCE_MARGIN",
            10,
            mavlink2.MAVLINK_TYPE_UINT8_T,
        )  # Set distance from fence that constitutes breach to 10 metres
        self.mav_con.mav.param_set_send(
            self.mav_con.target_system,
            self.mav_con.target_component,
            b"FENCE_ACTION",
            2,
            mavlink2.MAVLINK_TYPE_UINT8_T,
        )  # Set fence breach action to hold current position
        self.fence_enable = True

    def transmit_geofence(self, points: List[OsmNodeData], home_lat: float,
                          home_long: float) -> None:
        """Transmit the geofence represented by the given data to ArduPilot.

        Args:
            - points: The points defining the fence
            - home_lat: The latitude to use for the home point
            - home_long: The longitude to use for the home point
        """
        if not self.fence_enable:
            self._enable_geofence()

        # First point is the return point
        # Last point is fucking chucked lmao
        # Actual polygon points are the ones from indices 1 to size-2
        # https://github.com/ArduPilot/ardupilot/blob/8a3a609e3ba80597484455b97d7589bd81c95c16/libraries/AC_Fence/AC_PolyFence_loader.cpp#L305
        self.fence_loader.clear()
        self.fence_loader.add_latlon(home_lat, home_long)
        [
            self.fence_loader.add_latlon(pt.latitude, pt.longitude)
            for pt in points
        ]
        self.fence_loader.add_latlon(32.67598384588704, -117.1578359851244)

        # Transmit point data
        # Set the number of geofence waypoints
        self.mav_con.mav.param_set_send(
            self.mav_con.target_system,
            self.mav_con.target_component,
            b"FENCE_TOTAL",
            self.fence_loader.count(),
            mavlink2.MAVLINK_TYPE_UINT8_T,
        )

        for idx in range(self.fence_loader.count()):
            point = self.fence_loader.point(idx)
            self.mav_con.mav.send(point)
        logging.getLogger("log.mavlink").info(
            "Geofence successfully transmitted")
