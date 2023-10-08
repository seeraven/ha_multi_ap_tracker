"""
Fritz!Box interface of ha_multi_ap_tracker.

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
from dataclasses import dataclass
from typing import Dict

from fritzconnection.lib.fritzhosts import FritzHosts

from .config import Config

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
@dataclass
class Device:
    """A device identified by the DeviceMonitor."""

    # pylint: disable=invalid-name
    mac: str = ""
    ip: str = ""
    name: str = ""
    interface_type: str = ""
    connected_to: str = ""
    status: bool = False


# pylint: disable=too-few-public-methods
class DeviceMonitor:
    """Device status retriever."""

    def __init__(self, config: Config) -> None:
        """Initialize this object."""
        self._fritz_hosts = [
            (
                "Fritz!Box",
                FritzHosts(
                    address=config.fritzbox.address, user=config.fritzbox.username, password=config.fritzbox.password
                ),
            )
        ]
        for repeater_config in config.repeater:
            self._fritz_hosts.append(
                (
                    f"Repeater {repeater_config.address}",
                    FritzHosts(
                        address=repeater_config.address,
                        user=repeater_config.username,
                        password=repeater_config.password,
                    ),
                )
            )

    def get_current_status(self) -> Dict[str, Device]:
        """Query all devices and create a combined list of host information."""
        device_names: Dict[str, str] = {}
        device_states: Dict[str, Device] = {}
        for router_name, fritz_host in self._fritz_hosts:
            LOGGER.debug("Gather hosts information from %s.", router_name)
            hosts = fritz_host.get_hosts_info()
            for host in hosts:
                # Update the mac to name dict to choose the best name in the end
                mac = host["mac"]
                if mac:
                    name = host["name"]
                    if mac not in device_names:
                        device_names[mac] = name
                    elif not name.startswith("PC-"):
                        if device_names[mac].startswith("PC-"):
                            device_names[mac] = name
                        elif len(name) > len(device_names[mac]):
                            device_names[mac] = name
                else:
                    continue

                # Add a fully identified host (this has normally a status True)
                if host["ip"] and host["interface_type"]:
                    device_states[mac] = Device(
                        mac=mac,
                        ip=host["ip"],
                        interface_type=host["interface_type"],
                        connected_to=router_name,
                        status=host["status"],
                    )
                # ... and add not fully identified hosts to allow drop detection
                elif mac not in device_states:
                    device_states[mac] = Device(
                        mac=mac, interface_type=host["interface_type"], connected_to=router_name
                    )

        for mac, state in device_states.items():
            if mac in device_names:
                state.name = device_names[mac]
        return device_states


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
