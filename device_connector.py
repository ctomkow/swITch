# Craig Tomkow
# August 4, 2016
#
# Device class to handle selecting the correct device


from netmiko import ConnectHandler
from netmiko import FileTransfer


class device_connector:
    
    
    device_type = ''
    raw_ip = ''
    ip = ''
    username = ''
    password = ''
    enable_password = ''
    netmiko_device_details = {}
    device_connection = None
    connect_type = ''
    
    def __init__(self, raw_ip, username, password, enable_password='', connect_type='ssh'):
        
        self.raw_ip = raw_ip
        self.username = username
        self.password = password
        self.enable_password = enable_password
        self.connect_type = connect_type
        
        if self.raw_ip.find('cisco_ios') is not -1:
                self.ip = self.raw_ip.rstrip(',cisco_ios')
                if connect_type == 'telnet':
                    print 'selected telnet'
                    self.device_type = 'telnet'
                else:
                    self.device_type = 'cisco_ios'
                self.cisco_ios_normalize()
                self.device_connection = self.connect()
        elif self.raw_ip.find('hp_procurve') is not -1:
                self.ip = self.raw_ip.rstrip(',hp_procurve')
                self.device_type = 'hp_procurve'
                self.hp_procurve_normalize()
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
    
    def connect(self):
        
        return ConnectHandler(**self.netmiko_device_details)
        
    def find_prompt(self):
        
        return self.device_connection.find_prompt()
        
    def send_command(self, cmd):
        
        return self.device_connection.send_command(cmd)
        
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
