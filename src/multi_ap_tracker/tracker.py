"""
tracker component of ha_multi_ap_tracker.

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
import time
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List

from .config import Config
from .fritz_ifc import DeviceMonitor
from .mqtt_ifc import MqttInterface
from .state import State

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
# pylint: disable=too-many-instance-attributes
class Tracker:
    """The tracker responsible for identifying the devices and publishing their states."""

    def __init__(self, config: Config, state: State) -> None:
        """Initialize the tracker."""
        self._config = config
        self._state = state
        self._last_ha_online_state = True
        self._created_hostnames: List[str] = self._state.data.setdefault("CreatedHostnames", [])
        self._reconfigure_all = False
        self._lock = Lock()
        self._mqtt = MqttInterface(config, self.on_ha_state)
        self._monitor = DeviceMonitor(config, state)

    def close(self) -> None:
        """Close the connection."""
        self._mqtt.close()

    def on_ha_state(self, online: bool) -> None:
        """Callback when home-assistant goes offline or online."""
        if online and not self._last_ha_online_state:
            # When we went from offline to online, we need to reconfigure all device trackers
            with self._lock:
                self._reconfigure_all = True
        self._last_ha_online_state = online

    # pylint: disable=too-many-branches
    def track(self) -> None:
        """The tracking main loop."""
        last_states: Dict[str, bool] = {}

        while True:
            host_states = self._monitor.get_host_stati()

            hosts_to_create: List[str] = []
            hosts_to_delete: List[str] = []
            hosts_to_update: Dict[str, bool] = {}
            host_attributes_to_update: Dict[str, Dict[str, Any]] = {}
            current_time_str = datetime.now().astimezone().isoformat("T", "seconds")

            with self._lock:
                reconfigure_all = self._reconfigure_all
                self._reconfigure_all = False

            for hostname, device in host_states.items():
                if device.known:
                    if hostname not in self._created_hostnames or reconfigure_all:
                        hosts_to_create.append(hostname)
                        hosts_to_update[hostname] = device.status
                        last_states[hostname] = device.status
                        if hostname not in self._created_hostnames:
                            self._created_hostnames.append(hostname)

                    if (
                        hostname not in last_states
                        or device.status != last_states[hostname]
                        or self._config.tracker.send_state_always
                    ):
                        hosts_to_update[hostname] = device.status
                        last_states[hostname] = device.status

                    host_attributes_to_update[hostname] = {
                        "mac": device.mac,
                        "ip": device.ip,
                        "interface_type": device.interface_type,
                        "connected_to": device.connected_to,
                        "last_update": current_time_str,
                    }
                else:
                    if hostname in self._created_hostnames:
                        self._created_hostnames.remove(hostname)
                        del last_states[hostname]

            if hosts_to_create or hosts_to_delete:
                self._state.data["CreatedHostnames"] = self._created_hostnames
                self._state.save()

            if hosts_to_create:
                LOGGER.debug("Create device tracker(s) for %d hosts: %s", len(hosts_to_create), hosts_to_create)
                for hostname in hosts_to_create:
                    self._mqtt.create_device_tracker(hostname)
                time.sleep(10)  # To give home assistant time to create listeners on the state topic

            if hosts_to_update:
                LOGGER.debug("Update state of %d device tracker(s).", len(hosts_to_update))
                for hostname, status in hosts_to_update.items():
                    self._mqtt.update_device_tracker(hostname, "home" if status else "not_home")

            if host_attributes_to_update:
                LOGGER.debug("Update attributes of %d device tracker(s).", len(hosts_to_update))
                for hostname, attributes in host_attributes_to_update.items():
                    self._mqtt.update_device_tracker_attributes(hostname, attributes)

            if hosts_to_delete:
                LOGGER.debug("Delete device tracker(s) for %d hosts: %s", len(hosts_to_delete), hosts_to_delete)
                for hostname in hosts_to_delete:
                    self._mqtt.delete_device_tracker(hostname)

            LOGGER.debug("Sleeping for %d seconds.", self._config.tracker.time_interval)
            time.sleep(self._config.tracker.time_interval)

    def cleanup(self) -> None:
        """Clean all device trackers in home-assistant and remove the state."""
        LOGGER.info("Deleting %d device tracker(s).", len(self._created_hostnames))
        for hostname in self._created_hostnames:
            self._mqtt.delete_device_tracker(hostname)
        self._created_hostnames = []
        self._state.data["CreatedHostnames"] = self._created_hostnames
        self._state.save()


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
