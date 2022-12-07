"""Loft control app."""
#!/usr/bin/python3
import os
import sys
import json
import socket
import logging as log
from lazylog import Logger
import bottle
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import functions
from loft_config import Config

config = Config()
logspec = { "filename" : "loft-api-error.log",
            "level" : "INFO",
            "splitlines" : True,
            "pretty" : True,
            "fmt" : "%(asctime)s %(levelname)-8s %(module)15.15s %(funcName)-15s: %(message)s" }

Logger.init('/var/log/',  termSpecs={"level" : 60}, fileSpecs=[logspec])
__builtins__['log'] = log
functions.pin_setup(config)

def ret_http(retcode, data=None):
    """Return a HTTP Response with code and data."""
    if not data:
        return bottle.Response(status=retcode, mimetype='text/html')
    try:
        jsondata = json.dumps(data)
        return bottle.Response(jsondata, status=retcode, mimetype='application/json')
    except TypeError:
        pass
    return bottle.Response(data, status=retcode, mimetype='text/html')


def ret_ok(data=None):
    """Return 200."""
    return ret_http(200, data=data)


def ret_error(data=None):
    """Retrun 500."""
    return ret_http(500, data=data)


@bottle.route('/')
def index():
    """Default route."""
    pid = os.getpid()
    cpu = functions.get_cpu()
    (usedram, totalram, _freeram, rampercent) = functions.get_ram(config)
    on_pins = functions.get_on(config)
    off_pins = functions.get_off(config)
    myapproutes = "<br>".join(functions.get_all_routes(os.path.realpath(__file__)))
    #print myapproutes
    return (
        '<h2>Online  <img src="http://192.168.0.101/on.png" width="20px"></h2>\n'
        '<h3>Requests processed: ' + str(config.requests) + '<h3>\n'
        '<br>\n'
        '<h3>Process ID: ' + str(pid) + ' </h3>\n'
        '<h3>CPU: ' + str(cpu) + '</h3>\n'
        '<h3>RAM: ' + str(usedram) + ' / ' + str(totalram) + ' (' + str(rampercent) + '%)</h3>\n'
        '<hr>\n'
        '<h3>Relays</h3>\n'
        '<h3>On:  ' + str(on_pins) + '</h3>\n'
        '<h3>Off: ' + str(off_pins) + '</h3>\n'
        '<h3>Available routes:</h3>\n'
        '<h3>' + myapproutes + '</h3>\n'
        '<!--<iframe src="http://192.168.0.101/" width="80%" height="80%">-->\n'
    )


@bottle.route('/devquery')
def dev_query():
    """Device query."""
    config.requests += 1
    return ret_ok(data=socket.gethostname())


@bottle.route('/getconfig')
def get_config():
    """Retrieve config."""
    config.requests += 1
    return ret_ok(data=config.__dict__)


@bottle.route('/flip/<relay>')
def flip_relay(relay):
    """Flip a relay."""
    config.requests += 1
    returned = functions.flip_relay(config, relay)
    return ret_ok(data=returned)


@bottle.route('/control/<operation>/<relay>')
def force_relay(operation, relay):
    """Force a relay."""
    config.requests += 1
    returned = functions.force_relay(config, operation, relay)
    if returned == 0:
        return ret_ok()
    return ret_error()


@bottle.route('/off')
def all_off():
    """Turn everything configured off."""
    config.requests += 1
    returned = functions.force_relays(config, "off")
    if returned == 0:
        return ret_ok()
    return ret_error()


@bottle.route('/on')
def all_on():
    """Turn everything configured on."""
    config.requests += 1
    returned = functions.force_relays(config, "on")
    if returned == 0:
        return ret_ok()
    return ret_error()


@bottle.route('/timed/<relay>/<duration>')
def timed_relay(relay, duration):
    """Operate a relay for a specified time."""
    config.requests += 1
    returned = functions.time_relay(config, relay, duration)
    if returned == 0:
        return ret_ok()
    return ret_error()


@bottle.route('/getstate/<relay>')
def get_state(relay):
    """Retrieve a state."""
    config.requests += 1
    state = functions.get_state(config, relay)
    return ret_ok(data=state)


@bottle.route('/getinfo/<thing>')
def get_info(thing):
    """Retrieve info for a thing."""
    config.requests += 1
    return ret_ok(data=functions.get_info(config, thing))


@bottle.route('/getallinfo')
def get_all_info():
    """Retrieve informaton about everything configured."""
    config.requests += 1
    return ret_ok(data=functions.get_all_info(config))


@bottle.route('/getallstates')
def get_all_states():
    """Retrieve states for everything configured."""
    config.requests += 1
    return ret_ok(data=functions.get_all_states(config))


@bottle.route('/getlevel/<bucket>')
def get_level(bucket):
    """Retrieve level for specified bucket."""
    config.requests += 1
    if bucket not in config.buckets:
        return ret_ok(data=1.00)
        # return ret_error(data={'error': "%s not found" % (bucket)})
    return ret_ok(
        data=functions.get_bucket_levels(config, config.buckets[bucket]['trig'], config.buckets[bucket]['echo'])
    )


@bottle.route('/getlevels/')
def get_levels():
    """Retrieve all bucket levels."""
    config.requests += 1
    levels = {
        'left': 0,
        'right': 0
        # 'left': functions.get_bucket_levels(config, config.buckets['left']['trig'], config.buckets['left']['echo']),
        # 'right': functions.get_bucket_levels(config, config.buckets['right']['trig'], config.buckets['right']['echo'])
    }
    return ret_ok(data=levels)


@bottle.route('/getcylindertemps/')
def get_cylinder_temps():
    """Retrieve all cylinder temperatures."""
    config.requests += 1
    return ret_ok(data=functions.get_cylinder_temps(config))


@bottle.route('/getwatertemp/')
def get_water_temp():
    """Retrieve hot water temperature."""
    config.requests += 1
    temps = functions.get_cylinder_temps(config)
    return ret_ok(data=temps['middle'])


@bottle.route('/getbuckettemps/')
def get_bucket_temps():
    """Retrieve water bucket temperatures."""
    config.requests += 1
    return ret_ok(data=
        {
            'cold' : functions.get_sensor_reading(config.sensors['cold']),
            'hot' : functions.get_sensor_reading(config.sensors['hot'])
        }
    )


@bottle.route('/getupstairstemp/')
def get_upstairs_temp():
    """Retrieve landing temperature."""
    config.requests += 1
    return ret_ok(data=functions.get_sensor_reading(config.sensors['upstairs']))


@bottle.route('/gettemp/<location>')
def get_temp(location):
    """Retrieve bedroom temperature."""
    config.requests += 1
    if location not in config.sensors:
        return ret_error()
    return ret_ok(data=functions.get_sensor_reading(config.sensors[location]))

#loft.run(server='paste', host='192.168.0.101', port=5000, reloader=True, quiet=False)
application = bottle.default_app()
