"""Agent.

Usage:
  agent -f <config-file>
  agent (-h | --help)

Options:
  -h --help     Show this screen.

"""
from docopt import docopt

import ConfigParser
import sys
import requests
import gevent
import json
import subprocess
import psutil
import time

arguments = docopt( __doc__, version='Agent 0.1' )

config = ConfigParser.ConfigParser()
config.read( arguments['<config-file>'] )

api_host = config.get( 'appbus', 'api_host' )
api_key = config.get( 'appbus', 'api_key' )

updates_push_url = 'http://%s/api/v0/server/software-updates/' % (api_host,)
metrics_push_url = 'http://%s/api/v0/server/metrics/' % (api_host,)

def push( push_url, _data ):
	data = {}
	data.update( _data )
	data['ts'] = time.time()
	data['server_api_key'] = api_key
	
	while True:
		try:
			return requests.put( push_url, data=json.dumps(data) )
		except requests.ConnectionError:
			print 'Could not push to', push_url, ' - retrying...'
			gevent.sleep( 60 )

def get_software_updates( ):
	check_script = '/usr/lib/update-notifier/apt-check'
	
	try:
		output = subprocess.check_output( check_script, stderr=subprocess.STDOUT )
	except subprocess.CalledProcessError:
		total, security = 0, 0
	except OSError:
		total, security = 0, 0
	else:
		total, security = [int(a) for a in output.split(';')]
	
	return { 'total': total, 'security': security }

def software_updates_pusher():
	while True:
		data = {'updates': get_software_updates()}
		r = push( updates_push_url, data )
		if r.status_code != 200:
			print r.content
		gevent.sleep( 60*60 )

def get_system_metrics( ):
	cpu_percent = psutil.cpu_percent( interval=None )
	memory_percent = psutil.virtual_memory( ).percent
	disk_percent = psutil.disk_usage('/').percent
	
	return {
		'cpu': cpu_percent,
		'memory': memory_percent,
		'disk': disk_percent,
	}

def metrics_pusher():
	get_system_metrics( )
	
	GRAB_FREQUENCY = (5*60)
	GRAB_POLL_SLEEP = (60)
	
	next_grab = time.time( )
	
	while True:
		next_grab += GRAB_FREQUENCY
		
		while time.time() < next_grab:
			gevent.sleep( GRAB_POLL_SLEEP )
		
		data = {'metrics': get_system_metrics()}
		r = push( metrics_push_url, data )
		if r.status_code != 200:
			print r.content

gevent.joinall( [gevent.spawn(software_updates_pusher), gevent.spawn(metrics_pusher)] )