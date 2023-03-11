# Craig Tomkow
# August 4, 2016
#
# Device class to handle selecting the correct device


from netmiko import ConnectHandler
from netmiko import FileTransfer

from swITch.sentry_pdu import SentryPdu


class device_connector:
    
    
    device_type = ''
    raw_ip = ''
    ip = ''
    username = ''
    password = ''
    enable_password = ''
    netmiko_device_details = {}
    device_connection = None
    
    def __init__(self, raw_ip, username, password, enable_password=''):
        
        self.raw_ip = raw_ip
        self.username = username
        self.password = password
        self.enable_password = enable_password
        
        if self.raw_ip.find('cisco_ios') != -1:
                self.ip = self.raw_ip.rstrip('cisco_ios').replace(',', '')
                self.device_type = 'cisco_ios'
                self.cisco_ios_normalize()
                self.device_connection = self.connect()
        elif self.raw_ip.find('hp_procurve') != -1:
                self.ip = self.raw_ip.rstrip('hp_procurve').replace(',', '')
                self.device_type = 'hp_procurve'
                self.hp_procurve_normalize()
                self.device_connection = self.connect()
        elif self.raw_ip.find('sentry_pdu') != -1:
                self.ip = self.raw_ip.rstrip('sentry_pdu').replace(',', '')
                self.device_type = 'sentry_pdu'
                self.sentry_pdu_normalize()
                self.sentry_pdu = SentryPdu(self.netmiko_device_details)
                self.device_connection = self.sentry_pdu.connect()
        elif self.raw_ip.find('juniper_junos') != -1:
                self.ip = self.raw_ip.rstrip('juniper_junos').replace(',', '')
                self.device_type = 'juniper_junos'
                self.juniper_junos_normalize()
                self.device_connection = self.connect()
        elif self.raw_ip.find('paloalto_panos') != -1:
                self.ip = self.raw_ip.rstrip('paloalto_panos').replace(',', '')
                self.device_type = 'paloalto_panos'
                self.paloalto_panos_normalize()
                self.device_connection = self.connect()
        else: # Unsupported device or missing device type, raise exception
            raise ValueError()
        
    def cisco_ios_normalize(self):
        
        self.netmiko_device_details = {
            'device_type':self.device_type,
            'ip':self.ip,
            'username':self.username,
            'password':self.password,
            'secret':self.enable_password,
            'verbose':False,
            'global_delay_factor': .2,
        }
    ##### HP is currently broken it seems (when needing uname/pass for enable) Why oh why!
    def hp_procurve_normalize(self):
        
        self.netmiko_device_details = {
            'device_type':self.device_type,
            'ip':self.ip,
            'username':self.username,
            'password':self.password,
            'secret':self.password,
            'verbose':False,
        }

    def sentry_pdu_normalize(self):

        # device list: https://github.com/ktbyers/netmiko/blob/develop/netmiko/ssh_dispatcher.py
        self.netmiko_device_details = {
            'device_type': 'accedian',
            'ip': self.ip,
            'username': self.username,
            'password': self.password,
            'verbose': False,
            'conn_timeout': 20,
            'global_delay_factor': 2.0,
        }

    def juniper_junos_normalize(self):

        # device list: https://github.com/ktbyers/netmiko/blob/develop/netmiko/ssh_dispatcher.py
        self.netmiko_device_details = {
            'device_type': self.device_type,
            'ip': self.ip,
            'username': self.username,
            'password': self.password,
            'verbose': False,
            'global_delay_factor': 2.0,
        }

    def paloalto_panos_normalize(self):

        # device list: https://github.com/ktbyers/netmiko/blob/develop/netmiko/ssh_dispatcher.py
        self.netmiko_device_details = {
            'device_type': self.device_type,
            'ip': self.ip,
            'username': self.username,
            'password': self.password,
            'verbose': False,
        }
    
    def connect(self):
        
        return ConnectHandler(**self.netmiko_device_details)
        
    def find_prompt(self):
        
        return self.device_connection.find_prompt()
        
    def send_command(self, cmd):
        
        return self.device_connection.send_command(cmd)

    def send_config_set(self, set_list):

        if self.device_type == 'juniper_junos':
            return self.device_connection.send_config_set(set_list, exit_config_mode=False, config_mode_command='configure exclusive')
        elif self.device_type == 'cisco_ios':
            return self.device_connection.send_config_set(set_list, exit_config_mode=True)
        elif self.device_type == 'hp_procurve':
            return self.device_connection.send_config_set(set_list, exit_config_mode=True)
        elif self.device_type == 'sentry_pdu':
            return self.device_connection.send_config_set(set_list, exit_config_mode=False)
        elif self.device_type == 'paloalto_panos':
            try:
                return self.device_connection.send_config_set(set_list, exit_config_mode=False)
            except OSError:
                return "Did not find expected pattern. Likely nothing to commit!"
        else:
            pass

    def save_config_and_exit(self):

        buf = ""

        if self.device_type == 'juniper_junos':
            buf += self.device_connection.commit(and_quit=True)
        elif self.device_type == 'cisco_ios':
            buf += self.device_connection.save_config()
        elif self.device_type == 'hp_procurve':
            buf += self.device_connection.save_config()
        elif self.device_type == 'sentry_pdu':
            try: # e.g. sentry_pdu uses netmiko's accedian device - it doesn't impl save_config as config is auto-saved
                buf += self.device_connection.save_config()
            except NotImplementedError:
                return buf
        elif self.device_type == 'paloalto_panos':
            buf += self.device_connection.commit()
        else:
            pass

        buf += self.device_connection.exit_config_mode()
        return buf
        
    def disconnect(self):
        
        return self.device_connection.disconnect()
    
    def enable(self):
        
        if self.device_type == 'cisco_ios':
            return self.device_connection.enable()
        elif self.device_type == 'hp_procurve':
            return self.device_connection.enable(default_username=self.username)
    
    def transfer_file(self, file):
        
        with FileTransfer(self.device_connection, source_file=file, dest_file=file) as scp_transfer:
            if scp_transfer.check_file_exists():
                return file + ' already exists!'
            else:
                if not scp_transfer.verify_space_available():
                    return 'Insufficient space available!'
                scp_transfer.transfer_file() # Transfer file                                      
                if scp_transfer.verify_file():
                    return 'Transfer complete! \nsrc and dst MD5 match!'
                else:
                    return 'Transfer failed! \nMD5 mismatch on src and dst!'
        
    def enable_scp(self):
        
        return self.device_connection.send_config_set(['ip scp server enable'])
    
    def disable_scp(self):
        
        return self.device_connection.send_config_set(['no ip scp server enable'])
    
    def enable_authorization(self):
        
        return self.device_connection.send_config_set(['aaa authorization exec default group TACACS_PLUS local'])
        
    def disable_authorization(self):
        
        return self.device_connection.send_config_set(['no aaa authorization exec default group TACACS_PLUS local'])
