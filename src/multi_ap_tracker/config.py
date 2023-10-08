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
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import yaml

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# -----------------------------------------------------------------------------
# Configuration Objects
# -----------------------------------------------------------------------------
@dataclass
class Fritzbox:
    """Configuration of the connection to the Fritz!Box."""

    address: str = "fritz.box"
    username: str = "admin"
    password: str = "secret"

    def __str__(self) -> str:
        """Return the string representation of this object."""
        retval = "  FritzBox Connection:\n"
        retval += f"    Address:  {self.address}\n"
        retval += f"    Username: {self.username}\n"
        retval += f"    Password: {self.password}\n"
        return retval


@dataclass
class Mqtt:
    """Configuration of the connection to the MQTT broker."""

    address: str = "mqtt.local.net"
    port: int = 1883
    username: str = "mqtt"
    password: str = "secret"

    def __str__(self) -> str:
        """Return the string representation of this object."""
        retval = "  MQTT:\n"
        retval += f"    Address:  {self.address}\n"
        retval += f"    Port:     {self.port}\n"
        retval += f"    Username: {self.username}\n"
        retval += f"    Password: {self.password}\n"
        return retval


@dataclass
class Repeater:
    """Configuration of the connection to a Fritz!Repeater."""

    address: str = "fritz.repeater"
    username: str = "admin"
    password: str = "secret"

    def __str__(self) -> str:
        """Return the string representation of this object."""
        retval = "  Repeater Connection:\n"
        retval += f"    Address:  {self.address}\n"
        retval += f"    Username: {self.username}\n"
        retval += f"    Password: {self.password}\n"
        return retval


@dataclass
class Config:
    """Configuration of this application."""

    mqtt: Mqtt = Mqtt()
    fritzbox: Fritzbox = Fritzbox()
    repeater: list[Repeater] = field(default_factory=lambda: [Repeater()])

    def load(self, config_file: Optional[Path]) -> None:
        """Load the configuration from a yaml file."""
        if config_file:
            LOGGER.debug("Loading configuration file %s.", config_file)
            with open(config_file, "r", encoding="utf-8") as file_handle:
                data = yaml.safe_load(file_handle)
            self.mqtt = Mqtt(**data["mqtt"])
            self.fritzbox = Fritzbox(**data["fritzbox"])
            self.repeater = [Repeater(**args) for args in data["repeater"]]

    def save(self, config_file: Path) -> None:
        """Save the configuration to a yaml file."""
        with open(config_file, "w", encoding="utf-8") as file_handle:
            yaml.dump(asdict(self), file_handle)

    def __str__(self) -> str:
        """Return the string representation of this object."""
        retval = "Configuration:\n"
        retval += str(self.mqtt) + "\n"
        retval += str(self.fritzbox) + "\n"
        for repeater in self.repeater:
            retval += str(repeater) + "\n"
        return retval


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
