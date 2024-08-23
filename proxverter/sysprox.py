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

    def get_prox_instance(self):
        plat = platform.system().lower()
        if plat == "windows":
            prox = WinProxy(self.ip_address, self.port)
        elif plat == "linux":
            prox = LinuxProxy(self.ip_address, self.port)
        elif plat == "macos" or plat == "darwin":
            prox = MacProxy(self.ip_address, self.port)
        else:
            raise OSError("Unable to determine the underlying operating system")

        return prox

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
