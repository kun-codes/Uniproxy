import platform

from proxverter.linux_proxy import LinuxProxy
from proxverter.mac_proxy import MacProxy
from proxverter.win_proxy import WinProxy


class Proxy:

    ## Gets necessary information and kill mitmproxy if already running
    def __init__(self, ip_address, port):
        '''
            Accepts two arguments:

            ip_address: The IP address for system wide proxy
            port: The port for system wide proxy
        '''
        self.ip_address = ip_address
        self.port = port
        self._prox_instance = None

    def get_prox_instance(self):
        if self._prox_instance is None:
            plat = platform.system().lower()
            if plat == "windows":
                self._prox_instance = WinProxy(self.ip_address, self.port)
            elif plat == "linux":
                self._prox_instance = LinuxProxy(self.ip_address, self.port)
            elif plat == "macos" or plat == "darwin":
                self._prox_instance = MacProxy(self.ip_address, self.port)
            else:
                raise OSError("Unable to determine the underlying operating system")
        return self._prox_instance

    def engage(self):
        '''
            Setup system wide proxy.
        '''

        prox = self.get_prox_instance()
        prox.join()

    def cleanup(self):
        '''
            Removes system wide proxy
        '''

        prox = self.get_prox_instance()
        prox.del_proxy()

        if hasattr(prox, 'refresh'):
            prox.refresh()
