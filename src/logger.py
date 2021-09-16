"""Module used for logging."""
import logging
from pathlib import Path

from singleton_metaclass import Singleton


class Logger(metaclass=Singleton):
    """Logger Object, used to log MQTT, MAVLINK and Error Messages."""
    def __init__(self):
        """Constructor for the logger class."""
        Path("logs/").mkdir(parents=True, exist_ok=True)
        logging.getLogger("log").setLevel(logging.DEBUG)

        # create console handler and set level to debug
        self._ch = logging.StreamHandler()
        self._ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter(
            '[%(levelname)s] %(asctime)s - %(name)s - %(message)s', '%H:%M:%S')

        # add formatter to ch
        self._ch.setFormatter(formatter)

        # add ch to logger
        logging.getLogger("log").addHandler(self._ch)

        logging.basicConfig(
            filename='logs/logs.txt',
            filemode='a+',
            level=logging.DEBUG,
            format='[%(levelname)s] %(asctime)s - %(name)s: %(message)s')
