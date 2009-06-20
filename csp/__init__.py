# import atexit, socket, SocketServer, sys, time

# try:
#     import cPickle as pickle # Faster pickle
# except ImportError:
#     import pickle

# # Multiprocessing libary -- name changed between versions.
# try: 
#     # Python version 2.5
#     if sys.version_info[:2] == (2,5): 
#         import processing
#     # Version 2.6 and above
#     else: import multiprocessing as processing
#     if sys.platform == 'win32':
#         import processing.reduction
# except ImportError, e:
#     print 'No library available for multiprocessing. Exiting now.'
#     sys.exit(1)
# from processing.managers import SyncManager

# try: # Python optimisation compiler
#     import psyco 
#     psyco.full()
# except ImportError:
#     print 'No available optimisation'

# from csp import _BUFFSIZE, _HOST, _CHANNEL_PORT,  _OTA_PORT, _VIS_PORT

# _IS_SECURE = False 	# Can't take this from csp module because it's

# class ChannelServer(SyncManager):
#     def __init__(self, address, authkey):
#         SyncManager.__init__(self, address, authkey)
# 	print 'Starting channel server...'
#         self.start()
#         print 'creating dict...'
#         self.channels = self.dict()
#         print 'Channel server started...'
#     def set_value(self, channel, obj):
#         self.channels[channel] = obj
#         return True
#     def get_value(self, channel):
#         try:
#             return self.channels[channel]
#         except KeyError, e:
#             return None
#     def clear_value(self, channel):
#         self.channels[channel] = None
#         return True

# class ChannelServerProxy(ChannelServer):
#     def __init__(self, address, authkey):
#         self.manager = ChannelServerProxy.fromAddress(address, authkey)
#         self.channels = self.manager.channels
#     def set_value(self, channel, obj):
#         self.channels[channel] = obj
#         return True
#     def get_value(self, channel):
#         try:
#             return self.channels[channel]
#         except KeyError, e:
#             return None
#     def clear_value(self, channel):
#         self.channels[channel] = None
#         return True

# if __name__ != '__main__':
# #    cs = ChannelServer((_HOST, _CHANNEL_SERVER), '')
# # Do nothing for now...
# 	pass


# #################################################################
# #
# # *** SCRATCH SPACE ***
# #
# ## The following will not work with Python2.5.2:
# #
# # class ChannelServer(object):
# #     """Store values passed along channels created on this host.
# #     """
# #     def __init__(self):
# #         self.names = {}
# #     def set_value(self, channel, obj):
# #         self.names[channel] = obj
# #         return
# #     def get_value(self, channel):
# #         try:
# #             return self.names[channel]
# #         except KeyError:
# #             return None
# #     def clear_value(self, channel):
# #         self.names[channel] = None
# #         return

# # class CSPChannelManager(BaseManager):
# #     def __init__(self):
# #         BaseManager.__init__(self)

# # CSPChannelManager.register('ChannelServer', ChannelServer)

# # if __name__ != '__main__':
# #     manager = CSPChannelManager(address=('', _CHANNEL_PORT), authkey=None)
# #     manager.get_server().serverForever()
    

