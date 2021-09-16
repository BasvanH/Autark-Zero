Configuration
===================
In order to configure the program you make use of the provided
configuration file. At the moment, the configuration file needs to be
in project root. Support for the `XDG Desktop Base Dir Standard
<https://specifications.freedesktop.org/basedir-spec/latest/ar01s03.html>`_,
which deals with directories used on a typical GNU/Linux system,
should be added in the future.

Explanation of the Variables
----------------------------
As of June 2021 the following variables are supported:

* *broker*: The URI to the MQTT broker.
* *client_name*: Name used for the program to connect to MQTT.
* *MQTT_TOPICS*: Names of various topics used throughout the project.
* *get_home_attempt_limit*: Amount of times the program will
  communicate with ArduPilot to get the home location before it gives
  up.
* *latitude_delta*: Latitude distance that the bounding box is drawn
  around the yacht
* *longitude_delta*: Longitude distance that the bounding box is
  drawn around the yacht
* *minimum_refresh_distance*: Distance that the boat has to move before
  a new geofence is generated in meters.
* *refresh_delay*: Number of seconds between attempting to generate
  another geofence.
* *simplification_tolerance_distance*: Maximum distance from the
  original polugonm for each distance.
* *distance_until_heading_straight*: Unused
* *limit_ardupilot_waypoints*: Amount of points the mission planner is
  allowed to generate at once.
* *resolution_ocean_trip*: Precision that the course over the ocean is
  planned.
* *time_offset_collision*: Indicates the time interval which is used
  to determine whether the boat crashed into an object.
* *collision_distance_threshold*: Maximum amount that the object is
  allowed to before it is considered a crash.
* *direction_change_angle*: Angle at which the boat changes it course
  each time that it tacks.
* *obstacle_line_project_distance*: Defines the length of the course
  of each object in meters.
* *obstacle_origin_reverse_epsilon*: Figuring out whether objects
  crash is done by intersecting their courses. Due to floating point
  errors this is not always accurate so one of the lines needs to
  moved slightly to the back. This defines the amount it is moved back
  in meters.


Example file
----------------------------

.. code-block:: ini

   [MQTT_CONFIG]
   broker = autarkzero.xyz
   client_name = anti-death_machine

   [MQTT_TOPICS]
   compass = sensors/compass
   destination = destination
   gps = sensors/gps
   openhab_commands = commands
   speed = sensors/speed
   windmeter = sensors/windmeter

   [MAVLINK]
   get_home_attempt_limit = 5

   [GEOFENCE]
   latitude_delta = 0.01
   longitude_delta = 0.01
   simplification_tolerance_distance = 3
   minimum_refresh_distance = 25
   refresh_delay = 10


   [MISSION_PLANNER]
   distance_until_heading_straight = 300
   limit_ardupilot_waypoints = 15
   minimum_distance_waypoint = 30
   resolution_ocean_trip = 5
   time_offset_collision = 40

   [PATH_FINDER]
   collision_distance_threshold = 100
   direction_change_angle = 10
   obstacle_line_projection_distance = 1000
   obstacle_origin_reverse_epsilon = 1
