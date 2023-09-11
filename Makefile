# ----------------------------------------------------------------------------
# Makefile for ha_multi_ap_tracker
#
# Copyright (c) 2023 by Clemens Rabe
# All rights reserved.
# This file is part of ha_multi_ap_tracker (https://github.com/seeraven/ha_multi_ap_tracker)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
#  SETTINGS
# ----------------------------------------------------------------------------
APP_NAME             := ha-multi-ap-tracker
APP_VERSION          := 0.0.1

ALL_TARGET           := check-style.venv
SCRIPT               := src/ha_multi_ap_tracker.py
UBUNTU_DIST_VERSIONS   := 20.04 22.04
ENABLE_WINDOWS_SUPPORT := 0


# ----------------------------------------------------------------------------
#  MAKE4PY INTEGRATION
# ----------------------------------------------------------------------------
include .make4py/make4py.mk


# ----------------------------------------------------------------------------
#  OWN TARGETS
# ----------------------------------------------------------------------------
.PHONY: precheck-releases

precheck-releases: check-style.all tests.all doc man


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
