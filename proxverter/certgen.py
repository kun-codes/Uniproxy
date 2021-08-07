from OpenSSL import crypto, SSL
import OpenSSL
import random
import re
import os
import platform
import subprocess

class Generator:

    def __init__(self, email=None, country=None, province=None, locality=None, organization=None, unit=None, commonname=None):
        self.email   = email
        self.country = country
        self.province = province
        self.locality = locality
        self.organization = organization
        self.unit     = unit
        self.commonname = commonname or "example.com"
        self.serial_number = random.getrandbits(64)
        self.valid_start = 0
        self.valid_end   = 10*365*24*60*60

    def generate(self):
        self.cert = crypto.X509()
        self.key = crypto.PKey()
        self.key.generate_key(crypto.TYPE_RSA, 2048)
        if self.country:
            self.cert.get_subject().C = self.country
        if self.province:
            self.cert.get_subject().ST = self.province
        if self.locality:
            self.cert.get_subject().L = self.locality
        if self.organization:
            self.cert.get_subject().O = self.organization
        if self.unit:
            self.cert.get_subject().OU = self.unit
        self.cert.get_subject().CN = self.commonname
        if self.email:
            self.cert.get_subject().emailAddress = self.email
        self.cert.set_serial_number(self.serial_number)
        self.cert.gmtime_adj_notBefore(self.valid_start)
        self.cert.gmtime_adj_notAfter(self.valid_end)
        self.cert.set_issuer(self.cert.get_subject())
        self.cert.set_pubkey(self.key)
        self.cert.sign(self.key, 'sha256')

    def gen_key(self, key_file):
        key_file = open(key_file, 'wt')
        try:
            key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, self.key).decode("utf-8"))
        except TypeError:
            key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, self.key))
        key_file.close()

    def gen_cert(self, cert_file):
        cert_file = open(cert_file, 'wt')
        try:
            cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, self.cert).decode("utf-8"))
        except TypeError:
            cert_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, self.key))
        cert_file.close()

    def gen_pfx(self, pfx_file):
        p12 = OpenSSL.crypto.PKCS12()
        p12.set_privatekey( self.key )
        p12.set_certificate( self.cert )

        pfx_file = open(pfx_file, 'wb')
        pfx_file.write(p12.export())
        pfx_file.close()

class Importer:

    def __init__(self, home_paths):
        self.home_paths = home_paths

        if not os.path.isfile(self.home_paths['privname']):
            raise FileNotFoundError("No private key file was found in home directory. It has either been modified or deleted. ")

        if not os.path.isfile(self.home_paths['certname']):
            raise FileNotFoundError("No cert file was found in home directory. It has either been modified or deleted. ")

        if not os.path.isfile(self.home_paths['pfxname']):
            raise FileNotFoundError("No pfx file was found in home directory. It has either been modified or deleted. ")

    def __import_windows(self):
        import ctypes

        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not is_admin:
            raise PermissionError("Importing certificate requires admin privileges")

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        comm = subprocess.check_output(
            'powershell.exe "Get-PfxCertificate -FilePath {}"'.format(self.home_paths['pfxname']),
            shell=True,
            startupinfo=startupinfo,
            stdin=subprocess.PIPE
        )

        thumbprint = comm.split(b"\r\n")[3].split(b" ")[0].decode()

        comm = subprocess.check_output(
            'powershell.exe "Test-Path (Join-Path Cert:\LocalMachine\Root\ {})"'.format(thumbprint),
            shell=True,
            startupinfo=startupinfo,
            stdin=subprocess.PIPE
        )

        if comm.strip() == b"False":
            comm = subprocess.call(
                'powershell.exe "Import-PfxCertificate -FilePath \'{}\' -CertStoreLocation cert:\LocalMachine\Root\"'.format(self.home_paths['pfxname']),
                shell=True,
                startupinfo=startupinfo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            if comm:
                raise SystemError("Error while importing certificate ")

            return 0
        else:
            return 1

    def cimport(self):
        plat = platform.system().lower()
        if plat == "windows":
            return self.__import_windows()
        elif plat == "linux":
            pass
        elif plat == "macos":
            pass
        else:
            raise OSError("Unable to determine the underlying operating system")
