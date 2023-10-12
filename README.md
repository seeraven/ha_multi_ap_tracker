# ha_multi_ap_tracker

This repository hosts the `ha_multi_ap_tracker`, a custom device tracker for
[home-assistant] to track WiFi devices over non-mesh configurations. It uses the
[fritzconnection] interface to query all devices and builds up a combined view
of the availability of the devices. The state of the individual devices is
communicated to [home-assistant] via [MQTT].


## Installation


### Setup of Home Assistant

For this tool to work you need to have the MQTT discovery enabled. For more
information on how to enable it look at the official
[MQTT - Configure MQTT options].


### Configuration

The configuration is stored in a yaml file. To start, generate an example
configuration file by calling

    ha_multi_ap_tracker config generate config.yml

The generated configuration file looks like this:
```
fritzbox:
  address: fritz.box
  password: secret
  username: admin
mqtt:
  address: mqtt.local.net
  discovery_prefix: homeassistant
  node_id: multi_ap_tracker
  name_prefix: mqtt_
  password: secret
  port: 1883
  username: mqtt
repeater:
- address: fritz.repeater
  password: secret
  username: admin
```

The entry `fritzbox` defines the connection to the main Fritz!Box. The
`username` can be retrieved as documented in the
[home-assistant AVM FRITZ!Box Tools].

The entry `mqtt` defines the connection to the [MQTT] broker. If you are using
the [home-assistant MQTT integration] you should set the `address` attribute to
the IP of your [home-assistant] instance and if you are using an authentication
you should adjust the `username` and `password` settings. The `discovery_prefix`
must be adapted if you have changed it in your [home-assistant] configuration.
The `node_id` gives the common prefix of all MQTT messages sent by this tool. Only
change it if you know what you are doing. The `name_prefix` is added to every
found hostname and allows you to distinguish between hosts identified by this
device tracker and hosts identified by others (like ones identified by the
[home-assistant AVM FRITZ!Box Tools] integration).

The entry `repeater` contains a list of Fritz!Repeater instances again with
`username` and `password`. For the repeaters, the username is usually `admin`
and the `password` is the password you also use in the web interface of the
repeater.

Once you have edited the file, you can verify the configuration by calling

    ha_multi_ap_tracker --config-file config.yml config show


### Testing the Data Aquisition

To test the data aquisition from the Fritz!Box and all repeaters use the command

    ha_multi_ap_tracker --config-file config.yml status show

This queries all known instances and prints a table of all found devices. You
can also display the per host information and monitor changes:

    ha_multi_ap_tracker --config-file config.yml status monitor


### Testing the MQTT Interface

To test the MQTT interface you can manually create, update and delete a
device tracker entry. To do so, use the `mqtt` subcommand:

    ha_multi_ap_tracker --config-file config.yml mqtt create TestHost
    ha_multi_ap_tracker --config-file config.yml mqtt update TestHost home
    ha_multi_ap_tracker --config-file config.yml mqtt update TestHost not_home
    ha_multi_ap_tracker --config-file config.yml mqtt delete TestHost

In the Developer Tools -> States of your [home-assistant] instance you should
be able to see the individual states of the created device tracker. Look at
the state of the `device_tracker.testhost` entity.

To test the state detection of the [home-assistant] instance call:

    ha_multi_ap_tracker --config-file config.yml mqtt listen

If you restart the [home-assistant] instance you should see the offline/online
state transition.


### Perform the Device Tracking

If all tests are successful, you can start tracking the devices. This is
done by calling:

    ha_multi_ap_tracker --config-file config.yml track

If you are in the testing phase, you can delete all created device trackes
by calling

    ha_multi_ap_tracker --config-file config.yml cleanup


## Developer Notes

### Implementation Details

The Fritz!Box and the repeaters provide information about currently connected
devices as well as currently offline devices (which were online in the past).

For this device tracker to work, we want to establish a new device state
information whenever a device is online for the first time. This means we keep
track of all devices created by this application. This allows us to identify
devices that are offline and were removed by the user from the Fritz!Box so
that we can remove them from our tracking as well.

Some OS use a random MAC address when connecting to a WLAN. This randomization
of the MAC address usually takes the SSID of the WLAN into account to ensure
the MAC address is the same when connecting to the same WLAN. However, we can't
be sure the SSID of the WLANs is always the same (if it was the user would have
setup a mesh and wouldn't need this tool). This means we can't use the MAC
address as the unique identifier for a device.

As the MAC address might change over different access points, we use the
hostname as the unique identifier of a device. For all information correlation
between the Fritz!Box and the repeaters the MAC address is still used, as for
example for the hostname derivation (repeaters use only the first 15 characters,
whereas the Fritz!Box has the full hostnames).

Another effect we've observed with random MAC addresses over multiple
differently named WLANs was stale connection entries on the Fritz!Box where
the interface was shown as Ethernet. Such entries where the interface changes
from 802.11 to Ethernet for the same MAC address are treated like going offline.


### MQTT Interface

As stated in the [MQTT Device Tracker] documentation, a device tracker entity
can be configured by publishing a configuration on the topic
`<discovery_prefix>/device_tracker/[<node_id>/]<object_id>/config`. The
individual parts are:
  - The `discovery_prefix` is usually `homeassistant` and can be configured in the
    configuration file.
  - The `node_id` is also configured in the configuration file and is named
    `multi_ap_tracker` per default.
  - The `object_id` is the internal unique ID of the device (we use the md5sum
    of the hostname).

The payload consists of the following entries encoded as a JSON map:
  - `state_topic` is set to `<node_id>/<object_id>/state`
  - `name` is set to the host name of the device.
  - `payload_home` is set to `home`.
  - `payload_not_home` is set to `not_home`.

To delete a device the configuration is published again with an empty payload.

The following commands illustrate the behaviour (Ubuntu package
`mosquitto-clients` assumed to be installed):

    # Create the tracker
    mosquitto_pub -h 192.168.1.70 \
                  -u mqtt -P <pw> \
                  -t homeassistant/device_tracker/multi_ap_tracker/abc1234/config \
                  -m '{"state_topic": "multi_ap_tracker/abc1234/state", "name": "My Tracker", "payload_home": "home", "payload_not_home": "not_home"}'
    # Set the state to 'home'
    mosquitto_pub -h 192.168.1.70 \
                  -u mqtt -P <pw> \
                  -t multi_ap_tracker/abc1234/state \
                  -m 'home'
    # Delete the tracker again
    mosquitto_pub -h 192.168.1.70 \
                  -u mqtt -P <pw> \
                  -t homeassistant/device_tracker/multi_ap_tracker/abc1234/config \
                  -m ''


### Formatting and Checking the Source Code

Before committing your changes, you should ensure the source code is formatted
with the common style and all status code checks are successful:

    make format check-style


### Creating a New Release

- Update `CHANGELOG.md`.
- Update `Makefile` to contain the new version number.
- Update `pyproject.toml` to contain the new version number.
- Update `README.md` to point the release to the new version number.
- Commit the changes onto the main branch.
- Call `make releases` to create the binaries.
- Create a new release on the github repository. Attach the binaries to it.


[home-assistant]: https://www.home-assistant.io/
[fritzconnection]: https://github.com/kbr/fritzconnection
[MQTT]: https://mqtt.org/
[MQTT Device Tracker]: https://www.home-assistant.io/integrations/device_tracker.mqtt/
[MQTT - Configure MQTT options]: https://www.home-assistant.io/integrations/mqtt/#configure-mqtt-options
[home-assistant AVM FRITZ!Box Tools]: https://www.home-assistant.io/integrations/fritz/
[home-assistant MQTT integration]: https://www.home-assistant.io/integrations/mqtt