import gevent
import zmq.green as zmq

import time

class PollingService(gevent.Greenlet):
	"""Regularly polls system metrics and forwards them to the pusher service."""
	
	def __init__( self, config ):
		self.config = config
		
		self.ctx = zmq.Context( )
		self.sock = self.ctx.socket( zmq.PUSH )
		self.sock.connect( self.config.get_ipc_socket() )
		
		super(PollingService, self).__init__( )
		
		self.poll_frequency = (5*60)
		self.poll_sleep = (60)
	
	def setup( self ):
		pass
	
	def poll( self ):
		pass
	
	def send_json( self, data ):
		self.sock.send_json( data )
	
	def _run( self ):
		self.setup( )

		next_grab = time.time( )
		
		while True:
			next_grab += self.poll_frequency

			while time.time() < next_grab:
				gevent.sleep( self.poll_sleep )

			self.poll( )
