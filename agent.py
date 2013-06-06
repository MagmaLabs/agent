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

arguments = docopt( __doc__, version='Agent 0.1' )

config = ConfigParser.ConfigParser()
config.read( arguments['<config-file>'] )

api_host = config.get( 'appbus', 'api_host' )
api_key = config.get( 'appbus', 'api_key' )

push_url = 'http://%s/api/v0/server/software-updates/' % (api_host,)

def get_software_updates( ):
	check_script = '/usr/lib/update-notifier/apt-check'
	
	try:
		output = subprocess.check_output( check_script )
	except subprocess.CalledProcessError:
		total, security = 0, 0
	except OSError:
		total, security = 0, 0
	else:
		total, security = [int(a) for a in output.split(';')]
	
	return { 'total': total, 'security': security }

def pusher():
	while True:
		data = json.dumps( {'server_api_key': api_key, 'updates': get_software_updates()} )
		r = requests.put( push_url, data=data )
		if r.status_code != 200:
			print r.content
		gevent.sleep( 60 )

gevent.joinall( [gevent.spawn(pusher)] )