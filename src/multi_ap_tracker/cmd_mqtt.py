"""
mqtt subcommand of ha_multi_ap_tracker.

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

from .config import Config
from .mqtt_ifc import MqttInterface

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger(__name__)
DESCRIPTION = """
'mqtt' command
==============

Manually send MQTT messages to create, update and delete a device tracker.
"""

DESCRIPTION_CREATE = """
'mqtt create' command
=====================

Send the MQTT configuration message to create a new device tracker in home-assistant.
"""

DESCRIPTION_UPDATE = """
'mqtt update' command
=====================

Send the MQTT state message of a device tracker in home-assistant.
"""

DESCRIPTION_DELETE = """
'mqtt delete' command
=====================

Send the MQTT configuration message to delete a device tracker in home-assistant.
"""

DESCRIPTION_LISTEN = """
'mqtt listen' command
=====================

Starts the MQTT interface and monitors changes of the homeassistant/status topic.
"""


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------
def create_tracker(args) -> None:
    """Send the MQTT configuration message to create a new device tracker."""
    config = Config()
    config.load(args.config_file)
    mqtt = MqttInterface(config)
    mqtt.create_device_tracker(args.hostname)
    mqtt.close()


def update_tracker(args) -> None:
    """Send the MQTT state message of a device tracker."""
    config = Config()
    config.load(args.config_file)
    mqtt = MqttInterface(config)
    mqtt.update_device_tracker(args.hostname, args.state)
    mqtt.close()


def delete_tracker(args) -> None:
    """Send the MQTT configuration message to delete a device tracker."""
    config = Config()
    config.load(args.config_file)
    mqtt = MqttInterface(config)
    mqtt.delete_device_tracker(args.hostname)
    mqtt.close()


def listen(args) -> None:
    """Start the MQTT interface and monitor changes of the homeassistant/status topic."""
    config = Config()
    config.load(args.config_file)
    mqtt = MqttInterface(config)
    last_state = mqtt.ha_state
    LOGGER.info("Initial home-assistant state: %s", last_state)
    LOGGER.debug("Waiting for changes...")
    while True:
        curr_state = mqtt.ha_state
        if curr_state != last_state:
            LOGGER.info("home-assistant state changed to: %s", curr_state)
            last_state = curr_state
        time.sleep(10)


# -----------------------------------------------------------------------------
# Parsers
# -----------------------------------------------------------------------------
def add_mqtt_parser(subparsers) -> None:
    """Add the parser for the 'mqtt' subcommand."""
    mqtt_parser = subparsers.add_parser("mqtt", description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    mqtt_subparsers = mqtt_parser.add_subparsers(required=True)

    create_mqtt_parser = mqtt_subparsers.add_parser(
        "create", description=DESCRIPTION_CREATE, formatter_class=argparse.RawTextHelpFormatter
    )
    create_mqtt_parser.add_argument("hostname", type=str, help="The hostname to track.")
    create_mqtt_parser.set_defaults(func=create_tracker)

    update_mqtt_parser = mqtt_subparsers.add_parser(
        "update", description=DESCRIPTION_UPDATE, formatter_class=argparse.RawTextHelpFormatter
    )
    update_mqtt_parser.add_argument("hostname", type=str, help="The hostname.")
    update_mqtt_parser.add_argument(
        "state", choices=["home", "not_home"], help="The state. Valid choices are %(choices)s."
    )
    update_mqtt_parser.set_defaults(func=update_tracker)

    delete_mqtt_parser = mqtt_subparsers.add_parser(
        "delete", description=DESCRIPTION_DELETE, formatter_class=argparse.RawTextHelpFormatter
    )
    delete_mqtt_parser.add_argument("hostname", type=str, help="The hostname of the device tracker to delete.")
    delete_mqtt_parser.set_defaults(func=delete_tracker)

    listen_mqtt_parser = mqtt_subparsers.add_parser(
        "listen", description=DESCRIPTION_LISTEN, formatter_class=argparse.RawTextHelpFormatter
    )
    listen_mqtt_parser.set_defaults(func=listen)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
