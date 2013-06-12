"""AppBus Agent Metrics Service.

Usage:
  agent -f <config-file>
  agent (-h | --help)

Options:
  -h --help     Show this screen.

"""
from docopt import docopt

import gevent
import zmq.green as zmq

import psutil
import time

from conf import AppBusAgentConfig
from pollingService import PollingService

class MetricsService(PollingService):
	"""Regularly polls system metrics and forwards them to the pusher service."""
	
	def __init__( self, config ):
		super(MetricsService, self).__init__( config )
		
		self.poll_frequency = (5*60)
		self.poll_sleep = (60)
	
	def setup( self ):
		self.get_system_metrics( )

	def poll( self ):
		data = {
			'endpoint': 'server/metrics/',
			'payload': {
				'metrics': self.get_system_metrics()
			}
		}
		
		self.send_json( data )
		
	def get_system_metrics( self ):
		cpu_percent = psutil.cpu_percent( interval=None )
		memory_percent = psutil.virtual_memory( ).percent
		disk_percent = psutil.disk_usage('/').percent

		return {
			'cpu': cpu_percent,
			'memory': memory_percent,
			'disk': disk_percent,
		}

if __name__ == '__main__':
	arguments = docopt( __doc__, version='AppBus Agent Metrics Service 0.1' )
	
	config = AppBusAgentConfig( arguments )
	
	service = MetricsService( config )
	service.start( )
	service.join( )