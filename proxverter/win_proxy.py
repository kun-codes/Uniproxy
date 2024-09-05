import winreg
import ctypes

class WinProxy:
    '''
    Refers to the windows version of system wide proxy. Refer to `Proxy` class for initializing system wide proxy.
    '''

    def __init__(self, ip_address, port):

        self.regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 0, winreg.KEY_ALL_ACCESS)
        self.internet_option_refresh = 37
        self.internet_option_settings_changed = 39
        self.internet_set_option = ctypes.windll.Wininet.InternetSetOptionW

        self.ip_address = ip_address
        self.port      = port

    def refresh(self):
        self.internet_set_option(0, self.internet_option_settings_changed, 0, 0)
        self.internet_set_option(0, self.internet_option_refresh, 0, 0)

    def set_key(self, name, value):
        try:
            _, reg_type = winreg.QueryValueEx(self.regkey, name)
            winreg.SetValueEx(self.regkey, name, 0, reg_type, value)
        except FileNotFoundError:
            winreg.SetValueEx(self.regkey, name, 0, winreg.REG_SZ, value)

    def set_proxy(self):
        try:
            #self.set_key('ProxyOverride', u'*.local;<local>')
            self.set_key('ProxyServer', u'%s:%i' % (self.ip_address, self.port))
            return True
        except IndexError:
            raise ValueError(f"Unable to find the registry path for proxy")
            return False

    def get_proxy(self):
        try:
            is_enable = self.get_enable()
            proxy_server = winreg.QueryValueEx(self.regkey, 'ProxyServer')[0]
            proxies = self.extract_proxies(proxy_server)
            return {
                "is_enable": is_enable,
                "http": proxies.get("http", {"ip_address": "", "port": ""}),
                "https": proxies.get("https", {"ip_address": "", "port": ""}),
                "ftp": proxies.get("ftp", {"ip_address": "", "port": ""})
            }
        except FileNotFoundError:
            return {
                "is_enable": False,
                "http": {"ip_address": "", "port": ""},
                "https": {"ip_address": "", "port": ""},
                "ftp": {"ip_address": "", "port": ""}
            }

    def extract_proxies(self, proxy_server):
        proxies = {}
        for proxy in proxy_server.split(';'):
            if '=' in proxy:
                protocol, address = proxy.split('=', 1)
                ip_address, port = address.split(':')
                proxies[protocol] = {"ip_address": ip_address, "port": port}
            else:  # in the case when no protocol is specified, it is used for http, https and ftp
                ip_address, port = proxy.split(':')
                proxies["http"] = {"ip_address": ip_address, "port": port}
                proxies["https"] = {"ip_address": ip_address, "port": port}
                proxies["ftp"] = {"ip_address": ip_address, "port": port}
        return proxies

    def set_enable(self, is_enable):
        self.set_key('ProxyEnable', 1 if is_enable else 0)
        self.refresh()

    def get_enable(self):
        try:
            return winreg.QueryValueEx(self.regkey, 'ProxyEnable')[0] == 1
        except FileNotFoundError:
            return False

    def set_bypass_domains(self, domains: list[str]):
        self.set_key('ProxyOverride', ';'.join(domains))
        self.refresh()

    def get_bypass_domains(self):
        try:
            return winreg.QueryValueEx(self.regkey, 'ProxyOverride')[0].split(';')
        except FileNotFoundError:
            return []

    def del_proxy(self):
        try:
            self.set_key('ProxyEnable', 0)
            self.set_key('ProxyServer', '')
            self.set_key('ProxyOverride', '<local>')
            self.refresh()
        except FileNotFoundError:
            pass

    def join(self):
        self.set_proxy()
        self.set_enable(True)
        self.refresh()
