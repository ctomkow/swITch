
from netmiko import ConnectHandler

from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography import utils as crypto_utils


# https://github.com/paramiko/paramiko/issues/750
def _override_check_dsa_parameters(parameters):

    """Override check_dsa_parameters from cryptography's dsa.py

    Allows for shorter or longer parameters.p to be returned from the server's host key. This is a
    HORRIBLE hack and a security risk, please remove if possible!
    """
    # if utils.bit_length(parameters.p) not in [1024, 2048, 3072]:
        # raise ValueError("p is {}, must be exactly 1024, 2048, or 3072 bits long".format(utils.bit_length(parameters.p)))
    if crypto_utils.bit_length(parameters.q) not in [160, 256]:
        raise ValueError("q must be exactly 160 or 256 bits long")

    if not (1 < parameters.g < parameters.p):
        raise ValueError("g, p don't satisfy 1 < g < p.")


dsa._check_dsa_parameters = _override_check_dsa_parameters


class SentryPdu:

    def __init__(self, details):

        self.netmiko_device_details = details

    def connect(self):

        return ConnectHandler(**self.netmiko_device_details)
