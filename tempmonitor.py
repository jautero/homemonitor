# -*- coding: utf-8 -*-
# Based on example.py in dht11

import RPi.GPIO as GPIO
import dht11
import w1thermsensor
import time
import datetime
import paho.mqtt.client as mqtt

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# read data using pin 17
indoortemp = dht11.DHT11(pin=17)
outdoortemp = w1thermsensor.W1ThermSensor()
auth={'username':'mqtt','password':'mqtt'}
do_configuration=True

def on_connect(client, userdata, flags, rc):
    # (Re)Subscribe to topic on connection.
    client.subscribe("homeassistant/sensor/restart/state")

def on_message(client, userdata, msg):
    if msg.topic == "homeassistant/sensor/restart/state":
        do_configuration=True

def on_disconnect(client, userdata, rc):
    if rc != 0:
        client.reconnect()


client=mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnext = on_disconnect

client.username_pw_set(auth['username'],auth['password'])
client.connect("homeassistant.local")
client.loop_start()

config_msgs=[
    ("homeassistant/sensor/indoor/config",'{"device_class": "temperature", "name": "indoor temperature", "state_topic": "homeassistant/sensor/indoor/state", "unit_of_measurement": "°C"}',0,False),
    ("homeassistant/sensor/humidity/config",'{"device_class": "humidity", "name": "indoor humidity", "state_topic": "homeassistant/sensor/humidity/state", "unit_of_measurement": "%"}',0,False),
    ("homeassistant/sensor/outdoor/config",'{"device_class": "temperature", "name": "outdoor temperature", "state_topic": "homeassistant/sensor/outdoor/state", "unit_of_measurement": "°C"}',0,False)]


try:
    while True:
        if do_configuration:
            for msg in config_msgs:
                client.publish(*msg)
            do_configuration=False
        result = indoortemp.read()
        outresult = outdoortemp.get_temperature()
        if result.is_valid():
            client.publish("homeassistant/sensor/indoor/state", result.temperature)
            client.publish("homeassistant/sensor/humidity/state", result.humidity)
            client.publish("homeassistant/sensor/outdoor/state", outresult)

        time.sleep(60) # Sleep one minute

except KeyboardInterrupt:
    print("Cleanup")
    client.loop_stop()
    GPIO.cleanup()
