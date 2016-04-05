#!/usr/bin/env python

# Craig Tomkow
# April 4, 2016
#
# Send a config to a list of switches, specified in config files. Uses netmiko
# for handling switch interaction.

import argparse
from argparse import RawDescriptionHelpFormatter

from netmiko import ConnectHandler


class swITch:


    def __init__(self):

        # Arg Parsing
        parser = argparse.ArgumentParser(
            description="""
            This program logs into network devices using netmiko/paramiko, issue
            commands, and capture the result in output.log \n
            A typical example:\n
            swITch.py -eva auth.txt -i 172.30.30.30,cisco_ios -c 'show vlan'
            """,
            formatter_class=RawDescriptionHelpFormatter,
            add_help=False
            )
        reqFlags = parser.add_argument_group('Required flags')
        optFlags = parser.add_argument_group('Optional flags')
        reqFlags.add_argument('-a', '--auth', help="""Txt file with uername on first
            line,passwd on second,enablePasswd on third.""", required=True)
        optFlags.add_argument('-c', '--cmd', help="""Txt file with one device
            command per line. Or a single command in single quotes.""",
            required=False)
        optFlags.add_argument('-d', '--debug', help="""Prints out additional session
        action information beyond the default output and the verbose flag.
        Debug is a superset of all the flags. Debug --> verbose --> default output --> suppress.""",
        action='store_true', required=False)
        optFlags.add_argument('-e', '--enable', help="""Privileged exec mode. Will be ignored
        if the device drops you into privileged mode on login.""",
            action='store_true', required=False)
        optFlags.add_argument('-h', '--help', help="""show this help message and exit""",
            action='help')
        reqFlags.add_argument('-i', '--ip', help="""Txt file with one IP per
            line. Or a single IP in single quotes.""", required=True)
        optFlags.add_argument('-p', '--port', help="""File that has interface
            and port descriptions seperated by a comma per line. "int gi1/0/1 ,
            des C001".  Tip, use an excel sheet to generate the list.""",
            required=False)
        optFlags.add_argument('-s', '--suppress', help="""Suppress most output.  Does
        not print out the default output.
        Suppress is a subset of the default output. Debug --> verbose --> default output --> suppress.""",
        action='store_true', required=False)
        optFlags.add_argument('-v', '--verbose', help="""Prints out additional cli
        information.  This prints out the cli prompt and command sent.
        Verbose is a subset of debug. Debug --> verbose --> default output --> suppress.""", 
        action='store_true', required=False)
        
        args = parser.parse_args()
    
        self.main(args.auth, args.cmd, args.debug, args.enable, args.ip,
            args.port, args.suppress, args.verbose)

    #-------------------- Main Loop ----------------------------------
    def main(self, auth, commands, debug, enable, ip_list, port_list, suppress, verbose):      
    
        ##### FILE STUFF #####
    
        # Attempt to get file descriptors for each provided txt file
        if ip_list is not None:
            ip_list_file = self.open_file(ip_list, 'r', suppress)
            if ip_list_file == -1:
                if debug:
                    print 'Assuming this is an IP not a file'
                ip_list_file = [ip_list] 
        if commands is not None:
            cli_file = self.open_file(commands, 'r', suppress)
            if cli_file == -1:
                if debug:
                    print 'Assuming this is a cmd not a file'
                cli_file = [commands]
        if port_list is not None:
            port_list_file = self.open_file(port_list, 'r', suppress)
        output_file = self.open_file('output.log', 'a', suppress)   
        access_file = self.open_file(auth, 'r', suppress)
        
        uname = access_file.readline()
        uname = self.strip_new_line(uname)      
        passwd = access_file.readline()
        passwd = self.strip_new_line(passwd)       
        enable_passwd = access_file.readline()
        enable_passwd = self.strip_new_line(enable_passwd)

        # Initialize IP and command lists
        list_of_commands = []
        list_of_IPs      = []

        # Parse port description file
        if port_list is not None: 
            for cmd in port_list_file:
                cmd = self.strip_new_line(cmd)
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
            for cmd in cli_file:
                cmd = self.strip_new_line(cmd)
                list_of_commands.append(cmd) 
        # Parse IPs from file
        if ip_list is not None:
            for ip in ip_list_file:
                ip = self.strip_new_line(ip)
                list_of_IPs.append(ip)
        
        ##### SWITCH CONNECTION AND EXECUTION LOGIC #####  
    
        for ip in list_of_IPs:
            # IF CISCO, DO THIS
            if ip.find('cisco_ios') is not -1:
                ip = ip.rstrip(',cisco_ios')
                cisco_details = {
                    'device_type':'cisco_ios',
                    'ip':ip,
                    'username':uname,
                    'password':passwd,
                    'secret':enable_passwd,
                    'verbose': True}
                dev = ConnectHandler(**cisco_details)
                if enable:
                    self.enable(dev)
            # IF HP, DO THIS
            elif ip.find('hp_procurve') is not -1:
                ip = ip.rstrip(',hp_procurve')
                hp_details = {
                    'device_type':'hp_procurve',
                    'ip':ip,
                    'username':uname,
                    'password':passwd,
                    'secret':passwd,
                    'verbose': True}
                dev = ConnectHandler(**hp_details)
                if enable:
                    self.enable(dev, uname)
            
            # Run all commands on this device
            for cmd in list_of_commands:
                if verbose or debug:
                    print dev.find_prompt() + cmd
                output = dev.send_command(cmd)
                if verbose or debug:
                    print dev.find_prompt() 
                if not suppress:
                    print output # default output
                self.write_to(output_file, output)

            dev.disconnect()
                                                    
        # Close all files if they are open
        # Needs to determine if file is exists and is open or not...
        self.close_file(output_file, suppress)
        if commands is not None:
            self.close_file(cli_file, suppress)
        if port_list is not None:
            self.close_file(port_list_file, suppress)
        if ip_list_file is not None:
            self.close_file(ip_list_file, suppress)
        if access_file is not None:
            self.close_file(access_file, suppress)
            
#------------------ Methods -----------------------------------------
# Handling files. Add exception handling in these methods. Should
# these methods be in a class? There is already the python file
# class that these methods call...
#--------------------------------------------------------------------

    def open_file(self, file, operation, suppress):

        try:
            f = open(file, operation)
        except IOError:
            if not suppress:
                print 'Can\'t open file because I can\'t find file to open.'
            return -1
        return f

    def close_file(self, file, suppress):

        try:
            file.close()
        except AttributeError:
            if not suppress:
                print 'Can\'t close file due to no file attributes'
            else:
                pass

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
        else: # a username and password
            dev.enable(default_username=enable_username) 

    
if __name__=='__main__':
    swITch()

