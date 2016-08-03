# Craig Tomkow
# August 3, 2016
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
    
    def __init__(self, raw_ip, username, password, enable_password=''):
        
        self.raw_ip = raw_ip
        self.username = username
        self.password = password
        self.enable_password = enable_password
        
        if self.raw_ip.find('cisco_ios') is not -1:
                self.ip = self.raw_ip.rstrip(',cisco_ios')
                self.device_type = 'cisco_ios'
                self.cisco_ios_normalize()
                self.device_connection = self.connect()
        elif self.raw_ip.find('hp_procurve') is not -1:
                self.ip = self.raw_ip.rstrip(',hp_procurve')
                self.device_type = 'hp_procurve'
                self.hp_procurve_normalize()
                self.device_connection = self.connect()
        else: # Unsupported device or missing device type, so skip it
            return(self.raw_ip + " is an unsupported type, or missing type. Skipping.")
        
    def cisco_ios_normalize(self):
        
        self.netmiko_device_details = {
            'device_type':self.device_type,
            'ip':self.ip,
            'username':self.username,
            'password':self.password,
            'secret':self.enable_password,
            'verbose':False,
        }
    
    def hp_procurve_normalize(self): # HP is currently broken! Don't know why!!!1
        
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
            self.device_connection.enable()
        elif self.device_type == 'hp_procurve':
            self.device_connection.enable(default_username=self.username)
    
    def transfer_file(self, file, zomg):
        with FileTransfer(self.device_connection, source_file=file, dest_file=file) as scp_transfer:
            if scp_transfer.check_file_exists():
                print 'file already exists'
                #log.event('info', file_image + " Already Exists")
            else: ##### make this an elif so the program doesn't break when not enough space available...remove the valueerror...
                if not scp_transfer.verify_space_available():
                    output = "Insufficient space available on remote device"
                    print output
                    #log.event('info', output)
                    #raise ValueError(output) 
                
#                log.event('verbose', 'Enabling SCP') 
                log_output = self.scp_handler('enable') # Enable SCP  
#                log.event('debug', 'DEBUG: ' + log_output)
                if zomg:
#                   log.event('debug', 'DEBUG: ' + self.enable_authorization(dev))
                    self.enable_authorization()
#                log.event('verbose', 'SCP enabled')
#                log.event('info', "Started Transferring at " + str(datetime.datetime.now()))         
                scp_transfer.transfer_file() # Transfer file                   
#                log.event('info', "Finished transferring at " + str(datetime.datetime.now()))
#                log.event('verbose', 'Disabling SCP')
                log_output = self.scp_handler('disable') # Disable SCP
#                log.event('debug', 'DEBUG: ' + log_output)
                if zomg:
#                        log.event('debug', 'DEBUG: ' + self.disable_authorization(dev))
                    self.disable_authorization()
#                log.event('verbose', 'SCP disabled')
#                log.event('info', 'Verifying file...')
#                        
                if scp_transfer.verify_file():
#                        log.event('info', 'Src and dest MD5 matches')
                    print 'src and des MD5 matches'
                else:
                    print 'MD5 mismatch'
#                      output
#                      log.event('info', 'MD5 mismatch between src and dest') 
#                      raise ValueError(output)
    
    def scp_handler(self, mode):
        cmd='ip scp server enable'
        if mode == 'disable':
            cmd = 'no ' + cmd
            return self.device_connection.send_config_set([cmd])
        if mode == 'enable':
            return self.device_connection.send_config_set([cmd])
    
    def enable_authorization(self):
        return self.device_connection.send_config_set(['aaa authorization exec default group TACACS_PLUS local'])
        
    def disable_authorization(self):
        return self.device_connection.send_config_set(['no aaa authorization exec default group TACACS_PLUS local'])
        
            
            
### CREATE VARIOUS METHODS FOR INTERACTING WITH NETMIKO HERE SO I AM NOT DIRECTLY
### ACCESSING NETMIKO FROM MAIN!!!  DECOUPLE THAT SHIT!
