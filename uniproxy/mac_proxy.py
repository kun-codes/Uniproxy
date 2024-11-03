import subprocess
from contextlib import redirect_stdout

from uniproxy.shell_env_var import ShellEnvVar


class MacProxy:
    '''
    Refers to the macOS version of system-wide proxy. Refer to `Proxy` class for initializing system-wide proxy.
    '''

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    def set_proxy(self):
        network_services = self.get_network_services()
        network_service = None
        try:
            for network_service in network_services:
                self.set_http_proxy(network_service)
                self.set_https_proxy(network_service)

            if self.get_enable():
                shell_env_var = ShellEnvVar(self.ip_address, self.port, self.get_bypass_domains())
                shell_env_var.set_proxy_env_var()

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"failed to set proxy services for {network_service}: {e}")

    def del_proxy(self):
        network_services = self.get_network_services()
        network_service = None
        try:
            for network_service in network_services:
                subprocess.run(['networksetup', '-setwebproxy', network_service, "", str(0)], check=True)
                subprocess.run(['networksetup', '-setsecurewebproxy', network_service, "", str(0)], check=True)
                subprocess.run(['networksetup', '-setwebproxystate', network_service, 'off'], check=True)
                subprocess.run(['networksetup', '-setsecurewebproxystate', network_service, 'off'], check=True)

            self.set_bypass_domains(["*.local", "169.254/16"])

            shell_env_var = ShellEnvVar(self.ip_address, self.port, self.get_bypass_domains())
            shell_env_var.unset_proxy_env_var()
            shell_env_var.unset_bypass_domains_env_var()
        except subprocess.CalledProcessError:
            raise RuntimeError(f"failed to delete proxy services for {network_service}")

    def join(self):
        self.set_proxy()
        self.set_enable(True)

    def get_network_services(self):
        """
        Get the list of network services available on the macOS device
        """
        try:
            result = subprocess.run(['networksetup', '-listallnetworkservices'], capture_output=True, text=True, check=True)
            network_services = result.stdout.split('\n')
            network_services = [network_service.strip() for network_service in network_services if
                                network_service.strip() and "An asterisk" not in network_service]
            return network_services
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get network services: {e}")

    def set_enable(self, is_enable):
        network_services = self.get_network_services()
        network_service = None
        try:
            for network_service in network_services:
                if is_enable:
                    subprocess.run(['networksetup', '-setwebproxystate', network_service, 'on'], check=True)
                    subprocess.run(['networksetup', '-setsecurewebproxystate', network_service, 'on'], check=True)
                else:
                    subprocess.run(['networksetup', '-setwebproxystate', network_service, 'off'], check=True)
                    subprocess.run(['networksetup', '-setsecurewebproxystate', network_service, 'off'], check=True)

            shell_env_var = ShellEnvVar(self.ip_address, self.port, self.get_bypass_domains())
            if is_enable:
                shell_env_var.set_proxy_env_var()
                shell_env_var.set_bypass_domains_env_var()
            else:
                shell_env_var.unset_proxy_env_var()
                shell_env_var.unset_bypass_domains_env_var()

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to set proxy services for {network_service}: {e}")


    def set_http_proxy(self, network_service):
        try:
            http_proxy_state = self.get_http_proxy(network_service)
            is_enabled = http_proxy_state['enabled']

            subprocess.run(['networksetup', '-setwebproxy', network_service, self.ip_address, str(self.port)], check=True)

            # since networksetup -setwebproxy turns on the proxy too, we need to turn it off if it was off
            # this function doesn't change the state of the proxy if it was already on since it would be turned on
            # by the previous command

            if not is_enabled:
                subprocess.run(['networksetup', '-setwebproxystate', network_service, 'off'], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to set http proxy for {network_service}: {e}")

    def set_https_proxy(self, network_service):
        try:
            https_proxy_state = self.get_https_proxy(network_service)
            is_enabled = https_proxy_state['enabled']

            subprocess.run(['networksetup', '-setsecurewebproxy', network_service, self.ip_address, str(self.port)], check=True)

            # since networksetup -setsecurewebproxy turns on the proxy too, we need to turn it off if it was off
            # this function doesn't change the state of the proxy if it was already on since it would be turned on
            # by the previous command
            if not is_enabled:
                subprocess.run(['networksetup', '-setsecurewebproxystate', network_service, 'off'], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to set https proxy for {network_service}: {e}")

    def set_bypass_domains(self, domains: list[str], network_service=None):
        if network_service is None:
            network_services = self.get_network_services()
        else:
            network_services = [network_service]

        try:
            for service in network_services:
                subprocess.run(['networksetup', '-setproxybypassdomains', service] + domains, check=True)

            if self.get_enable():
                shell_env_var = ShellEnvVar(self.ip_address, self.port, domains)
                shell_env_var.set_bypass_domains_env_var()

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to set bypass domains for {network_service}: {e}")

    def get_bypass_domains(self, network_service=None):
        if network_service is None:
            network_service = self.get_default_network_service()
        try:
            result = subprocess.run(['networksetup', '-getproxybypassdomains', network_service], capture_output=True,
                                    text=True)

            result = result.stdout.split('\n')
            result = [domain for domain in result if domain.strip()]
            return result
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get bypass domains for {network_service}: {e}")

    def get_http_proxy(self, network_service):
        try:
            result = subprocess.run(['networksetup', '-getwebproxy', network_service], capture_output=True, text=True)
            output = result.stdout

            enabled = self.parse(output, 'Enabled:') == "Yes"
            server = self.parse(output, 'Server:')
            port = self.parse(output, 'Port:')

            return {
                'enabled': enabled,
                'ip_address': server,
                'port': port
            }
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get http proxy for {network_service}: {e}")

    def get_https_proxy(self, network_service):
        try:
            result = subprocess.run(['networksetup', '-getsecurewebproxy', network_service], capture_output=True, text=True)
            output = result.stdout

            enabled = self.parse(output, 'Enabled:') == "Yes"
            server = self.parse(output, 'Server:')
            port = self.parse(output, 'Port:')

            return {
                'enabled': enabled,
                'ip_address': server,
                'port': port
            }
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get https proxy for {network_service}: {e}")

    def get_enable(self):
        """
        Get if proxy is enabled or not. Only checks for default network service which is determined by
        get_default_network_service()
        """
        http_proxy = self.get_http_proxy(self.get_default_network_service())
        https_proxy = self.get_https_proxy(self.get_default_network_service())
        return http_proxy['enabled'] and https_proxy['enabled']

    def parse(self, output, key):
        for line in output.split('\n'):
            if line.strip().startswith(key):
                return line.split(':', 1)[1].strip()
        return None

    def get_default_network_device(self):
        """
        Get default network device by parsing the output of `route -n get default`. Returns None is machine is not
        connected to any network.
        """
        try:
            route_result = subprocess.run(['route','-n', 'get', 'default'], capture_output=True, text=True).stdout.strip()
            if not "route: writing to routing socket:" in route_result:  # happens when machine is not connected to any network
                for line in route_result.split('\n'):
                    if line.strip().startswith('interface:'):
                        return line.split(':', 1)[1].strip()
            else:
                return None  # return None if machine is not connected to any network

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get default network service: {e}")

    def get_default_network_service_by_ns(self):
        """
        Get default network service by parsing the output of `networksetup -listallnetworkservices`.
        Returns the first enabled network service. Returns None if no such network service is found.
        """
        try:
            result = subprocess.run(['networksetup', '-listallnetworkservices'], capture_output=True, text=True).stdout.strip()
            lines = result.split('\n')
            lines = [line for line in lines if line.strip()]
            if len(lines) > 1:  # above command returns nothing if there is no network service
                lines.pop(0)   # remove the first line which is "An asterisk (*) denotes that a network service is disabled."

            default_network_service = None

            for line in lines:
                if line.strip().startswith('*'):  # skip the deactivated network service
                    continue
                else:
                    default_network_service = line.strip()
                    break

            return default_network_service if default_network_service else None

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get default network service by network service: {e}")

    def get_network_service_name_by_network_device(self, device_name: str):
        """
        Returns the network service name by network device name.
        """
        try:
            result = subprocess.run(['networksetup', '-listallhardwareports'], capture_output=True, text=True)
            if result.returncode == 0:
                stdout = result.stdout
                blocks = stdout.split("Ethernet Address:")
                for block in blocks:
                    lines = block.split("\n")
                    hardware_port = None
                    device = None
                    for line in lines:
                        if line.strip().startswith("Hardware Port:"):
                            hardware_port = line.strip()[15:].strip()
                        if line.strip().startswith("Device:"):
                            device = line.strip()[8:].strip()
                    if device == device_name:
                        return hardware_port
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get network service name by network device ({device_name}): {e}")

    def get_default_network_service(self):
        """
        Returns the default network service determined by get_default_network_device(). If get_default_network_device()
        fails to find a default network device then get_default_network_service_by_ns() is used to find the default
        network service
        """
        default_network_device = self.get_default_network_device()
        if default_network_device is None:
            default_network_service = self.get_default_network_service_by_ns()
        else:
            default_network_service = self.get_network_service_name_by_network_device(default_network_device)

        if default_network_service is None:
            raise RuntimeError("Failed to get default network service. Check if there are any network services available.")

        return default_network_service

    def get_proxy(self):
        default_network_service = self.get_default_network_service()
        http_proxy = self.get_http_proxy(default_network_service)
        https_proxy = self.get_https_proxy(default_network_service)

        is_enable = http_proxy['enabled'] and https_proxy['enabled']

        return {
            "is_enable": is_enable,
            "http": {
                "ip_address": http_proxy['ip_address'],
                "port": http_proxy['port'],
            },
            "https": {
                "ip_address": https_proxy['ip_address'],
                "port": https_proxy['port'],
            }
        }
