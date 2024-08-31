import shutil
import os
import socket
import pathlib
import platform

## Package Imports

if platform.system().lower() == "linux":
    from proxverter.linux_proxy import LinuxProxy
if platform.system().lower() == "macos" or platform.system().lower() == "darwin":
    from proxverter.mac_proxy import MacProxy
if platform.system().lower() == "windows":
    from proxverter.win_proxy import WinProxy

class Proxverter:
    '''
    The main Proxverter class that accepts creds, setup system wide caches and run proxy servers.
    '''

    def __init__(self, ip: str, port: int):
        self.ip_address = ip
        self.port       = port
        self.proxy      = self.__get_proxy_instance()
        if not self.__check_connection():
            raise ConnectionError("Unable to connect to the specified address")

    def __check_connection(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(( self.ip_address, self.port ))
            s.close()
            return True
        except Exception as e:
            print(e)
            return False

    def __get_proxy_instance(self):
        plat = platform.system().lower()
        if plat == "windows":
            return WinProxy(self.ip_address, self.port)
        elif plat == "linux":
            return LinuxProxy(self.ip_address, self.port)
        elif plat == "macos" or plat == "darwin":
            return MacProxy(self.ip_address, self.port)
        else:
            raise OSError("Unable to determine the underlying operating system")

    def __clear(self):
        try:
            shutil.rmtree(
                os.path.join(pathlib.Path.home(), ".proxy")
            )
        except FileNotFoundError:
            pass

    def join(self):
        self.proxy.join()

    def get_proxy(self):
        return self.proxy.get_proxy()

    def delete_proxy(self):
        self.proxy.del_proxy()

        if hasattr(self.proxy, 'refresh'):
            self.proxy.refresh()

    def set_proxy_enabled(self, enable: bool):
        self.proxy.set_enable(enable)

    def set_bypass_domains(self, domains: list[str]):
        self.proxy.set_bypass_domains(domains)

    def get_bypass_domains(self):
        return self.proxy.get_bypass_domains()

    def get_proxy_enabled(self):
        return self.proxy.get_enable()
