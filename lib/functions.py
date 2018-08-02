#!/usr/bin/python
import time
import sys
import psutil
import RPi.GPIO as GPIO
import os
import re
from math import pi

sys.path.append('/usr/sbin/loft/bottle/etc')

import config as cfg

INTERVAL = cfg.INTERVAL
log = cfg.log
setup = cfg.setup
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
for name in cfg.pins:
    pin = cfg.pins[name]
    print("%s - %s" % (name, pin))
    GPIO.setup(pin,GPIO.OUT)

def getstate( relay ):
    pin = cfg.pins[relay]
    try:
        state = GPIO.input(pin)
    except error:
        return error

    return state

def getinfo( thing ):
    for pinno in cfg.setup['pins']:
        if cfg.setup['pins'][pinno] != thing:
            next
        return cfg.setup['pins'][pinno]
    return False

def getallinfo( ):
    return cfg.setup['pins']

def fliprelay( relay ):
    pin = cfg.pins[relay]
    state = GPIO.input(pin)

    if state == 0:
        GPIO.output(pin, True)
    elif state == 1:
        GPIO.output(pin, False)

    state = GPIO.input(pin)
    return state

def forcerelay( relay, state):
    pin = cfg.pins[relay]
    if state == "off":
        GPIO.output(pin, True)
    elif state == "on":
        GPIO.output(pin, False)

    state = GPIO.input(pin)
    return state

def forcerelays( relay ):
    return False

def timerelay( relay ):
    return False

def getcpu():
    load = psutil.cpu_percent(interval=1)
    load = str(load) + '%'
    return load

def getram():
    mem = psutil.virtual_memory()
    free = mem[0] - mem[3]
    used = rambtomb(mem[3])
    total = rambtomb(mem[0])
    free = rambtomb(free)
    percent = mem[2]
    return [ used, total, free, percent ]

def getoff( ):
    off = 0
    for name in cfg.pins:
        state = getstate(name)
#        print "%s - %i - %s" % (name, pin, state)
        if state == 0:
            off += 1

    return off

def geton( ):
    on = 0
    for name in cfg.pins:
        state = getstate(name)
#        print "%s - %i - %s" % (name, pin, state)
        if state == 1:
            on += 1

    return on

def getallstates( ):
    allstates = {}
    for job in cfg.pins:
        allstates[job] = getstate(job)
    return allstates

def rambtomb( item ):
    count = 0
    while item > 1024:
        item = item / 1024
        count = count + 1

    item = str(item) + ' ' + cfg.units['memory'][count]
    return item

#def getbucketlevels( i ):
#    return False

def getbucketlevels( i ):
    global cfg
    i = int( i )
    GPIO_TRIGGER = cfg.TRIGGER_PINS[i]
    GPIO_ECHO = cfg.ECHO_PINS[i]
    # Set pins as output and input
    GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
    GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

    # Set trigger to False (Low)
    GPIO.output(GPIO_TRIGGER, False)

    # Allow module to settle
    time.sleep(0.5)

    # Send 10us pulse to trigger
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)

    GPIO.output(GPIO_TRIGGER, False)
    start = time.time()

    while GPIO.input(GPIO_ECHO)==0:
        start = time.time()
#        if time.time() > cfg.timeout:
#            print "Start: %s\nNow: %s\nTIMEOUT" % (start, time.time())
#            return "0"

    while GPIO.input(GPIO_ECHO)==1:
        stop = time.time()

    # Calculate pulse length
    elapsed = stop-start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34000

    # That was the distance there and back so halve the value
    distance = distance / 2
    distance = round((distance + cfg.compensation),2)
    volume = round((((cfg.RADIUS * cfg.RADIUS) * pi) * distance) / 1000, 2)
    return str(volume)

#def bucketchecker( ):
#    return False

def bucketchecker( ):
    date = time.strftime("%d/%m/%y")
    runtime = time.strftime("%H:%M:%S")
    now = time.strftime("%M")

    if now % 5 != 0:
        return

    left = getbucketlevels(0)
    right = getbucketlevels(1)
    data = "%s - %s - %s - %s" % (date, runtime, left, right)

    if left > 120 and right > 120:
        forcerelay( 'valve', 'off' )
        data = "%s or %s is more than 120, closing valve" % (left, right)
        with open(log, "a") as myfile:
            myfile.write(data + "\n")

    if left < 40 and right < 40:
        forerelay( 'valve', 'on' )
        data = "%s or %s is less than 40, opening valve" % (left, right)
        with open(log, "a") as myfile:
            myfile.write(data + "\n")

    x = db.cursor()
    try:
        x.execute("""INSERT INTO waterlevels (Date, Time, LBD, LBV, RBD, RBV) VALUES (%s,%s,%s,%s,%s,%s)""",(date, runtime, OUTPUT[1], OUTPUT[2], OUTPUT[4], OUTPUT[5]))
        db.commit()
    except MySQLdb.Error, e:
        db.rollback()
        data = "not updated - %s" % (e.args[1])
        with open(log, "a") as myfile:
            myfile.write(data + "\n")

    db.close()

def getSensorReading(sensor):
    base_dir = '/sys/bus/w1/devices/'
    tempfile = "%s%s/%s" % (base_dir, sensor, "w1_slave")
    if not os.path.isfile(tempfile):
        return False
    f = open(tempfile, 'r')
    lines = f.readlines()
    f.close
    if lines[0].strip()[-3:] != 'YES':
	return 1
    equals_pos = lines[1].find('t=')
    if equals_pos == -1:
        return 1
    temp_string = lines[1][equals_pos+2:]
    temp = float(temp_string) / 1000.0
    return temp

def getCylinderTemps():
    os.system('sudo modprobe wire')
    os.system('sudo modprobe w1-gpio')
    os.system('sudo modprobe w1-therm')
    date = time.strftime("%d/%m/%y")
    runtime = time.strftime("%H:%M:%S")
    bottom = getSensorReading(cfg.setup['sensors']['bottom'])
    middle = getSensorReading(cfg.setup['sensors']['middle'])
    top = getSensorReading(cfg.setup['sensors']['top'])

    if bottom == False and middle == False and top == False:
        return {"Error" : "Sensors not connected"}

    while bottom == 1:
         bottom = getSensorReading(cfg.setup['sensors']['bottom'])

    while middle == 1:
        middle = getSensorReading(cfg.setup['sensors']['middle'])

    while top == 1:
        top = getSensorReading(cfg.setup['sensors']['top'])

    logdata = "%s - %s - %s - %s - %s" % (date, runtime, top, middle, bottom)
    with open(log, "a") as myfile:
         myfile.write(logdata + "\n")

    data = {"top" : top, "middle" : middle, "bottom" : bottom}
    return data


def getAllRoutes(appfile):
    f = open(appfile, 'r')
    lines = f.readlines()
    f.close
    approutes = []
    for line in lines:
        aroute = re.search('^\@route\(\'(.*)\'\)', line)
        if aroute:
            theroute = aroute.group(1)
            theroute = re.sub(r"\<", "&lt", theroute)
            theroute = re.sub(r"\>", "&gt", theroute)
            approutes.append(theroute)
    approutes.pop(0)
    return approutes
