Usage and Deployment
=======================
Structurally this program is in usage slightly different than those of
most other programs. This is because configurability and extensiblity
are at the very core of the program, which can be done using the
command-line interface or flags. Our reason for implementing it as
such is simply because, at the moment, is hard to tell exactly when or
what Green Marine Concepts actually want or need. Development of the
software side of the Autark Zero is not far along enough to really
make decisions like this.


Options
------------------------

| `--with-commands`: Allow for the communcation from OpenHAB.
| `--with-telemetry`: Start sending telemetry to OpenHAB from ArduPilot
| `--with-qt`: Run the Qt debugging application
| `--with-geofence`: Create Geofences while the boat is sailing
| `--all (-a)` : Start the program with all the options

Command-Line Interface
-----------------------
Whenever you are running the program without the Qt debugging view, it
will start it in a headless mode which gives you access to a
command-line interface. The idea is that this program allows for
interactive tuning of the various parameters and a dynamic way start
services when they are needed.

The following options are supported:
| `exit`: Close the program
| `qt`: Start the Qt debugging view
| `telemetry`: Continously send telemetry data from ArduPilot to OpenHAB
| `commander`: Parse messages from openHAB
| `geofence`: Start creating geofences around the boat
| `config get [section]`: Get all the values in a section
| `config get [section] [value]`: Get a value
| `config get [section] [name] [value]`: set a value

Requirements
-------------------------

Hardware & Software
######################
Running this software can be done on any system capable of running a generic
GNU/Linux system. Software requirements are just X11 or Wayland,
optionally Qt 5 and a network stack

Server Requirements
#####################
Running the software requires running a MQTT Broker and optionally an
`OpenHAB <https://www.openhab.org/>`_ instance. For the MQTT Broker it suffices to download the
`Mosquitto <https://mosquitto.org/>`_ broker from the Eclipse project. You can start it locally
using `systemctl start --user mosquitto`.

Deploying the software
#######################
The software can be started manually using the two methods outlined
above, however when running on a production it is useful to run it
headless in the background. In our opinion the best way to do this is
to utilise the `systemd <https://www.freedesktop.org/wiki/Software/systemd/>`_ service system. To do so add the following file
to `$HOME/.config/systemd/user/ca-recommendation-engine.unit`

.. code-block::

   [Unit]
   Description=Context-Aware Recommendation Engine

   [Service]
   ExecStart=/usr/bin/bash -c 'cd $HOME/autark-server; source
   .env/bin/activate; python src/main.py'

   [Install]
   WantedBy=default.target

Debugging without a boat
##########################
Debugging without a boat requires that you run an instance of
the `ArduPilot SITL <https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html>`_, otherwise the program is unable to start either
the commander or the telemetry.
