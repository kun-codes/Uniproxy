class MacProxy:
    '''
    Refers to the macos version of system wide proxy. Refer to `Proxy` class for initializing system wide proxy.
    '''

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port       = port

    def join(self):
        pass
