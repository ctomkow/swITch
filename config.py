# Craig Tomkow
# Nov 25, 2016
#
# Device class to generate the switch config (pull from yaml, etc.)


import yaml

class config:
    
    
    username        = []
    password        = []
    enable_password = []
    config_list     = {}
    
    gen_conf_state  = False
    int_desc_state  = False
    
    def __init__(self, gen_conf, int_desc):
        
        # Set the config options to know whether to parse config info or interface descriptions
        if gen_conf:
            self.gen_conf_state = True
        if int_desc:
            self.int_desc_state = True
        
        with open("conf.yaml", 'r') as stream:
            try:
                self.config_list = (yaml.load(stream))
            except yaml.YAMLError as exc:
                print(exc)
        
        # Set creds to global class variables.
        self.username = self.convert_list_to_string(self.get_single_item('credentials', 'username'))
        self.password = self.convert_list_to_string(self.get_single_item('credentials', 'password'))
        self.enable_password = self.convert_list_to_string(self.get_single_item('credentials', 'enable'))
        
        # Pop off credentials ... so I only get device groups (stored creds as vars, don't need them now)
        self.config_list.pop('credentials', None)

    def get_config_length(self):
        
        return len(self.config_list)
    
    def convert_list_to_string(self, list):
        
        return str(list[0])

    def get_single_item(self, index_name, subindex_name):
        
        return self.config_list[index_name][subindex_name]
        
    def get_username(self):
        
        return self.username
    
    def get_password(self):
        
        return self.password
    
    def get_enable_password(self):
        
        return self.enable_password
        
    def get_a_device_group(self):
        
        # Pull out a dictionary tuple (note I said 'a' not first/last, as dicts are unordered)
        (i,j) = self.config_list.items()[0]
        ip_list = []
        cmd_list = []
        int_desc = []
        
        # Call get dict,key method, it raises a Keyerror if key not found
        device_type = self.get_dict_item(j, 'device_type')
        for ip in self.get_dict_item(j, 'ip_address'):
            ip_list.append(ip)
        if self.gen_conf_state:
            for config in self.get_dict_item(j, 'config'):
                cmd_list.append(config)
        if self.int_desc_state:
            for desc in self.get_dict_item(j, 'interface_description'):
                int_desc.append(desc)
        
        # Pop off list so I don't grab it again
        try:
            self.config_list.pop(i,j)
            # Ensure that you are returning the correct config variables/lists
            if self.gen_conf_state:
                return self.convert_list_to_string(device_type), ip_list, cmd_list
            if self.int_desc_state:
                return self.convert_list_to_string(device_type), ip_list, int_desc
        except IndexError:
            return None, None, None
    
    def set_a_device_group(self, ip, cmd, device_type):
        
        self.config_list = {'CLI_GROUP': {'ip_address': [ip], 'config': [cmd], 'device_type': [device_type]}}
        
    def get_dict_item(self, dict, key):
        
        if dict.get(key) is None:
            raise KeyError("%s not present" % key)
        else:
            return dict.get(key)