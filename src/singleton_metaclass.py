"""This file defines a singleton meta-class for creating singletons.

Based off of this SO answer: https://stackoverflow.com/a/6798042/14247568
"""
from typing import Dict


class Singleton(type):
    """A simple Simpleton meta class.

    Example:
      class TestTon(metaclass=Singleton):
          def __init__(self):
              print("Starting..,")
    """

    _instances: Dict[type, type] = {}

    def __call__(cls, *args, **kwargs):
        """Magic function which always returns the same instance if called."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]
