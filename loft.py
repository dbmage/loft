#!/usr/bin/python
from bottle import route, run
import sys
import os
import json
import socket
sys.path.append('/usr/sbin/loft/bottle/lib')
from functions import *

requests = 0

@route('/')
def FUNCTION():
    pid = os.getpid()
    cpu = getcpu()
    (usedram, totalram, freeram, rampercent) = getram()
    on = geton()
    off = getoff()
    myapproutes = "<br>".join(getAllRoutes(os.path.realpath(__file__)))
    print myapproutes
    return '<h2>Online  <img src="http://192.168.0.2/img/online.png" width="20px"></h2>\
        <h3>Requests processed: ' + str(requests) + '<h3>\
	    <br>\
	    <h3>Process ID: ' + str(pid) + ' </h3>\
	    <h3>CPU: ' + str(cpu) + '</h3>\
	    <h3>RAM: ' + str(usedram) + ' / ' + str(totalram) + ' (' + str(rampercent) + '%)</h3>\
	    <hr>\
	    <h3>Relays</h3>\
	    <h3>On:  ' + str(on) + '</h3>\
	    <h3>Off: ' + str(off) + '</h3>\
        <h3>Available routes:</h3>\
        <h3>' + myapproutes + '</h3>\
	    <!--<iframe src="http://192.168.0.101/" width="80%" height="80%">-->'

@route('/devquery')
def FUNCTION():
    global requests
    requests += 1
    return socket.gethostname()


@route('/flip/<relay>')
def FUNCTION(relay):
    global requests
    requests += 1
    returned = fliprelay(relay)
    return str(returned)

@route('/control/<operation>/<relay>')
def FUNCTION(relay):
    global requests
    requests += 1
    returned = forcerelay(operation, relay)
    if returned == 0:
        return "Done"
    else:
        return "Failed"


@route('/off')
def FUNCTION():
    global requests
    requests += 1
    returned = forcerelays("off")
    if returned == 0:
        return "Done"
    else:
        return "Failed"


@route('/on')
def FUNCTION():
    global requests
    requests += 1
    returned = forcerelays("on")
    if returned == 0:
        return "Done"
    else:
        return "Failed"


@route('/timed/<relay>/<duration>')
def FUNCTION(relay, duration):
    global requests
    requests += 1
    returned = timerelay(relay, duration)
    if returned == 0:
        return "Done"
    else:
        return "Failed"


@route('/getstate/<relay>')
def FUNCTION(relay):
    global requests
    requests += 1
    state = getstate(relay)
    return str(state)

@route('/getinfo/<relay>')
def FUNCTION(relay):
    global requests
    requests += 1
    return json.dumps(getinfo(relay))

@route('/getallinfo')
def FUNCTION():
    global requests
    requests += 1
    return json.dumps(getallinfo())

@route('/getallstates')
def FUNCTION():
    global requests
    requests += 1
    states = getallstates()
    print states
    states = json.dumps(states)
    return states

@route('/getlevel/<bucket>')
def FUNCTION(bucket):
    global requests
    requests += 1
    if bucket not in cfg.setup['buckets']:
        return "%s not found" % bucket
    
    level = getbucketlevels(cfg.setup['buckets'][bucket]['trig'], cfg.setup['buckets'][bucket]['echo'])
    return level

@route('/getlevels/')
def FUNCTION():
    global requests
    requests += 1
    levels = {}
    levels['left'] = getbucketlevels(cfg.setup['buckets']['left']['trig'], cfg.setup['buckets']['left']['echo'])
    levels['right'] = getbucketlevels(cfg.setup['buckets']['right']['trig'], cfg.setup['buckets']['right']['echo'])
    return json.dumps(levels)

@route('/getcylindertemps/')
def FUNCTION():
    global requests
    requests += 1
    temps = getCylinderTemps()
    return json.dumps(temps)

@route('/getbuckettemps/')
def FUNCTION():
    global requests
    requests += 1
    temp1 = getSensorReading(cfg.setup['sensors']['bucket1'])
    temp2 = getSensorReading(cfg.setup['sensors']['bucket2'])
    temps = (temp1, temp2)
    return json.dumps(temps)


run(host='192.168.0.101', port=5000, debug=True, reloader=True)
