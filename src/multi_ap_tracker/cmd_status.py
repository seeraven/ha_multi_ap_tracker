"""
status subcommand of ha_multi_ap_tracker.

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
import argparse
import logging
import time

from tabulate import tabulate

from .config import Config
from .fritz_ifc import DeviceMonitor
from .state import State

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger(__name__)
DESCRIPTION = """
'status' command
================

Show the current status of the devices by connecting to the Fritz!Box and all
repeaters.
"""

DESCRIPTION_SHOW = """
'status show' command
=====================

Show the current status of all found devices. It shows the aggregated data for
each device identified by its MAC address.
"""

DESCRIPTION_MONITOR = """
'status monitor' command
========================

Show the current status of all found hosts and print detected changes
at a pre-defined interval specified by the `--interval` option (default 300s).
"""


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------
def show_status(args) -> None:
    """Show the current status of all found devices."""
    config = Config()
    config.load(args.config_file)
    state = State(args.state_file)
    monitor = DeviceMonitor(config, state)
    device_states = monitor.get_device_stati()
    table_headers = ["Name", "MAC", "IP", "Interface", "Connected To", "Status", "Seen by"]
    table_data = [
        [
            state.name,
            state.mac,
            state.ip,
            state.interface_type,
            state.connected_to,
            state.status,
            "\n".join(state.seen_by),
        ]
        for state in device_states.values()
    ]
    table_data.sort(key=lambda row: row[0])  # type: ignore
    print(tabulate(table_data, headers=table_headers, tablefmt="fancy_grid"))


def monitor_status(args) -> None:
    """Show the current status of all found devices followed by a monitoring mode."""
    config = Config()
    config.load(args.config_file)
    state = State(args.state_file)
    monitor = DeviceMonitor(config, state)

    host_states = monitor.get_host_stati()
    last_online_hosts = {hostname: device for hostname, device in host_states.items() if device.status}
    last_online_hostnames = set(last_online_hosts.keys())
    table_headers = ["Name", "MAC", "IP", "Interface", "Connected To"]
    table_data = [
        [state.name, state.mac, state.ip, state.interface_type, state.connected_to]
        for state in last_online_hosts.values()
    ]
    table_data.sort(key=lambda row: row[0])
    print("-" * 80)
    print("  INITIAL STATE")
    print("-" * 80)
    print(tabulate(table_data, headers=table_headers, tablefmt="rounded_outline"))

    while True:
        LOGGER.debug("Sleeping for %d seconds.", args.interval)
        time.sleep(args.interval)

        host_states = monitor.get_host_stati()
        curr_online_hosts = {hostname: device for hostname, device in host_states.items() if device.status}
        curr_online_hostnames = set(curr_online_hosts.keys())

        for new_online_hostname in curr_online_hostnames - last_online_hostnames:
            device = curr_online_hosts[new_online_hostname]
            LOGGER.info(
                "New online device found: Name=%s, MAC=%s, IP=%s, Interface=%s, Connected To=%s",
                device.name,
                device.mac,
                device.ip,
                device.interface_type,
                device.connected_to,
            )

        for offline_hostname in last_online_hostnames - curr_online_hostnames:
            device = last_online_hosts[offline_hostname]
            LOGGER.info(
                "Device gone offline: Name=%s, MAC=%s, IP=%s, Interface=%s, Connected To=%s",
                device.name,
                device.mac,
                device.ip,
                device.interface_type,
                device.connected_to,
            )

        last_online_hosts = curr_online_hosts
        last_online_hostnames = curr_online_hostnames


# -----------------------------------------------------------------------------
# Parsers
# -----------------------------------------------------------------------------
def add_status_parser(subparsers) -> None:
    """Add the parser for the 'status' subcommand."""
    status_parser = subparsers.add_parser(
        "status", description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )
    status_subparsers = status_parser.add_subparsers(required=True)

    show_status_parser = status_subparsers.add_parser(
        "show", description=DESCRIPTION_SHOW, formatter_class=argparse.RawTextHelpFormatter
    )
    show_status_parser.set_defaults(func=show_status)

    monitor_status_parser = status_subparsers.add_parser(
        "monitor", description=DESCRIPTION_MONITOR, formatter_class=argparse.RawTextHelpFormatter
    )
    monitor_status_parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=300,
        help="Time between two status retrievals in seconds. Default: %(default)s",
    )
    monitor_status_parser.set_defaults(func=monitor_status)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
