![banner](https://gistcdn.githack.com/kun-codes/238e08354c3aede326d34a9694627314/raw/6fcfcb7399ee70e4dc204c1168d1d2ea74b995f9/uniproxy-banner.svg)

<div align="center">
    <img alt="GitHub License" src="https://img.shields.io/github/license/kun-codes/Uniproxy">
    <a href="https://wakatime.com/badge/user/8585bb79-1d4a-4ee6-8234-62bc87ecba58/project/03ec9bf9-b700-4399-9af8-4c840209bb13"><img src="https://wakatime.com/badge/user/8585bb79-1d4a-4ee6-8234-62bc87ecba58/project/03ec9bf9-b700-4399-9af8-4c840209bb13.svg" alt="wakatime"></a>
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/uniproxy">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/uniproxy">
</div>

<h1 align="center">Uniproxy</h1>
<p align="center">Cross-platform python library to set system-wide proxy and proxy bypass domains.</p>

> [!IMPORTANT]
> Uniproxy doesn't provide a proxy server. It only sets the system-wide proxy settings.

## Features

- **Cross Platform:** Uniproxy is cross-platform and can be used on Windows, macOS and Linux.
- **System Wide Proxy:** Uniproxy can be used to set system-wide proxy for the host.
- **Bypassing Domains:** Uniproxy can be used to set bypass domains which don't go through the system-wide proxy.
- **Environment Variables:** Uniproxy can also set environment variables for the proxy.


## Installation

```bash
$ pip3 install uniproxy
```

## Getting Started

Install the package as mentioned above and import it.

### Proxy setup

```python
import uniproxy

prox = uniproxy.Uniproxy(ip="127.0.0.1", port=8081)  ## Create a uniproxy instance
prox.set_proxy()  ## Set system-wide proxy without changing the current proxy enabled state for the OS
prox.set_proxy_enabled(True)  ## Enable system-wide proxy
```

This will first edit the OS Settings to set the proxy and then enable the proxy.

```python
import uniproxy

prox = uniproxy.Uniproxy(ip="127.0.0.1", port=8081)  ## Create a uniproxy instance
prox.join()  ## Change
```

As an alternative, you can also use the above method to set the proxy and enable it directly.

### Bypass Domains

```python
import uniproxy

prox = uniproxy.Uniproxy(ip="127.0.0.1", port=8081)  ## Create a uniproxy instance
prox.set_bypass_domains(["www.google.com", "www.facebook.com"])  ## Set bypass domains
```

This will set the bypass domains for the proxy. The domains mentioned in the list will not pass through the proxy. Environment variables `no_proxy` and `NO_PROXY` will also be set.

### Turn off Proxy

```python
import uniproxy

prox = uniproxy.Uniproxy(ip="127.0.0.1", port=8081)  ## Create a uniproxy instance
prox.set_proxy_enabled(False)  ## Disable system-wide proxy
```

This will disable the system-wide proxy.

### Delete Proxy

```python
import uniproxy

prox = uniproxy.Uniproxy(ip="127.0.0.1", port=8081)  ## Create a uniproxy instance
prox.delete_proxy()  ## Delete the proxy settings
```

This will delete the proxy settings from the system and set them to OS defaults.

### Get Proxy Details

```python
import uniproxy

prox = uniproxy.Uniproxy(ip="127.0.0.1", port=8081)  ## Create a uniproxy instance
prox.join()
print(prox.get_proxy())  ## Get the proxy details
```

This will output the following (on Linux, KDE)

```
{
    "is_enable": True,
    "http": {"ip_address": "127.0.0.1", "port": "8081"},
    "https": {"ip_address": "127.0.0.1", "port": "8081"},
    "ftp": {"ip_address": "127.0.0.1", "port": "8081"},
}
```

### Get Bypass Domains

```python
import uniproxy

prox = uniproxy.Uniproxy(ip="127.0.0.1", port=8081)  ## Create a uniproxy instance
prox.set_bypass_domains(["www.google.com", "www.facebook.com"])  ## Set bypass domains
print(prox.get_bypass_domains())  ## Get bypass domains
```

This will output the following

```
['www.google.com', 'www.facebook.com']
```

### MacOS Specific Functionality

#### Get default network service

```python
import uniproxy

prox = uniproxy.Uniproxy(ip="127.0.0.1", port=8081)  ## Create a uniproxy instance
print(prox.proxy.get_default_network_service())  ## Get the default network service
```

This will output the following (depends on the system and current network configuration):

```
Wi-Fi
```

Default network service is determined by parsing the output of `route -n get default` command. If it fails for some reason the default network service is found out by parsing the output of `networksetup -listallnetworkservices` command and returning the first network service which is not disabled.

## Known Issues

- Uniproxy only works on SystemD based Linux systems.
- Uniproxy only supports KDE and GNOME desktop environments on Linux.

## Credits

- [hash3liZer/Proxverter](https://github.com/hash3liZer/Proxverter): for providing the initial base for the project.
- [zzzgydi/sysproxy-rs](https://github.com/zzzgydi/sysproxy-rs): for providing help with the macOS implementation.
- [Proxy Server page on Arch wiki](https://wiki.archlinux.org/title/Proxy_server#Environment_variables): for providing information on environment variables on linux.
