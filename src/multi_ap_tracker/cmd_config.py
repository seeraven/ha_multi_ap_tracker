"""
config subcommand of ha_multi_ap_tracker.

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
from pathlib import Path

from .config import DEFAULT_CONFIG, save_config

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()
DESCRIPTION = """
'config' command
================

Manage the configuration of the ha_multi_ap_tracker.
"""

DESCRIPTION_GENERATE = """
'config generate' command
=========================

Generate an example configuration file.
"""


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------
def save_example_config(args) -> None:
    """Save an example configuration."""
    LOGGER.info("Saving example configuration to %s.", args.config_file)
    save_config(args.config_file, DEFAULT_CONFIG)


# -----------------------------------------------------------------------------
# Parsers
# -----------------------------------------------------------------------------
def add_config_parser(subparsers) -> None:
    """Add the parser for the 'config' subcommand."""
    config_parser = subparsers.add_parser(
        "config", description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )
    config_subparsers = config_parser.add_subparsers(required=True)

    generate_config_parser = config_subparsers.add_parser(
        "generate", description=DESCRIPTION_GENERATE, formatter_class=argparse.RawTextHelpFormatter
    )
    generate_config_parser.add_argument("config_file", help="Config file to create.", type=Path)
    generate_config_parser.set_defaults(func=save_example_config)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
