#!/usr/bin/env python3

import json
import logging
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime

import paho.mqtt.client as mqtt

# Configure logging
log_levels = {
    'TRACE': logging.DEBUG,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'FATAL': logging.CRITICAL
}
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=log_levels.get(log_level, logging.INFO),
                   format='%(asctime)s [%(levelname)s] %(message)s',
                   datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Get MQTT configuration from environment variables
MQTT_HOST = os.environ.get('MQTT_HOST', 'core-mosquitto')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_USER = os.environ.get('MQTT_USER', '')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')
MQTT_DISCOVERY_PREFIX = os.environ.get('MQTT_DISCOVERY_PREFIX', 'homeassistant')
MQTT_TOPIC_PREFIX = os.environ.get('MQTT_TOPIC_PREFIX', 'rtl_433')
MQTT_RETAIN = os.environ.get('MQTT_RETAIN', 'true').lower() == 'true'
RTL_433_ADVANCED_PARAMS = os.environ.get('RTL_433_ADVANCED_PARAMS', '')
RTL_433_PROTOCOL_PARAMS = os.environ.get('RTL_433_PROTOCOL_PARAMS', '')

# Store discovered sensors
discovered_sensors = {}

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        if MQTT_USER and MQTT_PASSWORD:
            self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        
        self.client.on_connect = self.on_connect
        
    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to MQTT broker with result code {rc}")
    
    def connect(self):
        try:
            self.client.connect(MQTT_HOST, MQTT_PORT, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def publish(self, topic, payload, retain=False):
        try:
            self.client.publish(topic, payload, retain=retain)
            return True
        except Exception as e:
            logger.error(f"Failed to publish MQTT message: {e}")
            return False

def sanitize(text):
    return text.lower().replace(' ', '_')

def create_device_config(data):
    model = data.get('model', '').strip()
    device_id = None
    
    if 'id' in data:
        device_id = f"{model}_{data['id']}"
    elif 'channel' in data and ('raw_message' in data or 'message' in data):
        msg = data.get('raw_message', data.get('message', ''))
        device_id = f"{model}_{data['channel']}_{msg}"
    
    if not device_id:
        return None
    
    device_id = sanitize(device_id)
    
    # Only create config for new devices
    if device_id in discovered_sensors:
        return None
    
    logger.info(f"Discovered new sensor: {device_id}")
    discovered_sensors[device_id] = True
    
    config = {
        "device": {
            "identifiers": [device_id],
            "name": f"RTL_433 {model} {data.get('id', '')}",
            "model": model,
            "manufacturer": "RTL_433"
        }
    }
    
    entities = []
    
    # Create entities for each sensor type
    for key, value in data.items():
        if key in ['id', 'model', 'channel', 'message', 'raw_message']:
            continue
        
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
            entity_config = {
                "name": f"{model} {key}",
                "unique_id": f"{device_id}_{key}",
                "state_topic": f"{MQTT_TOPIC_PREFIX}/{device_id}",
                "value_template": f"{{{{ value_json.{key} }}}}",
                "device": config["device"]
            }
            
            # Add unit based on key name
            if key == 'temperature_C':
                entity_config["unit_of_measurement"] = "°C"
                entity_config["device_class"] = "temperature"
            elif key == 'temperature_F':
                entity_config["unit_of_measurement"] = "°F"
                entity_config["device_class"] = "temperature"
            elif key == 'humidity':
                entity_config["unit_of_measurement"] = "%"
                entity_config["device_class"] = "humidity"
            elif key == 'battery_ok':
                entity_config["device_class"] = "battery"
                entity_config["entity_category"] = "diagnostic"
            
            discovery_topic = f"{MQTT_DISCOVERY_PREFIX}/sensor/{device_id}/{key}/config"
            entities.append((discovery_topic, entity_config))
    
    return entities

def handle_rtl_433_data(mqtt_client, data):
    try:
        json_data = json.loads(data)
        
        # Create device discovery configurations
        configs = create_device_config(json_data)
        if configs:
            for topic, config in configs:
                mqtt_client.publish(topic, json.dumps(config), retain=MQTT_RETAIN)
        
        # Get device ID
        if 'model' in json_data and ('id' in json_data or 'channel' in json_data):
            model = json_data.get('model', '').strip()
            if 'id' in json_data:
                device_id = f"{model}_{json_data['id']}"
            else:
                msg = json_data.get('raw_message', json_data.get('message', ''))
                device_id = f"{model}_{json_data['channel']}_{msg}"
            
            device_id = sanitize(device_id)
            
            # Publish state update
            state_topic = f"{MQTT_TOPIC_PREFIX}/{device_id}"
            mqtt_client.publish(state_topic, data, retain=False)
            
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON received from rtl_433: {data}")
    except Exception as e:
        logger.error(f"Error handling rtl_433 data: {e}")

def build_rtl_433_command():
    cmd = [
        'rtl_433',
        '-F', 'json',
        '-M', 'time:iso:usec'
    ]
    
    if RTL_433_PROTOCOL_PARAMS:
        cmd.extend(RTL_433_PROTOCOL_PARAMS.split())
    
    if RTL_433_ADVANCED_PARAMS:
        cmd.extend(RTL_433_ADVANCED_PARAMS.split())
    
    return cmd

def main():
    mqtt_client = MQTTClient()
    if not mqtt_client.connect():
        logger.error("Failed to connect to MQTT. Exiting.")
        sys.exit(1)
    
    logger.info("Starting rtl_433 process...")
    rtl_433_cmd = build_rtl_433_command()
    logger.info(f"Command: {' '.join(rtl_433_cmd)}")
    
    rtl_433_process = subprocess.Popen(
        rtl_433_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    def cleanup(signum, frame):
        logger.info("Terminating rtl_433 process...")
        rtl_433_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    
    try:
        for line in iter(rtl_433_process.stdout.readline, ''):
            line = line.strip()
            if line:
                handle_rtl_433_data(mqtt_client, line)
    finally:
        cleanup(None, None)

if __name__ == "__main__":
    main()
