Introduction and background
============================
This project was initially developed by Valentijn van de Beek, William
Narchi, Meeher Kapoor, Omar Thabet, and Silviu Marii for the Software
Project course at the Delft University of Technology. It was conceived
in order to mitigate some of the shortcomings of the software used on
the Autark Zero. In particular it aims to improve the path finding by
taking the outlines of the water into account, provides object
avoidance, and allows for communication with OpenHAB.


Features
-----------

* Qt-based debugging application written in QML and Python.
* Configurable parameters and settings.
* Communication to ArduPilot over MAVLink.
* Sending Telemetry data to OpenHAB.
* Parsing commands from OpenHAB and sending to the Autark.
* Generating Geofences based on the current location of the boat.
* Finding a short path using OpenStreetMap data.
* Simple object-avoidance.
* A MQTT interface to receive new objects from external programs.
* Finding paths over large distances.
* Working command-line interface.
* Using flags in order to enable or disable features.
* Logging important messages.

To do
--------------------

* Make use of a custom dataset as indicated by the client.
* Avoid using GeoSeries.
* Add objects using the Qt interface.
* Medium distance path finding.
* MAVLink over serial
* Test deployment of the GUI on mobile phones. Currently it only works
  for Pure OS.
* Add rally points.


Software Used
--------------------

* `Python <https://www.python.org/>`_.
* `Qt <https://qt.io/>`_.
* `ArduPilot <https://ardupilot.org/>`_.
* `Shapely <https://shapely.readthedocs.io/en/stable/manual.html>`_ (geometry library).
* `Overpass <https://python-overpy.readthedocs.io/en/latest/>`_ (OpenStreetMap API).
* `PySide 2 <https://wiki.qt.io/Qt_for_Python>`_ (Qt Python Library).
* `pymavlink <https://github.com/ArduPilot/pymavlink>`_ (MAVLink bindings).
* `paho-mqtt <https://www.eclipse.org/paho/index.php?page=clients/python/index.php>`_ (Python MQTT Library).

We owe a huge debt to these open source developers. Without their high
quality software, this project would be nowhere near the state that is
now.
