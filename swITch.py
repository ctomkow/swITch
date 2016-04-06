#!/usr/bin/env python

# Craig Tomkow
# April 4, 2016
#
# Send a config to a list of switches, specified in config files. Uses netmiko
# for handling switch interaction.


from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from netmiko import ConnectHandler


class swITch:


    def __init__(self):

        # Arg Parsing
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, add_help=False,
            description="""
            This program logs into network devices using netmiko/paramiko, issue
            commands, and capture the result in output.log \n
            A typical example:\n
            swITch.py -eva auth.txt -i 172.30.30.30,cisco_ios -c 'show vlan'""")
            
        reqFlags = parser.add_argument_group('Required flags')
        reqFlags.add_argument('-a', '--auth', required=True,
            help="""Txt file with username on first line, passwd on second,
            enablePasswd on third.""")
        reqFlags.add_argument('-i', '--ip', required=True, 
            help="""Txt file with one IP per line. Or a single IP in single 
            quotes.""")
            
        optFlags = parser.add_argument_group('Optional flags')
        optFlags.add_argument('-c', '--cmd', required=False,
            help="""Txt file with one device command per line. Or a single 
            command in single quotes.""")
        optFlags.add_argument('-d', '--debug', required=False, action='store_true',
            help="""Prints out additional session action information beyond 
            the default output and the verbose flag. Debug is a superset of all
            the flags. Debug --> verbose --> default output --> suppress.""")
        optFlags.add_argument('-e', '--enable', action='store_true', required=False,
            help="""Privileged exec mode. Will be ignored if the device drops 
            you into privileged mode on login.""")
        optFlags.add_argument('-h', '--help', action='help', 
            help="""show this help message and exit""")
        optFlags.add_argument('-p', '--port', required=False, 
            help="""File that has interface and port descriptions seperated 
            by a comma per line. "int gi1/0/1 ,des C001".  Tip, use an excel 
            sheet to generate the list.""")
        optFlags.add_argument('-s', '--suppress', action='store_true', required=False,
            help="""Suppress all output.  What is happening?! OOOoooOOoOOOO! Suppress 
            is a subset of the default output. Debug --> verbose --> 
            default output --> suppress.""")
        optFlags.add_argument('-v', '--verbose', action='store_true', required=False,
            help="""Prints out additional cli information.  This prints out the 
            cli prompt and command sent. Verbose is a subset of debug. 
            Debug --> verbose --> default output --> suppress.""")
        
        args = parser.parse_args()
    
        self.main(args.auth, args.cmd, args.debug, args.enable, args.ip,
            args.port, args.suppress, args.verbose)

    #--------------------------------------------------------------------------#
    #                               Main Loop                                  #
    #--------------------------------------------------------------------------#
    def main(self, auth, commands, debug, enable, ip_list, port_list, suppress, verbose):      
    
        ### FILE STUFF ###
    
        # Attempt to get file descriptors for each provided txt file
        output_file = self.open_file('output.log', 'w')
        
        if ip_list is not None:
            ip_list_file = self.open_file(ip_list, 'r')
            if ip_list_file == -1:
                if debug:
                    print 'Not a file.  Assuming it\'s an IP address'
                    self.write_to(output_file, 'Not a file.  Assuming it\'s an IP address' + "\n")
                ip_list_file = [ip_list] 
        if commands is not None:
            cli_file = self.open_file(commands, 'r')
            if cli_file == -1:
                if debug:
                    print 'Not a file. Assuming it\'s a cli command'
                    self.write_to(output_file, 'Not a file. Assuming it\'s a cli command' + "\n")
                cli_file = [commands]
        if port_list is not None:
            port_list_file = self.open_file(port_list, 'r')
            if port_list_file == -1:
                if debug:
                    print 'Can\'t open port list file'
                    self.write_to(output_file, 'Can\'t open port list file.' + "\n")
                pass
        if auth is not None:
            access_file = self.open_file(auth, 'r') 
            if access_file == -1:
                if debug:
                    print 'Can\'t open authentication file'
                    self.write_to(output_file, 'Can\'t open port list file.' + "\n")
                pass
            
        raw_uname = access_file.readline()
        uname = self.strip_new_line(raw_uname)      
        raw_passwd = access_file.readline()
        passwd = self.strip_new_line(raw_passwd)       
        raw_enable_passwd = access_file.readline()
        enable_passwd = self.strip_new_line(raw_enable_passwd)

        # Initialize IP and command lists
        list_of_commands = []
        list_of_IPs      = []

        # Parse port description file
        if port_list is not None: 
            for raw_cmd in port_list_file:
                cmd = self.strip_new_line(raw_cmd)
                if cmd.find(',') == -1:
                    list_of_commands.append(cmd)
                else:
                    cmd_array = cmd.split(',')
                    interface_cmd = cmd_array[0]
                    interface_cmd = interface_cmd.replace('\t', '')
                    description_cmd = cmd_array[1]
                    description_cmd = description_cmd.replace('\t', '')
                    list_of_commands.append(interface_cmd)
                    list_of_commands.append(description_cmd)
        # Parse cli commands
        if commands is not None:    
            for raw_cmd in cli_file:
                cmd = self.strip_new_line(raw_cmd)
                list_of_commands.append(cmd) 
        # Parse IPs from file
        if ip_list is not None:
            for raw_ip in ip_list_file:
                ip = self.strip_new_line(raw_ip)
                list_of_IPs.append(ip)
        
        ### SWITCH CONNECTION AND EXECUTION LOGIC ###  
    
        for ip in list_of_IPs:
            # If Cisco...
            if ip.find('cisco_ios') is not -1:
                ip = ip.rstrip(',cisco_ios')
                cisco_details = {
                    'device_type':'cisco_ios',
                    'ip':ip,
                    'username':uname,
                    'password':passwd,
                    'secret':enable_passwd,
                    'verbose': not suppress}
                dev = ConnectHandler(**cisco_details)
                if not suppress:
                    output = "SSH connection open to " + ip
                    self.write_to(output_file, output + "\n")
                if enable:
                    self.enable(dev)
            # If HP...
            elif ip.find('hp_procurve') is not -1:
                ip = ip.rstrip(',hp_procurve')
                hp_details = {
                    'device_type':'hp_procurve',
                    'ip':ip,
                    'username':uname,
                    'password':passwd,
                    'secret':passwd,
                    'verbose': not suppress}
                dev = ConnectHandler(**hp_details)
                if not suppress:
                    output = "SSH connection open to " + ip
                    self.write_to(output_file, output + "\n")
                if enable:
                    self.enable(dev, uname)
            
            # Run all commands on this device
            for cmd in list_of_commands:
                if verbose or debug:
                    output = dev.find_prompt() + cmd
                    print output
                    self.write_to(output_file, output + "\n")
                    
                output = dev.send_command(cmd) # send command
                if not suppress:
                    print output # default output, can be suppressed
                    self.write_to(output_file, output)
                    
                if debug:
                    output = "PROMPT:" + dev.find_prompt() 
                    print output
                    self.write_to(output_file, output + "\n")

            dev.disconnect()
            if not suppress:
                output = "SSH connection closed to " + ip # base output, can be suppressed
                print output
                self.write_to(output_file, output + "\n")
 
        ### CLEANUP ###
        
        # Close all files if they are open
        if output_file is not None:
            op_code = self.close_file(output_file)
            if op_code == -1:
                if debug:
                    print 'Can\'t close output.log file'
                    self.write_to(output_file, 'Can\'t close output.log file' + "\n")
                pass
        if commands is not None:
            op_code = self.close_file(cli_file)
            if op_code == -1:
                if debug:
                    print 'Can\'t close cli file'
                    self.write_to(output_file, 'Can\'t close cli file' + "\n")
                pass
        if port_list is not None:
            op_code = self.close_file(port_list_file)
            if op_code == -1:
                if debug:
                    print 'Can\'t close port list file'
                    self.write_to(output_file, 'Can\'t close port list file' + "\n")
                pass
        if ip_list_file is not None:
            op_code = self.close_file(ip_list_file)
            if op_code == -1:
                if debug:
                    print 'Can\'t close ip list file'
                    self.write_to(output_file, 'Can\'t close ip list file' + "\n")
                pass
        if access_file is not None:
            op_code = self.close_file(access_file)
            if op_code == -1:
                if debug:
                    print 'Can\'t close access file'
                    self.write_to(output_file, 'Can\'t close access file' + "\n")
                pass
            
#------------------------------------------------------------------------------#
#                                  Methods                                     #
#------------------------------------------------------------------------------#

    def open_file(self, file, operation):

        try:
            f = open(file, operation)
        except IOError:
            return -1
        return f

    def close_file(self, file):

        try:
            file.close()
        except AttributeError:
            return -1
        return 0

    def write_to(self, file, str):

        file.write(str)
    
    # Strip newlines (\r\n for Windows) (\n for Unix)
    # Search for \r\n first, if not, it will remove just \n from \r\n
    def strip_new_line(self, str):
        
        if str.endswith('\r\n'):
            str = str.rstrip('\r\n')
        elif str.endswith('\n'):
            str = str.rstrip('\n')
        return str

    def enable(self, dev, enable_username=''):

        if enable_username is '': # just a password
            dev.enable()
        else: # username and password
            dev.enable(default_username=enable_username) 

    
if __name__=='__main__':
    swITch()

