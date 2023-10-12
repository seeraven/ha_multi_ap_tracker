"""
MQTT interface of ha_multi_ap_tracker.

Copyright:
    2023 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of powercounter (https://github.com/seeraven/ha_multi_ap_tracker)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""


import json

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import logging
import time
from hashlib import md5
from typing import Any, Callable, Dict, Optional

import paho.mqtt.client as mqtt

from .config import Config

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
class MqttInterface:
    """The interface to the MQTT broker."""

    def __init__(self, config: Config, ha_state_callback: Optional[Callable] = None) -> None:
        """Initialize this object."""
        LOGGER.debug("Create MQTT client.")
        self._mqtt_config = config.mqtt
        self.ha_state = "online"
        self._ha_state_callback: Optional[Callable] = ha_state_callback
        self._client = mqtt.Client("ha_multi_ap_tracker")
        self._client.username_pw_set(config.mqtt.username, config.mqtt.password)
        self._client.on_connect = self._on_connect
        if self._mqtt_config.ha_state_topic:
            self._client.message_callback_add(self._mqtt_config.ha_state_topic, self._on_ha_status_message)
        self._client.connect_async(config.mqtt.address, config.mqtt.port)
        self._client.loop_start()
        time.sleep(1)

    def close(self) -> None:
        """Close the connection to the broker."""
        LOGGER.debug("Closing MQTT connection.")
        self._client.loop_stop()
        self._client.disconnect()

    def _on_connect(self, _client, _userdata, _flags, _rc):
        LOGGER.debug("MQTT Client connected to broker.")
        if self._mqtt_config.ha_state_topic:
            LOGGER.debug("Subscribing to topic %s.", self._mqtt_config.ha_state_topic)
            res, _ = self._client.subscribe(self._mqtt_config.ha_state_topic, 2)
            if res == mqtt.MQTT_ERR_NO_CONN:
                LOGGER.error("Subscription failed due to no connection to the broker.")
            elif res != mqtt.MQTT_ERR_SUCCESS:
                LOGGER.error("Subscription failed due to unknown error.")
            else:
                LOGGER.debug("Subscription succeeded.")

    def _on_ha_status_message(self, _client, _userdata, message) -> None:
        """Callback called when the home-assistant state changed."""
        LOGGER.debug("Received message %s on home-assistant state topic %s.", message.payload.decode(), message.topic)
        self.ha_state = message.payload.decode()
        if self._ha_state_callback:
            self._ha_state_callback(message.payload.decode() == "online")

    def _get_object_id(self, hostname: str) -> str:
        """Get the object ID for the given hostname."""
        return md5(hostname.encode("utf-8")).hexdigest()

    def _get_config_topic(self, object_id: str) -> str:
        """Get the topic for configuration messages."""
        topic = f"{self._mqtt_config.discovery_prefix}/device_tracker/"
        if self._mqtt_config.node_id:
            topic += f"{self._mqtt_config.node_id}/"
        topic += f"{object_id}/config"
        return topic

    def _get_state_topic(self, object_id: str) -> str:
        """Get the topic for state messages."""
        topic = ""
        if self._mqtt_config.node_id:
            topic = f"{self._mqtt_config.node_id}/"
        topic += f"{object_id}/state"
        return topic

    def _get_attributes_topic(self, object_id: str) -> str:
        """Get the topic for attributes messages."""
        topic = ""
        if self._mqtt_config.node_id:
            topic = f"{self._mqtt_config.node_id}/"
        topic += f"{object_id}/attributes"
        return topic

    def create_device_tracker(self, hostname: str) -> None:
        """Publish a configuration message to create the device tracker."""
        object_id = self._get_object_id(hostname)
        topic = self._get_config_topic(object_id)
        data = {
            "state_topic": self._get_state_topic(object_id),
            "json_attributes_topic": self._get_attributes_topic(object_id),
            "name": f"{self._mqtt_config.name_prefix}{hostname}",
            "unique_id": object_id,
            "payload_home": "home",
            "payload_not_home": "not_home",
        }
        LOGGER.debug("Create new device tracker by sending MQTT configuration message on topic %s.", topic)
        ret = self._client.publish(topic, json.dumps(data))
        if ret.rc == mqtt.MQTT_ERR_NO_CONN:
            LOGGER.error("Mqtt Client is not connected!")
        elif ret.rc == mqtt.MQTT_ERR_QUEUE_SIZE:
            LOGGER.error("Mqtt Client queue size exceeded!")

    def update_device_tracker(self, hostname: str, state: str) -> None:
        """Publish a state message of the device tracker."""
        object_id = self._get_object_id(hostname)
        topic = self._get_state_topic(object_id)
        LOGGER.debug("Send device tracker state %s on topic %s.", state, topic)
        ret = self._client.publish(topic, state)
        if ret.rc == mqtt.MQTT_ERR_NO_CONN:
            LOGGER.error("Mqtt Client is not connected!")
        elif ret.rc == mqtt.MQTT_ERR_QUEUE_SIZE:
            LOGGER.error("Mqtt Client queue size exceeded!")

    def update_device_tracker_attributes(self, hostname: str, attributes: Dict[str, Any]) -> None:
        """Publish an attributes message of the device tracker."""
        object_id = self._get_object_id(hostname)
        topic = self._get_attributes_topic(object_id)
        LOGGER.debug("Send device tracker attributes for host %s on topic %s.", hostname, topic)
        ret = self._client.publish(topic, json.dumps(attributes))
        if ret.rc == mqtt.MQTT_ERR_NO_CONN:
            LOGGER.error("Mqtt Client is not connected!")
        elif ret.rc == mqtt.MQTT_ERR_QUEUE_SIZE:
            LOGGER.error("Mqtt Client queue size exceeded!")

    def delete_device_tracker(self, hostname: str) -> None:
        """Publish a configuration message to delete the device tracker."""
        object_id = self._get_object_id(hostname)
        topic = self._get_config_topic(object_id)
        LOGGER.debug("Delete device tracker by sending MQTT configuration message on topic %s.", topic)
        ret = self._client.publish(topic, "")
        if ret.rc == mqtt.MQTT_ERR_NO_CONN:
            LOGGER.error("Mqtt Client is not connected!")
        elif ret.rc == mqtt.MQTT_ERR_QUEUE_SIZE:
            LOGGER.error("Mqtt Client queue size exceeded!")
