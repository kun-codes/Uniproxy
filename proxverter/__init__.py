import shutil
import os
import socket
import pathlib

## Package Imports
from . import sysprox as sprox

class Proxverter:
    '''
    The main Proxverter class that accepts creds, setup system wide caches and run proxy servers.
    '''

    def __init__(self, ip, port, sysprox=False):
        self.ip_address = ip
        self.port       = port
        self.sysprox    = sysprox
        self.proxy      = sprox.Proxy(self.ip_address, self.port)
        self.__check_connection()

        if self.sysprox:
            self.set_sysprox()

    def __check_connection(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(( self.ip_address, self.port ))
            s.close()
            return True
        except Exception as e:
            return False

    def __clear(self):
        try:
            shutil.rmtree(
                os.path.join(pathlib.Path.home(), ".proxy")
            )
        except FileNotFoundError:
            pass

    def set_sysprox(self):
        self.proxy.engage()

    def del_sysprox(self):
        self.proxy.cleanup()
