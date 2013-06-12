"""AppBus Agent Updates Service.

Usage:
  agent -f <config-file>
  agent (-h | --help)

Options:
  -h --help     Show this screen.

"""
from docopt import docopt

import gevent
import zmq.green as zmq

import subprocess
import time

from conf import AppBusAgentConfig
from pollingService import PollingService

class UpdatesService(PollingService):
	"""Regularly polls system software updates and forwards them to the pusher service."""
	
	def __init__( self, config ):
		super(UpdatesService, self).__init__( config )
		
		self.poll_frequency = (60*60)
		self.poll_sleep = (5*60)
	
	def setup( self ):
		self.poll( ) # do the first poll at setup, instead of after the poll frequency
	
	def poll( self ):
		data = {
			'endpoint': 'server/software-updates/',
			'payload': {
				'updates': self.get_software_updates()
			}
		}
		
		self.send_json( data )
		
	def get_software_updates( self ):
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

if __name__ == '__main__':
	arguments = docopt( __doc__, version='AppBus Agent Updates Service 0.1' )
	
	config = AppBusAgentConfig( arguments )
	
	service = UpdatesService( config )
	service.start( )
	service.join( )