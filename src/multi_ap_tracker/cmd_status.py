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

from tabulate import tabulate

from .config import Config
from .fritz_ifc import DeviceMonitor

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()
DESCRIPTION = """
'status' command
================

Show the current status of the devices by connecting to the Fritz!Box and all
repeaters.
"""

DESCRIPTION_SHOW = """
'status show' command
=====================

Show the current status of all found devices.
"""


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------
def show_status(args) -> None:
    """Show the current status of all found devices."""
    config = Config()
    config.load(args.config_file)
    monitor = DeviceMonitor(config)
    device_states = monitor.get_current_status()
    table_headers = ["Name", "MAC", "IP", "Interface", "Connected To", "Status"]
    table_data = [
        [state.name, state.mac, state.ip, state.interface_type, state.connected_to, state.status]
        for state in device_states.values()
    ]
    table_data.sort(key=lambda row: row[0])
    print(tabulate(table_data, headers=table_headers, tablefmt="rounded_outline"))


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


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
