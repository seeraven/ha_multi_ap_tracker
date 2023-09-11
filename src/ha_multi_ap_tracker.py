#!/usr/bin/env python3
"""
Home-Assistant Device Tracker using a Non-Mesh Setup of FritzBox and FritzRepeater.

(c) 2023 by Clemens Rabe <clemens.rabe@mercedes-benz.com>
"""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import argparse
import logging

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()
DESCRIPTION = """
Device Tracker for Non-Mesh Setups of FritzBox and FritzRepeater
================================================================


"""


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def get_parser():
    """Get the argument parser."""
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Be verbose by setting the logging level to DEBUG."
    )
    return parser


# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------
def ha_multi_ap_tracker() -> None:
    """The main function."""
    parser = get_parser()
    args = parser.parse_args()

    log_format = "%(asctime)s [%(levelname)s]: %(message)s"
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(format=log_format, level=log_level)


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    ha_multi_ap_tracker()


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
