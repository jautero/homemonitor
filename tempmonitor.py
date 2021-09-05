# Based on example.py in dht11

import RPi.GPIO as GPIO
import dht11
import w1thermsensor
import time
import datetime
import paho.mqtt.publish as publish

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# read data using pin 17
indoortemp = dht11.DHT11(pin=17)
outdoortemp = w1thermsensor.W1ThermSensor()
auth={'username':'mqtt','password':'mqtt'}

config_msgs=[
    ("homeassistant/sensor/indoor/config",'{"device_class": "temperature", "name": "indoor temperature", "state_topic": "homeassistant/sensor/indoor/state", "unit_of_measurement": "°C"}',0,False),
    ("homeassistant/sensor/humidity/config",'{"device_class": "humidity", "name": "indoor humidity", "state_topic": "homeassistant/sensor/humidity/state", "unit_of_measurement": "%"}',0,False),
    ("homeassistant/sensor/outdoor/config",'{"device_class": "temperature", "name": "outdoor temperature", "state_topic": "homeassistant/sensor/outdoor/state", "unit_of_measurement": "°C"}',0,False)]


try:
    while True:
        result = indoortemp.read()
        outresult = outdoortemp.get_temperature()
        if result.is_valid():
            print("Last valid input: " + str(datetime.datetime.now()))
            print("Temperature: %-3.1f C" % result.temperature)
            publish.single("homeassistant/sensor/indoor/state", result.temperature, hostname="homeassistant.local", auth=auth)
            print("Humidity: %-3.1f %%" % result.humidity)
            publish.single("homeassistant/sensor/humidity/state", result.humidity, hostname="homeassistant.local", auth=auth)
            print("Outdoors: %-3.1f C" % outresult)
            publish.single("homeassistant/sensor/outdoor/state", outresult, hostname="homeassistant.local", auth=auth)

        time.sleep(6)

except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()
