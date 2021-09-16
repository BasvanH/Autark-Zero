"""This config is responsible for reading global variables."""
import configparser
from enum import Enum
from typing import Any
from typing import List
from typing import Tuple
from typing import Union

from singleton_metaclass import Singleton

CONFIG_FILE_NAME = "configfile.ini"


class DataType(Enum):
    """Enum class for indicating desired return type from config parser."""
    BOOLEAN = 'BOOLEAN'
    INT = 'INT'
    FLOAT = 'FLOAT'
    STRING = 'STRING'


class ConfigFile(metaclass=Singleton):
    """Singleton class for config file."""
    def __init__(self):
        """Create wrapper class around the Python config parser."""
        self._config_var = configparser.ConfigParser()
        self._config_var.read(CONFIG_FILE_NAME)

    def get_section(self, topic: str) -> List[Tuple[str, str]]:
        """Gets all the values from a section and returns them as list.

        Args:
           - topic: The name of the topic that you would like to see.

        Returns:
           A structured list of the values in that topic.
        """
        return list(self._config_var[topic].items())

    def general_getter(self,
                       topic: str,
                       spec: str,
                       data_type: DataType = DataType.STRING
                       ) -> Union[bool, int, float, str]:
        """A general getter for a given topic and specification.

        Args:
            - topic: Configuration file topic to search in
            - spec: Name of item to fetch
            - data_type: Specifies how to process parsed value
        """
        if data_type == DataType.BOOLEAN:
            return self._config_var[topic].getboolean(spec)
        elif data_type == DataType.INT:
            return self._config_var[topic].getint(spec)
        elif data_type == DataType.FLOAT:
            return self._config_var[topic].getfloat(spec)
        else:
            return self._config_var[topic][spec]

    def write_to_file(self, topic: str, spec: str, val: Any) -> None:
        """Write the given value to a (possibly new) spec in the config file.

        Args:
            - topic: Configuration file topic to write within
            - spec: Item name to bind value to
            - val: Value to write to config file
        """
        self._config_var[topic][spec] = val
        with open('configfile.ini', 'w') as config_set:
            self._config_var.write(config_set)

    def add_topic(self, topic: str) -> None:
        """Add a new topic to the config file.

        Args:
            - topic: Name of new topic to add
        """
        self._config_var.add_section(topic)
