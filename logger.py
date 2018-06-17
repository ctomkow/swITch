# Craig Tomkow
# July 27, 2016
#
# Logger class to handle STDOUT and logging to file


class logger:
    
    
    log_level_dict = {"suppress" : 0, "log_only" : 5, "info" : 10, "verbose" : 20, "debug" : 30}
    log_level = -1
    log_file = ''
    
    def __init__(self, log_level_mnemonic):
        
        self.log_level = self.log_level_dict[log_level_mnemonic]
        try:
            self.log_file = open('output.log', 'w')
        except IOError:
            return -1
    
    def event(self, target_log_level_mnemonic, msg):
        
        target_log_level = self.log_level_dict[target_log_level_mnemonic]
        if target_log_level <= self.log_level:
            print(msg)
            self.log_file.write(msg)
        else:
            pass
        
    def close_log_file(self):
        
        try:
            self.log_file.close()
        except AttributeError:
            self.event('debug', 'Can\'t close output.log file')

