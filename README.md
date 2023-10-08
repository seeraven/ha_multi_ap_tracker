# ha_multi_ap_tracker

This repository hosts the `ha_multi_ap_tracker`, a custom device tracker for
[home-assistant] to track WiFi devices over non-mesh configurations. It uses the
[fritzconnection] interface to query all devices and builds up a combined view
of the availability of the devices. The state of the individual devices is
communicated to [home-assistant] via [MQTT].


## Installation


## Configuration

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
  host: mqtt.local.net
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
the [home-assistant MQTT integration] you should set the `host` attribute to
the IP of your [home-assistant] instance and if you are using an authentication
you should adjust the `username` and `password` settings.

The entry `repeater` contains a list of Fritz!Repeater instances again with
`username` and `password`. For the repeaters, the username is usually `admin`
and the `password` is the password you also use in the web interface of the
repeater.

Once you have edited the file, you can verify the configuration by calling

    ha_multi_ap_tracker --config-file config.yml config show


## Testing the Data Aquisition

To test the data aquisition from the Fritz!Box and all repeaters use the command

    ha_multi_ap_tracker --config-file config.yml status show

This queries all known instances and prints a table of all found devices.


## Implementation Details

The Fritz!Box and the repeaters provide information about currently connected
devices as well as currently offline devices (which were online in the past).

For this device tracker to work, we want to establish a new device state
information whenever a device is online for the first time. This means we keep
track of all devices created by this application. This allows us to identify
devices that are offline and were removed by the user from the Fritz!Box so
that we can remove them from our tracking as well.


## Developer Notes

### Formatting and Checking the Source Code

Before committing your changes, you should ensure the source code is formatted
with the common style and all status code checks are successful:

    make format check-style


### Creating a New Release


[home-assistant]: https://www.home-assistant.io/
[fritzconnection]: https://github.com/kbr/fritzconnection
[MQTT]: https://mqtt.org/
[MQTT Device Tracker]: https://www.home-assistant.io/integrations/device_tracker.mqtt/
[home-assistant AVM FRITZ!Box Tools]: https://www.home-assistant.io/integrations/fritz/
[home-assistant MQTT integration]: https://www.home-assistant.io/integrations/mqtt