"""
command line interface of ha_multi_ap_tracker.

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

from .cmd_config import add_config_parser

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()
DESCRIPTION = """
Device Tracker for Non-Mesh Setups of FritzBox and FritzRepeater
================================================================


"""


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def get_parser():
    """Get the argument parser."""
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers()

    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Be verbose by setting the logging level to DEBUG."
    )

    add_config_parser(subparsers)

    return parser


def ha_multi_ap_tracker() -> None:
    """The main function."""
    parser = get_parser()
    args = parser.parse_args()

    log_format = "%(asctime)s [%(levelname)s]: %(message)s"
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(format=log_format, level=log_level)

    args.func(args)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
