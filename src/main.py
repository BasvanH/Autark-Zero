"""Defines the main application and some helper functions."""
import logging
import os
import sys
import threading
from pathlib import Path

import config
import qt_classes
import qt_utils
import send_commands
import telemetry
from cli import BufferAwareCompleter
from geofence import generate_fence_from_mqtt
from logger import Logger
from mqtt import MqttConnectorClass
from path_finding.mission_planner import MissionPlanner
from PySide2.QtGui import QGuiApplication
from PySide2.QtPositioning import QGeoCoordinate
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtWidgets import QApplication
from shapely.geometry import Point

# Compatibility for Windows plebs
try:
    import readline
except ImportError:
    import pyreadline as readline  # type: ignore


def _init_qt() -> None:
    """Initialise Qt visual application."""
    if not QApplication.instance():
        app = QGuiApplication(sys.argv)
    else:
        app = QApplication.instance()

    engine = QQmlApplicationEngine()

    # Connect generators for fence debug
    ardupilot_fence_generator = qt_classes.PolygonGenerator(
        qt_utils.get_ardupilot_polygons)
    debug_fence_generator = qt_classes.DebugPolygonGenerator(
        qt_utils.get_debug_fence_polygons)
    config_generator = qt_classes.ConfigFile()
    engine.rootContext().setContextProperty("ardupilotFenceGenerator",
                                            ardupilot_fence_generator)
    engine.rootContext().setContextProperty("debugFenceGenerator",
                                            debug_fence_generator)
    engine.rootContext().setContextProperty("config", config_generator)

    # Define starting boat info
    BOAT_ID = 23
    BOAT_ORIGIN = Point(4.660064, 52.403747)
    BOAT_DESTINATION = Point(4.673076, 52.407898)

    telemetry_class = telemetry.Telemetry()
    mis = MissionPlanner()

    # Create boat and trip
    boat = mis.add_new_mission(BOAT_ID, BOAT_ORIGIN, BOAT_DESTINATION)
    boat = mis.generate_waypoints(boat, 130, 18, telemetry_class.get_speed())
    # boat = mis.plan_trip(BOAT_ORIGIN, BOAT_DESTINATION, boat) No need to call

    # Add path point to Qt
    mission_list = qt_classes.MissionPathModel()
    mission_list.clear()
    while len(boat._path) > 0:
        wp = boat._path.popleft()
        mission_list.add(QGeoCoordinate(wp.y, wp.x))
    mission_list.missionChanged.emit()
    engine.rootContext().setContextProperty("missionList", mission_list)

    # Start up Qt application
    engine.load(os.fspath(Path(__file__).resolve().parent / "../qml/main.qml"))
    if not engine.rootObjects():
        sys.exit(-1)
    app.exec_()


def _start_telemetry():
    """Starts the telemetry thread."""
    mqtt_client = MqttConnectorClass()
    telemetry_class = telemetry.Telemetry()
    telemetry_thread = threading.Thread(target=telemetry_class.send_telemetry,
                                        args=(mqtt_client, ),
                                        daemon=True)
    telemetry_thread.start()


def _start_mavlink_geofence():
    """Starts a thread for transmiting geofence data to ArduPilot."""
    mavlink_geofence_thread = threading.Thread(target=generate_fence_from_mqtt,
                                               daemon=True)
    mavlink_geofence_thread.start()


def _console() -> None:
    # Disable console logging
    console_handler = Logger()._ch
    logging.getLogger("log").removeHandler(console_handler)

    conf = config.ConfigFile()
    completer = BufferAwareCompleter({
        'exit': [],
        'qt': [],
        'telemetry': [],
        'commander': [],
        'geofence': [],
        'config': ['get', 'set']
    })
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode emacs')

    while True:
        cmd = [x.strip().lower() for x in input("> ").strip().split(' ')]
        if cmd[0] == "exit":
            sys.exit(0)
        elif cmd[0] == "qt":
            _init_qt()
        elif cmd[0] == "telemetry":
            _start_telemetry()
        elif cmd[0] == "commander":
            send_commands.Commander()
        elif cmd[0] == "geofence":
            _start_mavlink_geofence()
        elif cmd[0] == "config" and cmd[1] == "get":
            conf = config.ConfigFile()
            try:
                if len(cmd) == 4:
                    print(
                        "Result: "
                        + conf.general_getter(cmd[2].upper(), cmd[3].upper()))
                elif len(cmd) == 3:
                    for item in conf.get_section(cmd[2].upper()):
                        print(f"{item[0].upper()}={item[1]}")
                    print('')
                else:
                    print("Invalid number of arguments")
            except IndexError:
                print("Invalid number of arguments")
            except KeyError:
                print("Cannot find item: " + ' '.join(cmd[2:]).upper())
        elif cmd[0] == "config" and cmd[1] == "set":
            conf = config.ConfigFile()
            if len(cmd) != 5:
                print("Invalid number of arguments")

            conf = config.ConfigFile()
            conf.write_to_file(cmd[2].upper(), cmd[3].upper(), cmd[4])
        else:
            print("Cannot find command '" + str(cmd) + "'")


def _handle_arguments() -> None:
    """Process commandline arguments to enable program features."""
    # Check used arguments
    all_features = ("--all" in sys.argv) or ("-a" in sys.argv)
    ardupilot_commands = "--with-commands" in sys.argv
    ardupilot_geofence = "--with-geofence" in sys.argv
    ardupilot_telemetry = "--with-telemetry" in sys.argv
    qt_visual = "--with-qt" in sys.argv

    # Enable features according to arguments
    if ardupilot_commands or all_features:
        send_commands.Commander()
    if ardupilot_geofence or all_features:
        _start_mavlink_geofence()
    if ardupilot_telemetry or all_features:
        _start_telemetry()
    if qt_visual or all_features:
        _init_qt()

    # CLI if visual portion is not enabled
    if not (qt_visual or all_features):
        _console()


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    logger = Logger()
    mqtt_client = MqttConnectorClass()

    _handle_arguments()
