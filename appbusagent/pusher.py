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

if __name__ == '__main__':
	arguments = docopt( __doc__, version='AppBus Agent Pusher 0.1' )
	
	config = AppBusAgentConfig( arguments )
	
	pusher = RemotePusher( config )
	pusher.start()
	pusher.join()

"""
# server
print zmq.Context
ctx = zmq.Context( )
sock = ctx.socket( zmq.PUSH )
sock.bind( 'ipc:///tmp/zmqtest' )

spawn(sock.send_pyobj, ('this', 'is', 'a', 'python', 'tuple'))
spawn_later(1, sock.send_pyobj, {'hi': 1234})
spawn_later(2, sock.send_pyobj, ({'this': ['is a more complicated object', ':)']}, 42, 42, 42))
spawn_later(3, sock.send_pyobj, 'foobar')
spawn_later(4, sock.send_pyobj, 'quit')


# client
ctx = zmq.Context() # create a new context to kick the wheels
sock = ctx.socket(zmq.PULL)
sock.connect('ipc:///tmp/zmqtest')

def get_objs(sock):
    while True:
        o = sock.recv_pyobj()
        print 'received python object:', o
        if o == 'quit':
            print 'exiting.'
            break

def print_every(s, t=None):
    print s
    if t:
        spawn_later(t, print_every, s, t)

print_every('printing every half second', 0.5)
spawn(get_objs, sock).join()
"""