"""This module defines path finding algorithms.

The ArduPilot's autopilot is unable to find a safe and good path. This
is down to limitations related to the memory on the ArduPilot's
memory. In practice it means that it cannot take the entirety of the
map and it's metadata in account. Which includes the geometry of where
it sails and the location of the water.

In this module you can find a basic abstract class which can be used as
an interface. It also contains a few implementations which can be
further expanded on where needed.
"""

__all__ = [
    "base_path", "boat", "mission_planner", "path_finder", "strategy",
    "visualizations"
]
