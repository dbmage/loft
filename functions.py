"""Loft control functions."""
import os
import re
import time
import logging as log
from math import pi
import psutil
from RPi import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def pin_setup(config):
    """Setup pins for use with Python."""
    for _pin_id, pin_data in config.pins.items():
        pin = pin_data['BCM']
        mode = pin_data['Mode']
        use = pin_data['Use']
        log.info("[%s] Use: %-10s Mode: %-8s (%s)", pin, use, config.modes[mode], mode)
        if mode not in config.modes:
            log.error("[%s] Pin incorrectly setup", pin)
            continue
        log.info("[%s] Setting up %-10s to %-8s mode", pin, use, config.modes[mode])
        GPIO.setup(pin, config.modes[mode])


def get_state(config, thing):
    """Get a thing state."""
    pin = config.pins[thing]['BCM']
    try:
        state = GPIO.input(pin)
    except:
        log.error("Unable to get %s state", pin)
        return "Unable to get %s state" % (pin)
    return state


def get_info(config, thing):
    """Get all data for a thing."""
    for pin_no, pin_data in config.pins.items():
        if pin_data[pin_no] != thing:
            continue
        return pin_data[pin_no]
    log.error("Unable to find %s", thing)
    return False


def get_all_info(config):
    """Get info for everything configured."""
    return config.pins


def flip_relay(config, relay_id):
    """Flip a relay to it's alternate state."""
    pin = config.pins[relay_id]
    state = GPIO.input(pin)
    if state == 0:
        GPIO.output(pin, True)
    elif state == 1:
        GPIO.output(pin, False)
    state = GPIO.input(pin)
    return state


def force_relay(config, thing, state):
    """Force a thing into a state."""
    pin = config.pins[thing]
    if state == "off":
        GPIO.output(pin, True)
    elif state == "on":
        GPIO.output(pin, False)
    state = GPIO.input(pin)
    return state


def force_relays(_config, _state):
    """Force all relays to a state."""
    return False


def time_relay(_config, _relay, _duration):
    """Operate a relay on a timer."""
    return False


def get_cpu():
    """Retrieve CPU usage."""
    load = psutil.cpu_percent(interval=1)
    load = "%s%%" % (load)
    return load


def get_ram(config):
    """Get Pi RAM data."""
    mem = psutil.virtual_memory()
    free = mem[0] - mem[3]
    used = ram_b_to_mb(config, mem[3])
    total = ram_b_to_mb(config, mem[0])
    free = ram_b_to_mb(config, free)
    percent = mem[2]
    return [ used, total, free, percent ]


def get_off(config):
    """Retrieve count of off pins."""
    off_pins = 0
    for name in config.pins:
        if get_state(config, name) == 0:
            off_pins += 1
    return off_pins


def get_on(config):
    """Retrieve count of on pins."""
    on_pins = 0
    for name in config.pins:
        if get_state(config, name) == 1:
            on_pins += 1
    return on_pins


def get_all_states(config):
    """Get the state of every configured thing."""
    allstates = {}
    for job in config.pins:
        allstates[job] = get_state(config, job)
    return allstates


def ram_b_to_mb(config, item):
    """Convert bytes to megabytes."""
    count = 0
    while item > 1024:
        item = item / 1024
        count = count + 1
    item = ' '.join([item, config.units['memory'][count]])
    return item

#def getbucketlevels( i ):
#    return False

def get_bucket_levels(config, trigger, echo):
    """Retrieve water bucket levels."""
    for _x in range(0,600):
        os.system('echo "" > /dev/null')
    maximum = 120
    # Set trigger to False (Low)
    GPIO.output(trigger, False)
    print("trigger to low")
    # Allow module to settle
    time.sleep(0.5)
    print("Sending pulse")
    # Send 10us pulse to trigger
    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)
    print("Sent Pulse")
    start = time.time()
    timeout = time.time() + 10
    while GPIO.input(echo)==0:
        start = time.time()
        if time.time() > timeout:
            print("Timeout")
            return "0"

    while GPIO.input(echo)==1:
        stop = time.time()
    print("got response")
    # Calculate pulse length
    elapsed = stop-start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34000

    # That was the distance there and back so halve the value
    distance = distance / 2
    distance = round((distance + config.vars['compensation']),2)
    volume = round(maximum - (((config.vars['radius'] * config.vars['radius']) * pi) * distance) / 1000, 2)
    return str(volume)


def bucket_checker(config):
    """Check bucket levels and action valves accordingly."""
    now = time.strftime("%M")
    if now % 5 != 0:
        return
    data = {
        'cold': get_bucket_levels(config, config.buckets['cold']['trig'], config.buckets['cold']['echo']),
        'hot': get_bucket_levels(config, config.buckets['hot']['trig'], config.buckets['hot']['echo'])
    }

    for bucket_name, bucket_level in data.items():
        if bucket_level > 120:
            force_relay(config, "%s_valve" % (bucket_name), 'off')
            log.info("%s is more than 120, closing valve", bucket_name)
        if bucket_level < 40:
            force_relay(config, "%s_valve" % (bucket_name), 'on')
            log.info("%s is less than 40, opening valve", bucket_name)
    # cursor = config.database.cursor()
    # try:
    #     cursor.execute(
    #         """INSERT INTO waterlevels (Date, Time, LBD, LBV, RBD, RBV) VALUES (%s,%s,%s,%s,%s,%s)""",
    #         (date, runtime, OUTPUT[1], OUTPUT[2], OUTPUT[4], OUTPUT[5])
    #     )
    #     config.database.commit()
    # except MySQLdb.Error as mys_err:
    #     config.database.rollback()
    #     log.info("not updated - %s" % (mys_err.args[1]))


def get_sensor_reading(sensor):
    """Retrieve temperature sensor reading."""
    base_dir = '/sys/bus/w1/devices'
    tempfile = '/'.join([base_dir, sensor, "w1_slave"])
    if not os.path.isfile(tempfile):
        return False
    with open(tempfile, 'r', encoding='utf-8') as tmp_fh:
        lines = tmp_fh.readlines()
    if lines[0].strip()[-3:] != 'YES':
        return 1
    equals_pos = lines[1].find('t=')
    if equals_pos == -1:
        return 1
    temp_string = lines[1][equals_pos+2:]
    temp = float(temp_string) / 1000.0
    return temp


def get_cylinder_temps(config):
    """Retrieve cylinder temperatures."""
    os.system('sudo modprobe wire')
    os.system('sudo modprobe w1-gpio')
    os.system('sudo modprobe w1-therm')
    bottom = get_sensor_reading(config.sensors['bottom'])
    middle = get_sensor_reading(config.sensors['middle'])
    top = get_sensor_reading(config.sensors['top'])

    if sum([int(bottom), int(middle), int(top)]) == 0:
        log.error("Sensors not connected")
        return {"Error" : "Sensors not connected"}
    while bottom == 1:
        bottom = get_sensor_reading(config.sensors['bottom'])
    while middle == 1:
        middle = get_sensor_reading(config.sensors['middle'])
    while top == 1:
        top = get_sensor_reading(config.sensors['top'])

    log.info("%s - %s - %s", top, middle, bottom)
    data = {"top" : top, "middle" : middle, "bottom" : bottom}
    return data


def get_all_routes(appfile):
    """Find and return all app routes."""
    with open(appfile, 'r', encoding='utf-8') as app_fh:
        lines = app_fh.readlines()
    approutes = []
    for line in lines:
        aroute = re.search(r'^\@route\(\'(.*)\'\)', line)
        if aroute:
            theroute = aroute.group(1)
            theroute = re.sub(r"\<", "&lt", theroute)
            theroute = re.sub(r"\>", "&gt", theroute)
            approutes.append(theroute)
    if len(approutes) > 1:
        approutes.pop(0)
    return approutes
