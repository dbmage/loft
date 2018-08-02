import time
import sys
import psutil
import RPi.GPIO as GPIO
from math import pi
import MySQLdb

INTERVAL = 0.1

setup = {
    "pins" : {
        "1" : {
            "Use" : "valve",
            "Description" : "Mains valve to buckets",
            "Name" : "GPIO. 7",
            "Wpi" : "7",
            "Mode" : 0, # 0 = out, 1 = in
            "BCM" : 4,
            "physical" : "7",
        },
        "2" : {
            "Use" : "lights",
            "Description" : "Controls mains power to big bathroom lights",
            "Name" : "SCL.1",
            "Wpi" : "9",
            "Mode" : 0,
            "BCM" : 3,
            "physical" : "5",
        },
        "3" : {
            "Use" : "door",
            "Description" : "Possibly unlocks the doors",
            "Name" : "SDA.1",
            "Wpi" : "8",
            "Mode" : 0,
            "BCM" : 2,
            "physical" : "3",
        },
        "4" : {
            "Use" : "pumps",
            "Description" : "Controls mains power to pumps",
            "Name" : "GPIO. 0",
            "Wpi" : "0",
            "Mode" : 0,
            "BCM" : 17,
            "physical" : "11",
        },
        "5" : {
            "Use" : "pump_flow",
            "Description" : "overrides pump flow switch (which pump)",
            "Name" : "CE0",
            "Wpi" : "10",
            "Mode" : 0,
            "BCM" : 8,
            "physical" : "24",
        },
        "6" : {
            "Use" : "NONE",
            "Description" : "NONE",
            "Name" : "NONE",
            "Wpi" : False,
            "Mode" : 1,
            "BCM" : False,
            "physical" : False,
        },
    },
    "unused" : [
        "shaun fan",
        "shaun light",
        "loft light",
        "landing light",
        "bathroom light"
    ],
    "rooms" : {
        "shaun" : {
            "light" : '',
            "fan" : ''
        },
        "bathroom" : {
            "doors" : 2,
            "light" : ''
        },
        "kyle" : {},
            "landing" : {
            "light" : ''
        },
        "loft" : {
            'light' : '',
            'valve' : 4,
            'pumps' : 17,
            'pump flow' : 8
        },
    },
    "sensors" : {
        "top"     : "28-011581c911ff", #originally labelled bottom
        "middle"  : "28-0115818c64ff", #originally labelled top
        "bottom"  : "28-0115818d1bff", #originally labelled middle
        "bucket1" : "28-011581c830ff",
        "bucket2" : "28-021581de70ff"
    },
    "modes" : {
        0 : "GPIO.OUT",
        1 : "GPIO.IN"
    },
    "operations" : {
        "on" : 1,
        "off" : 2
    },
    "requests" : 0,
}

units = {'memory' : [ 'B', 'KB', 'MB', 'GB' ]}

pins = { 'valve' : 4, 'lights' : 3, 'door' : 2, 'pumps' : 17, 'pump flow' : 8 }

TRIGGER_PINS = [15, 14] # left, right
ECHO_PINS = [22, 27] # left, right
compensation = -10 # -11
RADIUS = 29
timeout = time.time() + 30
bucketheight = 47

log="/var/log/bucket"
db = MySQLdb.connect(host="alien",    # your host, usually localhost
                     user="naruto",         # your username
                     passwd="yst94*",  # your password
                     db="Stuff")        # name of the data base
