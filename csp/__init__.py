# import socket
# import SocketServer
# import sys
# import time

# try:
#     import cPickle as pickle # Faster pickle
# except ImportError:
#     import pickle

# # Multiprocessing libary -- name changed between versions.
# try:
#     # Version 2.6 and above
#     import multiprocessing as processing
#     if sys.platform == 'win32':
#         import processing.reduction
# except ImportError:
#     raise ImportError('No library available for multiprocessing.\n'+
#                       'csp.cspprocess is only compatible with Python 2. 6 and above.')

# try: # Python optimisation compiler
#     import psyco 
#     psyco.full()
# except ImportError:
#     print 'No available optimisation'

# from csp.cspprocess import _BUFFSIZE, _HOST, _CHANNEL_PORT, _makeDigest

# _IS_SECURE = False 	# Can't take this from csp module because it's
#                         # wrapped in an if/else block.

# channels = []

# class CSPHandler(SocketServer.BaseRequestHandler):
    
#     def setup(self):
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#     def handle(self):
#         try:
#             global channels, IS_SECURE
#             data = self.request[0].strip()
#             self.sock.sendto(data, self.client_address)
#             return
#         except Exception:
#             pass

#     def parse(self, data):
#         """Parse a CSP event and return channel name and event data.
#         UNUSED
#         """
#         if data is None or data == '':
#             return None, None
#         header = data[:data.find('\n')]
#         if _IS_SECURE:
#             addr, digest = header.split(';')
#         else:
#             addr = header
#         obj = pickle.loads(data[data.find('\n')+1:])
#         return addr, obj

#     def marshal(self, addr, obj):
#         """Marshall a channel name and event data for sending.
#         UNUSED.
#         """
#         jam = pickle.dumps(obj, protocol=1)
#         if _IS_SECURE:
#             digest = _makeDigest(jam)
#             message = addr + ';' + digest + '\n' + jam + '\n'
#         else:
#             message = addr + '\n' + jam + '\n'
#         return message        


# def server():
#     """Create and start only one channel server."""
#     server = SocketServer.UDPServer((_HOST, _CHANNEL_PORT), CSPHandler)
#     try:
#         server.serve_forever()
#     except KeyboardInterrupt:
#         return


# class Server(processing.Process):
    
#     def __init__(self, serverfunc, server):
#         super(Server, self).__init__(target=serverfunc, args=(server,))
#         return

#     def run(self):
#         try:
#             self._target(*self._args, **self._kwargs)
#         except KeyboardInterrupt:
#             if self._popen:
#                 self.terminate()
#                 time.sleep(1)
#             print _notice('CSP channel server closed.')
#         return

# ### Process pool of servers

# _notice  = lambda s: '*** %s ***' % s

# def myserve(server):
#     try:
#         server.serve_forever()
#     except KeyboardInterrupt:
#         pass

# def runpool(numprocs):
#     try:
#         server = SocketServer.UDPServer((_HOST, _CHANNEL_PORT), CSPHandler)
#         for i in xrange(numprocs):
#             p = Server(myserve, server)
#             p.start()
#             ppid = str(p.getPid())
#             print _notice('Starting CSP channel server in process ' + ppid)
#     except KeyboardInterrupt:
#         pass


# def _saynothing(*args, **kwargs):
#     try:
#         return
#     except Exception:
#         return

# if __name__ == '__main__':
#     processing.freezeSupport()
#     print _notice('Starting CSP channel server')
#     server()
# else:
#     try:
#         sys.excepthook = _saynothing
#         runpool(10)
#     except KeyboardInterrupt:
#         pass
