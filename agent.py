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

arguments = docopt( __doc__, version='Agent 0.1' )

config = ConfigParser.ConfigParser()
config.read( arguments['<config-file>'] )

api_host = config.get( 'appbus', 'api_host' )
api_key = config.get( 'appbus', 'api_key' )

updates_push_url = 'http://%s/api/v0/server/software-updates/' % (api_host,)
metrics_push_url = 'http://%s/api/v0/server/metrics/' % (api_host,)

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
		data = json.dumps( {'server_api_key': api_key, 'updates': get_software_updates()} )
		r = requests.put( updates_push_url, data=data )
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
	
	while True:
		gevent.sleep( 5*60 )
		
		data = json.dumps( {'server_api_key': api_key, 'metrics': get_system_metrics()} )
		r = requests.put( metrics_push_url, data=data )
		if r.status_code != 200:
			print r.content

gevent.joinall( [gevent.spawn(software_updates_pusher), gevent.spawn(metrics_pusher)] )