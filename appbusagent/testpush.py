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

if __name__ == '__main__':
	arguments = docopt( __doc__, version='AppBus Agent Pusher 0.1' )
	
	config = AppBusAgentConfig( arguments )
	
	ctx = zmq.Context() # create a new context to kick the wheels
	sock = ctx.socket( zmq.PUSH )
	sock.connect( config.get_ipc_socket() )
	
	sock.send_json( { 'a': 'b' } )