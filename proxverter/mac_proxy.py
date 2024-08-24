import subprocess


class MacProxy:
    '''
    Refers to the macos version of system wide proxy. Refer to `Proxy` class for initializing system-wide proxy.
    '''

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    def set_proxy(self):
        network_services = self.get_network_services()
        for network_service in network_services:
            self.set_http_proxy(network_service)
            self.set_https_proxy(network_service)

    def del_proxy(self):
        network_services = self.get_network_services()
        for network_service in network_services:
            subprocess.run(['networksetup', '-setwebproxystate', network_service, 'off'])
            subprocess.run(['networksetup', '-setsecurewebproxystate', network_service, 'off'])

    def join(self):
        if not self.set_proxy():
            raise ValueError(f"Error setting proxy credentials")

    def get_network_services(self):
        # get the output of the command networksetup -listallnetworkservices
        result = subprocess.run(['networksetup', '-listallnetworkservices'], capture_output=True, text=True)
        network_services = result.stdout.split('\n')
        network_services = [network_service.strip() for network_service in network_services if
                            network_service.strip() and "An asterisk" not in network_service]
        return network_services

    def set_http_proxy(self, network_service):
        subprocess.run(['networksetup', '-setwebproxy', network_service, self.ip_address, self.port])
        subprocess.run(['networksetup', '-setwebproxystate', network_service, 'on'])

    def set_https_proxy(self, network_service):
        subprocess.run(['networksetup', '-setsecurewebproxy', network_service, self.ip_address, self.port])
        subprocess.run(['networksetup', '-setsecurewebproxystate', network_service, 'on'])

    def set_bypass_domains(self, network_service, domains: list):
        subprocess.run(['networksetup', '-setproxybypassdomains', network_service] + domains)

    def get_by_pass_domains(self, network_service):
        result = subprocess.run(['networksetup', '-getproxybypassdomains', network_service], capture_output=True,
                                text=True)

        result = result.stdout.split('\n')
        return result

    def get_http_proxy(self, network_service):
        result = subprocess.run(['networksetup', '-getwebproxy', network_service], capture_output=True, text=True)
        output = result.stdout

        enabled = self.parse(output, 'Enabled:') == "Yes"
        server = self.parse(output, 'Server:')
        port = self.parse(output, 'Port:')

        return {
            'enabled': enabled,
            'server': server,
            'port': port
        }

    def get_https_proxy(self, network_service):
        result = subprocess.run(['networksetup', '-getsecurewebproxy', network_service], capture_output=True, text=True)
        output = result.stdout

        enabled = self.parse(output, 'Enabled:') == "Yes"
        server = self.parse(output, 'Server:')
        port = self.parse(output, 'Port:')

        return {
            'enabled': enabled,
            'server': server,
            'port': port
        }

    def parse(self, output, key):
        for line in output.split('\n'):
            if line.strip().startswith(key):
                return line.split(':', 1)[1].strip()
        return None
