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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from fritzconnection.lib.fritzhosts import FritzHosts

from .config import Config
from .state import State

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger(__name__)


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
    seen_by: List[str] = field(default_factory=lambda: [])

    @property
    def known(self) -> bool:
        """Returns True if this device was actually seen by any router."""
        return len(self.seen_by) > 0


# pylint: disable=too-few-public-methods
class DeviceMonitor:
    """Device status retriever."""

    def __init__(self, config: Config, state: State) -> None:
        """Initialize this object."""
        self._state = state
        LOGGER.debug("Create connection to Fritz!Box at address %s.", config.fritzbox.address)
        self._fritz_hosts = [
            (
                "Fritz!Box",
                FritzHosts(
                    address=config.fritzbox.address, user=config.fritzbox.username, password=config.fritzbox.password
                ),
            )
        ]
        for repeater_config in config.repeater:
            LOGGER.debug("Create connection to repeater at address %s.", repeater_config.address)
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
        LOGGER.debug("All connections created.")

    def _aquire_host_infos(self) -> List[Tuple[str, List[Dict[str, Any]]]]:
        """Retrieve the current host infos from the Fritz!Box and all repeaters."""
        host_infos = []
        for router_name, fritz_host in self._fritz_hosts:
            LOGGER.debug("Gather hosts information from %s.", router_name)
            host_infos.append((router_name, fritz_host.get_hosts_info()))
        return host_infos

    def _get_mac_to_host_names(self, host_infos: List[Tuple[str, List[Dict[str, Any]]]]) -> Dict[str, str]:
        """Update the MAC to host name dictionary."""
        LOGGER.debug("Updating MAC to host names dictionary.")
        device_names: Dict[str, str] = self._state.data.setdefault("MacToDeviceNames", {})
        for _, hosts in host_infos:
            for host in hosts:
                mac = host["mac"]
                if mac:
                    name = host["name"]
                    if mac not in device_names:
                        device_names[mac] = name
                    elif not name.startswith("PC-"):
                        if device_names[mac].startswith("PC-"):
                            device_names[mac] = name
                        elif name[:15] != device_names[mac][:15]:
                            device_names[mac] = name
                        elif len(name) > len(device_names[mac]):
                            device_names[mac] = name
        return device_names

    def _get_mac_to_device_type(self, host_infos: List[Tuple[str, List[Dict[str, Any]]]]) -> Dict[str, str]:
        """Update the MAC to device type (802.11 or Ethernet) dictionary."""
        LOGGER.debug("Updating MAC to device type dictionary.")
        device_types: Dict[str, str] = self._state.data.setdefault("MacToDeviceType", {})
        for _, hosts in host_infos:
            for host in hosts:
                mac = host["mac"]
                if mac and host["ip"] and host["interface_type"]:
                    if mac not in device_types:
                        device_types[mac] = host["interface_type"]
                    # Prefer the 802.11 interface over Ethernet
                    if host["interface_type"] == "802.11" and device_types[mac] != host["interface_type"]:
                        device_types[mac] = host["interface_type"]
        return device_types

    def get_device_stati(self) -> Dict[str, Device]:
        """Query all devices and aggregate the information per device (identified by its MAC address)."""
        host_infos = self._aquire_host_infos()
        device_names = self._get_mac_to_host_names(host_infos)
        device_types = self._get_mac_to_device_type(host_infos)
        device_states: Dict[str, Device] = {}
        for router_name, hosts in host_infos:
            for host in hosts:
                mac = host["mac"]
                if not mac:
                    continue

                if mac not in device_states:
                    device_states[mac] = Device(mac=mac)

                device_states[mac].seen_by.append(router_name)

                # Add a fully identified host (this has normally a status True)
                if host["ip"] and host["interface_type"] and device_types[mac] == host["interface_type"]:
                    device_states[mac].ip = host["ip"]
                    device_states[mac].interface_type = host["interface_type"]
                    device_states[mac].connected_to = router_name
                    device_states[mac].status = host["status"]

        self._state.data["MacToDeviceNames"] = device_names
        self._state.data["MacToDeviceType"] = device_types
        self._state.save()

        for mac, state in device_states.items():
            if mac in device_names:
                state.name = device_names[mac]
            if mac in device_types and not state.interface_type:
                state.interface_type = device_types[mac]

        return device_states

    def get_host_stati(self) -> Dict[str, Device]:
        """Query all devices and create a per-host status information.

        Since we have to deal with MAC randomization we use the host name as the
        key for the returned dictionary. For every host seen by this application
        an entry is returned, even if it was not listed by the Fritz!Box or a
        repeater (in this case the `known` attribute of the Device object is False).
        """
        host_states: Dict[str, Device] = {}
        device_states = self.get_device_stati()

        for device in device_states.values():
            if device.name.startswith("PC-"):  # Ignore hosts named PC-*
                continue
            if device.name in host_states and host_states[device.name].status:  # Do not overwrite valid entries
                continue
            host_states[device.name] = device

        return host_states


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
