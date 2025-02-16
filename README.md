# RTL_433 Discover and Submit

This Home Assistant add-on uses rtl_433 to automatically discover wireless sensors and integrate them with Home Assistant via MQTT auto-discovery.

## Features

- Automatically discovers wireless sensors using rtl_433
- Creates device entries in Home Assistant for discovered sensors
- Forwards sensor data to Home Assistant via MQTT
- Configurable MQTT settings and rtl_433 parameters

## Requirements

- An RTL-SDR USB dongle
- Working MQTT broker (like the Mosquitto add-on)
- Home Assistant with MQTT integration enabled

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the add-on
3. Configure the required options
4. Start the add-on

## Configuration

| Option | Description |
|--------|-------------|
| `mqtt_discovery_prefix` | The prefix used for MQTT discovery (default: homeassistant) |
| `mqtt_topic_prefix` | The prefix used for MQTT topics (default: rtl_433) |
| `mqtt_retain` | Whether to retain MQTT messages (default: true) |
| `rtl_433_advanced_params` | Additional parameters to pass to rtl_433 |
| `rtl_433_protocol_params` | Protocol-specific parameters for rtl_433 |
| `log_level` | The log level for the add-on |

## Supported Devices

This add-on can discover a wide range of wireless sensors supported by rtl_433, including:

- Weather stations
- Thermometers
- Door/window sensors
- Motion detectors
- And many more

## Support

For issues, feature requests, or questions, please open an issue in the [GitHub repository](https://github.com/dewgenenny/rtl_433_discoverandsubmit).
