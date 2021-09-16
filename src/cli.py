"""Defines a class for creating a CLI when Qt is not used."""
from typing import List

import config

# Compatibility for Windows plebs
try:
    import readline
except ImportError:
    import pyreadline as readline  # type: ignore


class BufferAwareCompleter:
    """History which autocompletes the configuration settings."""
    def __init__(self, options: dict):
        """Initialise autocompleter class.

        Args:
            - options: Defines what options each supported command supports
        """
        self.options = options
        self.current_candidates: List[str] = []

    def complete(self, _, state):
        """Finds the autocompleted keys."""
        response = None
        if state == 0:
            # This is the first time for this text,
            # so build a match list.

            origline = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()
            being_completed = origline[begin:end]
            words = origline.split()

            if words[0] == "config" and words[1] in self.options['config']:
                conf = config.ConfigFile()
                sections = list(conf._config_var)

                if len(words) == 3 and words[2].upper() in sections:
                    values = list(conf._config_var[words[2]].keys())
                    self.current_candidates = values
                elif len(words) >= 2 and len(words) <= 3:
                    self.current_candidates = sections
                else:
                    self.current_candidates = []
            elif words[0] == "config":
                self.current_candidates = ["get", "set"]
            elif not words:
                self.current_candidates = sorted(self.options.keys())
            else:
                try:
                    if begin == 0:
                        # first word
                        candidates = self.options.keys()
                    else:
                        # later word
                        first = words[0]
                        candidates = self.options[first]

                    if being_completed:
                        # match options with portion of input
                        # being completed
                        self.current_candidates = [
                            w for w in candidates
                            if w.startswith(being_completed)
                        ]
                    else:
                        # matching empty string,
                        # use all candidates
                        self.current_candidates = candidates

                except (KeyError, IndexError):
                    self.current_candidates = []

        try:
            response = self.current_candidates[state]
        except IndexError:
            response = None
        return response
