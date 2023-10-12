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

from .config import Config

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger(__name__)
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

DESCRIPTION_SHOW = """
'config show' command
=====================

Print the configuration on stdout. The configuration file to load is
specified using the '--config-file' option.
"""


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------
def save_example_config(args) -> None:
    """Save an example configuration."""
    LOGGER.info("Saving example configuration to %s.", args.output_file)
    config = Config()
    config.save(args.output_file)


def show_config(args) -> None:
    """Show the configuration."""
    config = Config()
    config.load(args.config_file)
    print(config)


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
    generate_config_parser.add_argument("output_file", help="Config file to create.", type=Path)
    generate_config_parser.set_defaults(func=save_example_config)

    show_config_parser = config_subparsers.add_parser(
        "show", description=DESCRIPTION_SHOW, formatter_class=argparse.RawTextHelpFormatter
    )
    show_config_parser.set_defaults(func=show_config)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
