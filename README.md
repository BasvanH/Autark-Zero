# Context-Aware Mission Planner
This program is meant to interact with the OpenHAB interface and ArduPilot autopilot software on-board the [Autark Zero autonomous sailing yacht](https://greenmarineconcepts.com). The concrete functionality is composed of three parts.

* Constructing a geofence comprising surrounding waterbodies using data from OpenStreetMap and relaying that data as a complete geofence to ArduPilot using the MAVLink protocol
* Receiving telemetry data from ArduPilot via MAVLink and publishing it on MQTT with the intention of relaying the data to OpenHAB
* Receiving command data about the desired destination from OpenHAB via MQTT and relaying a path computed using an environment-aware pathfinding algorithm to ArduPilot over MAVLink

Additionally, a visual debug interface is made available to test out the geofence and pathfinding functionalities. It is built using the QML functionality of the Qt framework.

A config file is also provided to tune various parameters and most of these values can also be dynamically adjusted in the visual interface via a pull-out menu accessed from the left side of the interface.

## How to Install
### Python Environment
```sh
python -m venv --prompt autark .env
source .env/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Eurostat/Searoute Submodule
```sh
git submodule update --init
cd searoute/releases/searoute-2.1/
./searoute.sh (Linux) OR ./searoute.bat (Windows)
```

### ArduPilot SITL Simulator
In order to make use of functionality that interfaces with ArduPilot, the program must be connected to a running instance of ArduPilot.
For testing purposes, this has been done using the SITL Simulator, for which installation instructions can be found in [the official ArduPilot documentation](https://ardupilot.org/dev/docs/SITL-setup-landingpage.html).

For testing, the following command was used to launch the simulation (assuming a terminal launched from the root directory of a fully set-up clone of the ArduPilot repository).
```sh
cd Rover/
../Tools/autotest/sim_vehicle.py -v Rover -f sailboat -L Haarlem --console --map
```

Using this requires adding the following line to `Tools/autotest/locations.txt` in order to register the utilised test location
```
Haarlem=52.40359289862932,4.662117677145794,0,0
```

### MQTT
MQTT is heavily utilised and as such a broker must be set up and its address provided in the configuration file. Simply replace the value set for `broker` under `MQTT_CONFIG` to the address of your broker. Instructions for setting up a broker can be found online and a list of useful resources can be found [here](https://github.com/hobbyquaker/awesome-mqtt#broker).

## How to Run
The program supports both command-line arguments and provides a CLI when the visual debug portion is not being used. The main entry point is `src/main.py` and is accessed as outlined in "How to Install".

### Arguments
* `--with-commands`: Enables command data relay
* `--with-geofence`: Enables geofence generation and transmission (note that this will most likely require `--with-telemetry` enabled as the extracted data is used to generate the geofence - this is not done by default for the sake of modularity)
* `--with-telemetry`: Enables ArduPilot telemetry data extraction and transmission
* `--with-qt`: Launches the program with a visual map-based debugging view
* `-a` or `--all`: Enables all previously listed functionality

Example for launching with geofence and telemetry functionalities from a terminal in the root directory (assuming install instructions have been followed)
```sh
python src/main.py --with-geofence --with-telemetry
```

### CLI Functionality
If not launched with the visual debug view (i.e: not with `-a`, `--all`, or `with-qt`) a command-line interface is provided for interacting with the program and enabling its functions, similarly to the command-line arguments.

The commands are as follows:
* `exit`: Terminates the program
* `qt`: Launches the visual debug application
* `commander`: Enables command data relay
* `telemetry`: Enables ArduPilot telemetry data extraction and transmission
* `geofence`: Enables geofence generation and transmission (same conditions apply as when using `--with-geofence`, see the "Arguments" sub-section)
* `config get [CONFIG_FILE_SECTION_NAME]`: Show the value of all parameters in the given section (see the Python docs' [config file structure description](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure))
* `config get [CONFIG_FILE_SECTION_NAME] [CONFIG_FILE_ITEM_NAME]`: Show the value of the parameter indicated by the given data (see the Python docs' [config file structure description](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure))
* `config set [CONFIG_FILE_SECTION_NAME] [CONFIG_FILE_ITEM_NAME] [NEW_VALUE]`: Set the value of the parameter indicated by the given data to the provided value (see the Python docs' [config file structure description](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure))

## Documentation
Full documentation is provided using the [Sphinx](https://www.sphinx-doc.org/en/master/index.html) tool and can be generated using [`sphinx-build`](https://www.sphinx-doc.org/en/master/man/sphinx-build.html). The tool must be installed by following the [installation guide](https://www.sphinx-doc.org/en/master/usage/installation.html).

As an example, documentation can be generated in the form of HTML documents using the following command.
```sh
sphinx-build -b html docs build
```
