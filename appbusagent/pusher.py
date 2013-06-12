"""AppBus Agent Pusher.

Usage:
  agent -f <config-file>
  agent (-h | --help)

Options:
  -h --help     Show this screen.

"""
from docopt import docopt

import gevent
import zmq.green as zmq

import requests
import json
import time

from conf import AppBusAgentConfig

class RemotePusher(gevent.Greenlet):
	"""Pulls from the local zmq bus and pushes to the remote API endpoint."""
	
	def __init__( self, config ):
		self.config = config
		
		self.ctx = zmq.Context( )
		self.sock = self.ctx.socket( zmq.PULL )
		self.sock.bind( self.config.get_ipc_socket() )
		
		super(RemotePusher, self).__init__( )
	
	def _run( self ):
		while True:
			o = self.sock.recv_json()
			print 'received:', o
			self.push( o )
	
	def push( self, descriptor ):
		api_host = self.config.get( 'appbus', 'api_host' )
		api_key = self.config.get( 'appbus', 'api_key' )
		
		push_url = 'http://%s/api/v0/%s' % (api_host, descriptor['endpoint'])
		
		data = {}
		data.update( descriptor['payload'] )
		data['ts'] = time.time()
		data['server_api_key'] = api_key

		while True:
			try:
				return requests.put( push_url, data=json.dumps(data) )
			except requests.ConnectionError:
				print 'Could not push to', push_url, ' - retrying...'
				gevent.sleep( 60 )

if __name__ == '__main__':
	arguments = docopt( __doc__, version='AppBus Agent Pusher 0.1' )
	
	config = AppBusAgentConfig( arguments )
	
	pusher = RemotePusher( config )
	pusher.start()
	pusher.join()
