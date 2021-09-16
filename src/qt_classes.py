"""Defines classes to be used with Qt."""
import config
from path_finding.mission_planner import MissionPlanner
from PySide2.QtCore import Property
from PySide2.QtCore import QAbstractListModel
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import QObject
from PySide2.QtCore import Signal
from PySide2.QtCore import Slot
from PySide2.QtPositioning import QGeoCoordinate
from PySide2.QtPositioning import QGeoPolygon
from shapely.geometry.point import Point


class PolygonGenerator(QObject):
    """A generator which can be used to send polygons to QML."""
    def __init__(self, data_source_method):
        """
        Create the generator and construct the QObject.

        Args:
            - data_source_method: Function to call for retrieving
            raw polygon data (must return QGeoPolygon)
        """
        QObject.__init__(self)
        self.get_polygon_data = data_source_method

    polygonChanged = Signal(QGeoPolygon)

    @Slot(QGeoPolygon)
    def __add_polygon(self, poly: QGeoPolygon):
        """Add a polygon to the QML view.

        Args:
            - poly: Which polygon we ought to add.
        """
        self.__poly = poly
        self.polygonChanged.emit(self.__poly)

    @Slot(result=QGeoPolygon)
    def get_polygon(self):
        """Gets the currently selected polygon."""
        return self.__poly

    @Slot()
    def fetchPolygon(self):
        """QML accessible function which displays the polygons on the map."""
        polygons = self.get_polygon_data()
        [self.polygonChanged.emit(pol) for pol in polygons]

    poly = Property(QGeoPolygon, get_polygon, notify=polygonChanged)


class DebugPolygonGenerator(PolygonGenerator):
    """
    A generator which can be used to send polygons to QML.

    Allows for relaying position data from inside of QML.
    """
    @Slot(float, float)
    def fetchPolygon(self, latitude: float, longitude: float):
        """
        QML accessible function which displays the polygons on the map.

        Args:
            - latitude: Latitude of the point to construct the
            fence polygon around
            - longitude: Longitude of the point to construct the
            fence polygon around
        """
        polygons = self.get_polygon_data(latitude, longitude)
        [self.polygonChanged.emit(pol) for pol in polygons]


class MissionPathModel(QAbstractListModel):
    """A model which stores the points on the current mission."""

    missionChanged = Signal()

    def __init__(self, parent=None):
        """Create the model object and initiaze the QT object."""
        super().__init__(parent)
        self._location = QGeoCoordinate(52.40359289862932, 4.662117677145794)
        self._target = QGeoCoordinate(52.40757766975709, 4.663778575775887)
        self._mission_paths = [self._location, self._target]

    def rowCount(self, parent=QModelIndex()):
        """Fetches the number of points on the path."""
        return len(self._mission_paths)

    def roleNames(self):
        """Returns the roles that the data can take."""
        return {MissionPathModel.Both: b"both"}

    def add(self, point: QGeoCoordinate) -> None:
        """Adds a coordinate to the path."""
        self._mission_paths.append(point)

    @Slot(int, result=QGeoCoordinate)
    def get(self, index: int):
        """QML accessible function to get data from the array.

        Args:
          index: Location of the data on the array,

        Returns:
          A QT representation of the next coordinate.
        """
        try:
            return self._mission_paths[index]
        except IndexError:
            return None

    @Slot()
    def clear(self):
        """QML accessible function to delete all the points of the mission."""
        self._mission_paths = []

    @Slot()
    def addSignal(self):
        """QML accessible function which adds some points to the list."""
        self.add(QGeoCoordinate(52.403747, 4.660064))
        self.add(QGeoCoordinate(52.408165, 4.667674))
        self.missionChanged.emit()

    @Slot(float, float, float, float)
    def createPath(self, boat_lat: float, boat_long: float, dest_lat: float,
                   dest_long: float):
        """QML accessible function which creates a new path.

        Generates points for path to given destination.

        Args:
            - boat_lat: Current latitude of boat
            - boat_long: Current longitude of boat
            - dest_lat: Latitude of desired destination
            - dest_long: Longitude of desired destination
        """
        mis = MissionPlanner()

        # Create boat object and trip
        boat_id = 23
        boat_origin = Point(boat_long, boat_lat)
        boat_destination = Point(dest_long, dest_lat)
        boat = mis.add_new_mission(boat_id, boat_origin, boat_destination)
        boat = mis.generate_waypoints(boat, 50, 18, 20)

        self.clear()
        while len(boat._path) > 0:
            waypoint = boat._path.popleft()
            self.add(QGeoCoordinate(waypoint.y, waypoint.x))
        self.missionChanged.emit()


class ConfigFile(QObject):
    """Singleton class for config file."""
    def __init__(self, parent=None):
        """Create wrapper class around the Python config parser."""
        super().__init__(parent)
        self._config = config.ConfigFile()

    @Slot(str, str, result=str)
    def general_getter(self, topic: str, spec: str):
        """A general getter for a given topic and specification.

        Args:
            - topic: Configuration file topic to search in
            - spec: Name of item to fetch
            - data_type: Specifies how to process parsed value
        """
        return self._config.general_getter(topic, spec)

    @Slot(str, str, str)
    def write_to_file(self, topic: str, spec: str, val):
        """Write the given value to a (possibly new) spec in the config file.

        Args:
            - topic: Configuration file topic to write within
            - spec: Item name to bind value to
            - val: Value to write to config file
        """
        self._config.write_to_file(topic, spec, val)

    def add_topic(self, topic: str) -> None:
        """Add a new topic to the config file.

        Args:
            - topic: Name of new topic to add
        """
        self._config.add_topic(topic)
