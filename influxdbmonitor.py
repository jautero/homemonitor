#!/usr/bin/python

# Copyright (c) 2016 Juha Autero
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import Adafruit_DHT
import time
import influxdb

# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT11

pin = 17
fail_timestamp=0
fail_message=""

client=influxdb.InfluxDBClient("docker.trollitehdas.fi",8086,"root","root","homemonitor")


def get_weather_dict(temp,hum):
    return {"measurement": "livingroom_weather",
            "fields": {
                "temperature": temp,
                "humidity" : hum }}
def get_error_dict():
    return {"measurement": "livingroom_error",
            "fields": {
                "message": fail_message,
                "duration": time.time()-fail_timestamp
            }}

while True:
    try:
	    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

	    if humidity is not None and temperature is not None:    
	        data=[get_weather_dict(temperature,humidity)]
            if fail_timestamp!=0:
                fail_timestamp=0
                data.append(get_error_dict())
	        client.write_points(data)
	    else:
	        fail_timestamp=time.time()
            fail_message='Failed to get sensor reading.'
	    time.sleep(60)
    except:
        fail_timestamp=time.time()
        fail_message="Failed to send data"
