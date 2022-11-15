"""Loft control configuration."""
import os
import sys
import socket
import logging as log
import json
import base64
import MySQLdb
from RPi import GPIO


class Config():
    """Loft control config object."""

    def __init__(self):
        """Initialise config object."""
        self.host = { 'host': "%-6s" % (socket.gethostname())}
        self.vars = {
            'interval': 0.1,
            'compensation': -10,
            'radius': 29,
            'bucketheight': 47
        }
        self.log_file = "/var/log/bucket"
        self.modes = {
            '0': GPIO.OUT,
            '1': GPIO.IN,
            'pullup': GPIO.PUD_UP,
            'pulldown': GPIO.PUD_DOWN
        }
        self.operations = {
            "on": 1,
            "off": 2
        }
        self.requests = 0
        self.pinssetup = 0
        self.units = {
            'memory': [ 'B', 'KB', 'MB', 'GB', 'TB' ]
        }
        self.setup_pins()
        self.rooms = self.setup_rooms()
        self.database = self.connect_to_db()

    def __getitem__(self, i):
        """Get item from object."""
        return getattr(self, i)

    def setup_pins(self):
        """get pin configuration from json and initialise pins."""
        localdir = os.path.dirname(os.path.realpath(__file__))
        try:
            with open("%s/pins.json" % (localdir), 'r', encoding='utf-8') as pin_fh:
                pins = json.loads(pin_fh.read())
        except ValueError as error:
            log.error('Config file has invalid format: %s', error)
            sys.exit(1)
        except FileNotFoundError:
            log.critical("Config file pins.json does not exist")
            sys.exit(1)
        for pin, pin_data in pins.items():
            setattr(self, pin, pin_data)

    def setup_rooms(self):
        """Add rooms to config."""
        return {
            "main": {
                "light": None,
                "fan": None
            },
            "bathroom": {
                "doors": 2,
                "light": None
            },
            "small": {
                "landing": None,
                "light": None
            },
            "guest": {
                "light": None,
                "fan": None
            },
            "loft": {
                'light': None,
                'valve': 4,
                'pumps': 17,
                'pump flow': 8
            }
        }

    def connect_to_db(self):
        """Create connection to the Database."""
        try:
            db_conn = MySQLdb.connect(
                host="alien.home",
                user="naruto",
                passwd=base64.b64decode('eXN0OTQq').decode('utf-8'),
                db="Denham"
            )
        except MySQLdb.Error as mys_err:
            log.error("Error connecting to DB: %s", mys_err)
            return None
        return db_conn
