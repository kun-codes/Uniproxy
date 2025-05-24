import shutil
import os
import socket
import pathlib
import platform
import warnings

## Package Imports

if platform.system().lower() == "linux":
    from uniproxy.linux_proxy import LinuxProxy
if platform.system().lower() == "macos" or platform.system().lower() == "darwin":
    from uniproxy.mac_proxy import MacProxy
if platform.system().lower() == "windows":
    from uniproxy.win_proxy import WinProxy

class Uniproxy:
    def __init__(self, ip: str, port: int):
        self._ip_address = ip
        self._port = port
        self.proxy = self.__get_proxy_instance()
        if not self.__check_connection():
            warnings.warn("Unable to bind to the specified IP and Port.\nPlease check if the IP and Port are correct\n and port is not already in use.")

    @property
    def ip_address(self):
        return self._ip_address

    @ip_address.setter
    def ip_address(self, value):
        self._ip_address = value
        if hasattr(self, 'proxy'):
            self.proxy.ip_address = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        if hasattr(self, 'proxy'):
            self.proxy.port = value

    def __check_connection(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(( self.ip_address, self.port ))
            s.close()
            return True
        except Exception:
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
        """
        Sets the proxy server in OS settings and enables the proxy.
        """
        self.proxy.join()

    def set_proxy(self):
        """
        Sets the proxy server in OS settings without enabling the proxy.
        """
        self.proxy.set_proxy()

        if hasattr(self.proxy, 'refresh'):
            self.proxy.refresh()

    def get_proxy(self):
        """
        Gets the proxy settings in a dict.
        """
        return self.proxy.get_proxy()

    def delete_proxy(self):
        """
        Disconnects from proxy and reset proxy settings to OS defaults.
        """
        self.proxy.del_proxy()

        if hasattr(self.proxy, 'refresh'):
            self.proxy.refresh()

    def set_proxy_enabled(self, enable: bool):
        """
        Sets the proxy to be enabled or disabled.
        """
        self.proxy.set_enable(enable)

    def set_bypass_domains(self, domains: list[str]):
        """
        Sets the domains which bypass the proxy.
        """
        self.proxy.set_bypass_domains(domains)

    def get_bypass_domains(self):
        """
        Gets the domains in a list which bypass the proxy.
        """
        return self.proxy.get_bypass_domains()

    def get_proxy_enabled(self):
        """
        Gets if the proxy is enabled or not.
        """
        return self.proxy.get_enable()
