"""
Configuration Handling of the ha_multi_ap_tracker.

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
from pathlib import Path

import yaml

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "mqtt": {"username": "mqtt", "password": "secret", "host": "mqtt.local.net", "port": 1883},
    "fritzbox": {"address": "fritz.box", "username": "admin", "password": "secret"},
    "repeater": [{"address": "fritz.repeater", "username": "admin", "password": "secret"}],
}


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def load_config(config_file: Path):
    """Load the configuration."""
    with open(config_file, "r", encoding="utf-8") as file_handle:
        return yaml.safe_load(file_handle)


def save_config(config_file: Path, config) -> None:
    """Save a configuration."""
    with open(config_file, "w", encoding="utf-8") as file_handle:
        yaml.dump(config, file_handle)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
