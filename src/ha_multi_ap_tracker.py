#!/usr/bin/env python3
"""
Home-Assistant Device Tracker using a Non-Mesh Setup of FritzBox and FritzRepeater.

(c) 2023 by Clemens Rabe <clemens.rabe@mercedes-benz.com>
"""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from multi_ap_tracker.command import ha_multi_ap_tracker

# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    ha_multi_ap_tracker()


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
