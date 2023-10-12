"""
Persistent State Handling of the ha_multi_ap_tracker.

Copyright:
    2023 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of powercounter (https://github.com/seeraven/ha_multi_ap_tracker)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import logging
from pathlib import Path
from typing import Any, Dict

import yaml

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
class State:
    """Persistent state.

    This object contains the member dict `data` which contains all the state
    information to save. Upon creation of this object, the state is automatically
    loaded into memory. Users of this state must call the `save()` method to
    ensure the data survives crashes and restarts of the application.
    """

    def __init__(self, state_filepath: Path) -> None:
        """Create the persistent state object."""
        LOGGER.debug("Initialize persistent state using yaml file %s", state_filepath)
        self._filepath = state_filepath
        self.data: Dict[str, Any] = {}
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def load(self) -> None:
        """Load the persistent state from disc."""
        self.data = {}
        if self._filepath.exists():
            LOGGER.debug("Loading persistent state from yaml file %s", self._filepath)
            with open(self._filepath, "r", encoding="utf-8") as file_handle:
                self.data = yaml.safe_load(file_handle)
        else:
            LOGGER.debug("No persistent state found. Using empty state.")

    def save(self) -> None:
        """Save the persistent state to disc."""
        LOGGER.debug("Saving persistent state to yaml file %s", self._filepath)
        with open(self._filepath, "w", encoding="utf-8") as file_handle:
            yaml.dump(self.data, file_handle)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
