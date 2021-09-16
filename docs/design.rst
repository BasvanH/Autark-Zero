Design and Structure
====================
The design of the program is based around a core program which can be
run using just a command-line interface with optional features which
can be enabled or disabled at will.

Currently, this program consists out of four sections:

1. Geofence generation
2. Path finding + Object Avoidance
3. Qt debugging application
4. Communicating from OpenHAB and to ArduPilot

All of these are developed in such a way that they can be run
separately from each other. This allows for maximum flexiblity on the
side of Green Marine Concepts.

Besides those mentioned there are a few other smaller features which
are shared throughout the code base. You can think of a logger,
configuration file, utility code, dealing with OpenStreetMap, etc.

The Qt application makes use of the Model-View-Controller
architecture. In this case the view is constructed using the
definitions given in the QML file and is controlled using the embedded
JavaScript engine provided by Qt. Controlling is done using the code
defined throughout the code base. Glue for the model can be found in
the `qt_classes.py` file which defines Python classes which are
accessible to Qt.
