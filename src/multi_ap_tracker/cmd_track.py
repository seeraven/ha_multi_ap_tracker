"""
track subcommand of ha_multi_ap_tracker.

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

from .config import Config
from .state import State
from .tracker import Tracker

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger(__name__)
DESCRIPTION_TRACK = """
'track' command
===============

Perform the tracking of devices and publishing the state via MQTT.
"""
DESCRIPTION_CLEANUP = """
'cleanup' command
=================

Remove all tracked devices from home-assistant and the internal state.
"""


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------
def track(args) -> None:
    """Perform the tracking of the devices and publish the state via MQTT."""
    config = Config()
    config.load(args.config_file)
    state = State(args.state_file)
    tracker = Tracker(config, state)
    tracker.track()


def cleanup(args) -> None:
    """Remove all tracked devices in home-assistant and the internal state."""
    config = Config()
    config.load(args.config_file)
    state = State(args.state_file)
    tracker = Tracker(config, state)
    tracker.cleanup()


# -----------------------------------------------------------------------------
# Parsers
# -----------------------------------------------------------------------------
def add_track_parser(subparsers) -> None:
    """Add the parser for the 'track' subcommand."""
    track_parser = subparsers.add_parser(
        "track", description=DESCRIPTION_TRACK, formatter_class=argparse.RawTextHelpFormatter
    )
    track_parser.set_defaults(func=track)

    cleanup_parser = subparsers.add_parser(
        "cleanup", description=DESCRIPTION_CLEANUP, formatter_class=argparse.RawTextHelpFormatter
    )
    cleanup_parser.set_defaults(func=cleanup)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
