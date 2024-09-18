import os
import subprocess
from enum import Enum
from xdg import xdg_config_home
import re

BASH_RC = os.path.expanduser("~/.bashrc")
ZSH_RC = os.path.expanduser("~/.zshrc")
FISH_CONFIG = os.path.join(xdg_config_home(), "fish/config.fish")

class ShellsTypes(Enum):
    BASH = {
        "bin": "bash",
        "installed": False,
        "config": os.path.expanduser("~/.bashrc")
    }
    ZSH = {
        "bin": "zsh",
        "installed": False,
        "config": os.path.expanduser("~/.zshrc")
    }
    FISH = {
        "bin": "fish",
        "installed": False,
        "config": os.path.join(xdg_config_home(), "fish/config.fish")
    }

class ShellEnvVar:
    def __init__(self, ip_address, port, bypass_domains: list[str]):
        self.ip_address = ip_address
        self.port = port
        self.bypass_domains = bypass_domains

        self.shells = [
            {
                "name": shell.name,
                "bin": shell.value["bin"],
                "installed": self.command_exists(shell.value["bin"]),
                "config": shell.value["config"]
            }
            for shell in ShellsTypes
        ]

    def command_exists(self, command):
        return subprocess.call(["which", command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


    def set_proxy_env_var(self):
        """
        Sets the proxy environment variables in supported shell configuration files
        """
        self.unset_proxy_env_var()
        for shell in self.shells:
            if not shell["installed"]:
                continue

            shell_rc = shell["config"]
            if not os.path.exists(shell_rc):
                open(shell_rc, 'w').close()

            if shell["name"] in ["BASH", "ZSH"]:
                with open(shell_rc, 'a') as f:
                    f.write(f'export http_proxy="http://{self.ip_address}:{self.port}/"\n')
                    f.write(f'export HTTP_PROXY="http://{self.ip_address}:{self.port}/"\n')
                    f.write(f'export https_proxy="http://{self.ip_address}:{self.port}/"\n')
                    f.write(f'export HTTPS_PROXY="http://{self.ip_address}:{self.port}/"\n')
                    f.write(f'export ftp_proxy="ftp://{self.ip_address}:{self.port}/"\n')
                    f.write(f'export FTP_PROXY="ftp://{self.ip_address}:{self.port}/"\n')
                    f.write(f'export rsync_proxy="rsync://{self.ip_address}:{self.port}/"\n')
                    f.write(f'export RSYNC_PROXY="rsync://{self.ip_address}:{self.port}/"\n')

            elif shell["name"] == "FISH":
                with open(shell_rc, 'a') as f:
                    f.write(f'set -x http_proxy "http://{self.ip_address}:{self.port}/"\n')
                    f.write(f'set -x HTTP_PROXY "http://{self.ip_address}:{self.port}/"\n')
                    f.write(f'set -x https_proxy "http://{self.ip_address}:{self.port}/"\n')
                    f.write(f'set -x HTTPS_PROXY "http://{self.ip_address}:{self.port}/"\n')
                    f.write(f'set -x ftp_proxy "ftp://{self.ip_address}:{self.port}/"\n')
                    f.write(f'set -x FTP_PROXY "ftp://{self.ip_address}:{self.port}/"\n')
                    f.write(f'set -x rsync_proxy "rsync://{self.ip_address}:{self.port}/"\n')
                    f.write(f'set -x RSYNC_PROXY "rsync://{self.ip_address}:{self.port}/"\n')

    def unset_proxy_env_var(self):
        """
        Unsets the proxy environment variables in supported shell configuration files
        """
        for shell in self.shells:
            if not shell["installed"]:
                continue

            shell_rc = shell["config"]
            if not os.path.exists(shell_rc):
                continue

            with open(shell_rc, 'r') as f:
                lines = f.readlines()

            proxy_vars = [
                "http_proxy",
                "HTTP_PROXY",
                "https_proxy",
                "HTTPS_PROXY",
                "ftp_proxy",
                "FTP_PROXY",
                "rsync_proxy",
                "RSYNC_PROXY"
            ]

            proxy_patterns_bash_zsh = [re.compile(rf'export {var}\=.*') for var in proxy_vars]
            proxy_patterns_fish = [re.compile(rf'set -x {var} .*') for var in proxy_vars]

            if shell["name"] in ["BASH", "ZSH"]:
                self.remove_matching_lines(lines, proxy_patterns_bash_zsh, shell_rc)
            elif shell["name"] == "FISH":
                self.remove_matching_lines(lines, proxy_patterns_fish, shell_rc)

    def remove_matching_lines(self, lines, patterns, shell_rc):
        try:
            with open(shell_rc, 'w') as f:
                for line in lines:
                    if not any(pattern.match(line) for pattern in patterns):
                        f.write(line)
        except FileNotFoundError:
            pass

    def set_bypass_domains_env_var(self):
        """
        Sets the no_proxy and NO_PROXY environment variables in supported shell configuration
        """
        self.unset_bypass_domains_env_var()
        for shell in self.shells:
            if not shell["installed"]:
                continue

            shell_rc = shell["config"]
            if not os.path.exists(shell_rc):
                open(shell_rc, 'w').close()

            bypass_domains_str = ",".join(self.bypass_domains)

            if shell["name"] in ["BASH", "ZSH"]:
                with open(shell_rc, 'a') as f:
                    f.write(f'export no_proxy="{bypass_domains_str}"\n')
                    f.write(f'export NO_PROXY="{bypass_domains_str}"\n')
            elif shell["name"] == "FISH":
                with open(shell_rc, 'a') as f:
                    f.write(f'set -x no_proxy "{bypass_domains_str}"\n')
                    f.write(f'set -x NO_PROXY "{bypass_domains_str}"\n')

    def unset_bypass_domains_env_var(self):
        """
        Unsets the no_proxy and NO_PROXY environment variables in supported shell configuration
        """
        for shell in self.shells:
            if not shell["installed"]:
                continue

            shell_rc = shell["config"]
            if not os.path.exists(shell_rc):
                continue

            with open(shell_rc, 'r') as f:
                lines = f.readlines()

            bypass_vars = [
                "no_proxy",
                "NO_PROXY"
            ]

            bypass_patterns_bash_zsh = [re.compile(rf'export {var}\=.*') for var in bypass_vars]
            bypass_patterns_fish = [re.compile(rf'set -x {var} .*') for var in bypass_vars]

            if shell["name"] in ["BASH", "ZSH"]:
                self.remove_matching_lines(lines, bypass_patterns_bash_zsh, shell_rc)
            elif shell["name"] == "FISH":
                self.remove_matching_lines(lines, bypass_patterns_fish, shell_rc)
