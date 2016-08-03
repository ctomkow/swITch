# Craig Tomkow
# August 3, 2016
#
# Device class to handle selecting the correct device


from netmiko import ConnectHandler


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
            print "self.username"
            self.device_connection.enable(default_username=self.username)

#        if self.enable_username is '': # just a password
#            dev.enable()
#        else: # username and password
#            dev.enable(default_username=enable_username) 
            
            
### CREATE VARIOUS METHODS FOR INTERACTING WITH NETMIKO HERE SO I AM NOT DIRECTLY
### ACCESSING NETMIKO FROM MAIN!!!  DECOUPLE THAT SHIT!
