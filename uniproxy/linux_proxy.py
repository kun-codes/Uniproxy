import os
import subprocess
import re
import ast
from xdg import xdg_config_home


class LinuxProxy:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

        self.__is_gnome = self.__is_gnome()
        self.__is_kde = self.__is_kde()

        if not self.__is_gnome and not self.__is_kde:
            raise OSError("This library requires GNOME or KDE desktop environment")

    def __is_gnome(self):
        return os.environ.get("XDG_CURRENT_DESKTOP", "").lower() == "gnome"

    def __is_kde(self):
        return os.environ.get("XDG_CURRENT_DESKTOP", "").lower() == "kde"

    def __get_kde_command(self, command):
        kde_version = os.environ.get("KDE_SESSION_VERSION", "5")
        return f"{command}{kde_version}"

    def set_proxy(self):
        if self.__is_kde:
            self.__set_kde_proxy()
        if self.__is_gnome or self.__is_kde:
            self.__set_gnome_proxy()

        if self.get_enable():
            self.set_proxy_env_var()

    def set_enable(self, is_enable):
        if self.__is_kde:
            kde_command = self.__get_kde_command("kwriteconfig")
            subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "ProxyType", "1" if is_enable else "0"])
        if self.__is_gnome or self.__is_kde:
            subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "manual" if is_enable else "none"])

        if is_enable:
            self.set_proxy_env_var()
            self.set_bypass_domains_env_var()
        else:
            self.unset_proxy_env_var()
            self.unset_bypass_domains_env_var()

    def __set_kde_proxy(self):
        kde_command = self.__get_kde_command("kwriteconfig")

        subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "httpProxy", f"http://{self.ip_address} {self.port}"])
        subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "httpsProxy", f"http://{self.ip_address} {self.port}"])
        subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "ftpProxy", f"ftp://{self.ip_address} {self.port}"])

    def __set_gnome_proxy(self):
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "host", self.ip_address])
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "port", str(self.port)])
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.https", "host", self.ip_address])
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.https", "port", str(self.port)])
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.ftp", "host", self.ip_address])
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.ftp", "port", str(self.port)])

    def set_bypass_domains(self, domains: list[str]):
        if self.__is_kde:
            kde_command = self.__get_kde_command("kwriteconfig")
            subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "NoProxyFor", ','.join(domains)])
        if self.__is_gnome or self.__is_kde:
            subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "ignore-hosts", self.format_domains(domains)])

        if self.get_enable():
            self.set_bypass_domains_env_var()

    def get_proxy(self):
        is_enable = self.get_enable()
        if self.__is_kde:
            kde_proxy = self.__get_kde_proxy()
            return {"is_enable": is_enable, **kde_proxy}
        elif self.__is_gnome:
            gnome_proxy = self.__get_gnome_proxy()
            return {"is_enable": is_enable, **gnome_proxy}

    def get_enable(self):
        if self.__is_kde:
            kde_command = self.__get_kde_command("kreadconfig")
            output = subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "ProxyType"], capture_output=True, text=True)
            return output.stdout.strip() == "1"
        elif self.__is_gnome:
            output = subprocess.run(["gsettings", "get", "org.gnome.system.proxy", "mode"], capture_output=True, text=True)
            return output.stdout.strip() == "manual"

    def __get_kde_proxy(self):
        kde_command = self.__get_kde_command("kreadconfig")

        http_proxy = subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "httpProxy"], capture_output=True, text=True).stdout.strip()
        https_proxy = subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "httpsProxy"], capture_output=True, text=True).stdout.strip()
        ftp_proxy = subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "ftpProxy"], capture_output=True, text=True).stdout.strip()

        http_proxy_ip_address, http_proxy_port = self.extract_ip_and_port(http_proxy)
        https_proxy_ip_address, https_proxy_port = self.extract_ip_and_port(https_proxy)
        ftp_proxy_ip_address, ftp_proxy_port = self.extract_ip_and_port(ftp_proxy)

        return {
            "http": {
                "ip_address": http_proxy_ip_address,
                "port": http_proxy_port
            },
            "https": {
                "ip_address": https_proxy_ip_address,
                "port": https_proxy_port
            },
            "ftp": {
                "ip_address": ftp_proxy_ip_address,
                "port": ftp_proxy_port
            }
        }

    def __get_gnome_proxy(self):
        http_proxy_ip_address = subprocess.run(["gsettings", "get", "org.gnome.system.proxy.http", "host"], capture_output=True, text=True).stdout.strip()
        http_proxy_port = subprocess.run(["gsettings", "get", "org.gnome.system.proxy.http", "port"], capture_output=True, text=True).stdout.strip()
        https_proxy_ip_address = subprocess.run(["gsettings", "get", "org.gnome.system.proxy.https", "host"], capture_output=True, text=True).stdout.strip()
        https_proxy_port = subprocess.run(["gsettings", "get", "org.gnome.system.proxy.https", "port"], capture_output=True, text=True).stdout.strip()
        ftp_proxy_ip_address = subprocess.run(["gsettings", "get", "org.gnome.system.proxy.ftp", "host"], capture_output=True, text=True).stdout.strip()
        ftp_proxy_port = subprocess.run(["gsettings", "get", "org.gnome.system.proxy.ftp", "port"], capture_output=True, text=True).stdout.strip()

        return {
            "http": {
                "ip_address": http_proxy_ip_address,
                "port": http_proxy_port
            },
            "https": {
                "ip_address": https_proxy_ip_address,
                "port": https_proxy_port
            },
            "ftp": {
                "ip_address": ftp_proxy_ip_address,
                "port": ftp_proxy_port
            }
        }

    def get_bypass_domains(self):
        if self.__is_kde:
            kde_command = self.__get_kde_command("kreadconfig")
            output = subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "NoProxyFor"], capture_output=True, text=True)
            output = output.stdout.strip()
            bypass_domains = output.split(",") if output else []
            return bypass_domains
        elif self.__is_gnome:
            output = subprocess.run(["gsettings", "get", "org.gnome.system.proxy", "ignore-hosts"], capture_output=True, text=True)
            output = output.stdout.strip()
            return ast.literal_eval(output)

    def extract_ip_and_port(self, proxy):
        match = re.match(r'(http|https|ftp)://([\d\.]+)\s+(\d+)', proxy)
        if match:
            ip_address = match.group(2)
            port = match.group(3)
            return ip_address, port
        return None, None

    def format_domains(self, domains):
        formatted_domains = [f"'{domain}'" for domain in domains]
        return f"[{', '.join(formatted_domains)}]"

    def join(self):
        self.set_proxy()
        self.set_enable(True)

    def del_proxy(self):
        if self.__is_kde:
            kde_command = self.__get_kde_command("kwriteconfig")
            try:
                subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "ProxyType", "0"], check=True)
                subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "httpProxy", ""], check=True)
                subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "httpsProxy", ""], check=True)
                subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "ftpProxy", ""], check=True)
                subprocess.run([kde_command, "--file", "kioslaverc", "--group", "Proxy Settings", "--key", "NoProxyFor", "localhost,127.0.0.0/8,::1"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error deleting proxy: {e}")
        if self.__is_gnome or self.__is_kde:
            try:
                subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "none"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy.http", "host"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy.http", "port"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy.https", "host"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy.https", "port"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy.ftp", "host"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy.ftp", "port"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy", "ignore-hosts"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error deleting proxy: {e}")

        self.unset_proxy_env_var()
        self.unset_bypass_domains_env_var()

    def set_proxy_env_var(self):
        """
        Sets the proxy environment variables. Only works on Systemd based systems.
        """
        xdg_config_home_path = xdg_config_home()
        env_file_path = os.path.join(xdg_config_home_path, "environment.d", "01-proxy.conf")

        self.unset_proxy_env_var()

        with open(env_file_path, "w") as f:
            # https://www.freedesktop.org/software/systemd/man/latest/environment.d.html
            f.write(f"http_proxy=http://{self.ip_address}:{self.port}\n")
            f.write(f"https_proxy=http://{self.ip_address}:{self.port}\n")
            f.write(f"ftp_proxy=ftp://{self.ip_address}:{self.port}\n")
            f.write(f"rsync_proxy=rsync://{self.ip_address}:{self.port}\n")
            f.write(f"HTTP_PROXY=http://{self.ip_address}:{self.port}\n")
            f.write(f"HTTPS_PROXY=http://{self.ip_address}:{self.port}\n")
            f.write(f"FTP_PROXY=ftp://{self.ip_address}:{self.port}\n")
            f.write(f"RSYNC_PROXY=rsync://{self.ip_address}:{self.port}\n")

        self.refresh_env_var()

    def unset_proxy_env_var(self):
        xdg_config_home_path = xdg_config_home()
        env_file_path = os.path.join(xdg_config_home_path, "environment.d", "01-proxy.conf")

        try:
            os.remove(env_file_path)
        except FileNotFoundError:
            pass

        self.refresh_env_var()

    def set_bypass_domains_env_var(self):
        """
        Sets the domains which bypass the proxy. Only works on Systemd based systems.
        """
        xdg_config_home_path = xdg_config_home()
        env_file_path = os.path.join(xdg_config_home_path, "environment.d", "02-bypass-domains.conf")

        self.unset_bypass_domains_env_var()

        with open(env_file_path, "a") as f:
            # https://www.freedesktop.org/software/systemd/man/latest/environment.d.html
            f.write(f"no_proxy={','.join(self.get_bypass_domains())}\n")
            f.write(f"NO_PROXY={','.join(self.get_bypass_domains())}\n")

        self.refresh_env_var()

    def unset_bypass_domains_env_var(self):
        xdg_config_home_path = xdg_config_home()
        env_file_path = os.path.join(xdg_config_home_path, "environment.d", "02-bypass-domains.conf")

        try:
            os.remove(env_file_path)
        except FileNotFoundError:
            pass

        self.refresh_env_var()

    def refresh_env_var(self):
        try:
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error refreshing environment variable: {e}")

