import ConfigParser
import os

class AppBusAgentConfig(object):
	def __init__( self, arguments ):
		self.config = ConfigParser.ConfigParser()
		self.config.read( arguments['<config-file>'] )
	
	def get( self, section, name ):
		return self.config.get( section, name )
	
	def get_ipc_socket( self ):
		return 'ipc://%s' % os.path.join( os.path.dirname(__file__), '../pusher.sock' )
