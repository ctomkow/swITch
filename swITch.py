#!/usr/bin/env python

# Craig Tomkow
# February 5, 2016
#
# Set a config to a list of switches, specified in config files
#
#  !!!!!  NOTE TO SELF !!!!! 
# In the send commands loop, its send/expect

import argparse
from netmiko import ConnectHandler


class swITch:


    def __init__(self):

        # Arg Parsing
        parser = argparse.ArgumentParser(
            description="""This program can log into devices using expect, issue
            commands, and capture the result.""")
        parser.add_argument('-e', '--enable', help='Privileged exec mode',
            action='store_true', required=False)
        parser.add_argument('-i', '--iplist', help="""Txt file with one IP per
            line. Or a single IP in single quotes.""", required=True)
        parser.add_argument('-c', '--commands', help="""Txt file with one device
            command per line. Or a single command in single quotes.""",
            required=False)
        parser.add_argument('-a', '--auth', help="""Txt file with uname on first
            line,passwd on second,enablePasswd on third""", required=True)
        parser.add_argument('-p', '--portlist', help="""File that has interface
            and port descriptions seperated by a comma per line. "int gi1/0/1 ,
            des C001".  Tip, use an excel sheet to generate the list.""",
            required=False)
        args = parser.parse_args()
    
        self.main(args.enable, args.iplist, args.commands, args.auth,
            args.portlist)

    #-------------------- Main Loop ----------------------------------
    def main(self, enable, ip_list, commands, auth, port_list):      
    
        ##### FILE STUFF #####
    
        # Attempt to get file descriptors for each provided txt file
        if ip_list is not None:
            ip_list_file = self.open_file(ip_list, 'r')
            if ip_list_file == -1:
                print 'Hokay, assuming this is an IP not a file'
                ip_list_file = [ip_list] 
        if commands is not None:
            cli_file = self.open_file(commands, 'r')
            if cli_file == -1:
                print 'Hokay, assuming this is a cmd not a file'
                cli_file = [commands]
        if port_list is not None:
            port_list_file = self.open_file(port_list, 'r')
        output_file = self.open_file('output.txt', 'a')   
        access_file = self.open_file(auth, 'r')
        
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
                ciscoDetails = {
                    'device_type':'cisco_ios',
                    'ip':ip,
                    'username':uname,
                    'password':passwd,
                    'secret':enable_passwd,
                    'verbose': True}
                dev = ConnectHandler(**ciscoDetails)
            # IF HP, DO THIS
            elif ip.find('hp_procurve') is not -1:
                ip = ip.rstrip(',hp_procurve')
                hpDetails = {
                    'device_type':'hp_procurve',
                    'ip':ip,
                    'username':uname,
                    'password':passwd,
                    'verbose': True}
                dev = ConnectHandler(**hpDetails)
            
            # Enable da switch
            if enable:
                dev.enable()
            
            # Run all commands on this device
            for cmd in list_of_commands:
                print dev.find_prompt() + cmd
                output = dev.send_command(cmd)
                print dev.find_prompt()
                print output
                self.write_to(output_file, output)

            dev.disconnect()
                                                    
        # Close all files if they are open
        # Needs to determine if file is exists and is open or not...
        self.close_file(output_file)
        if commands is not None:
            self.close_file(cli_file)
        if port_list is not None:
            self.close_file(port_list_file)
        if ip_list_file is not None:
            self.close_file(ip_list_file)
        if access_file is not None:
            self.close_file(access_file)
            
#------------------ Methods -----------------------------------------
# Handling files. Add exception handling in these methods. Should
# these methods be in a class? There is already the python file
# class that these methods call...
#--------------------------------------------------------------------

    def open_file(self, file, operation):

        try:
            f = open(file, operation)
        except IOError:
            print 'Can\'t open file because I can\'t find file to open.'
            return -1
        return f

    def close_file(self, file):

        try:
            file.close()
        except AttributeError:
            print 'Can\'t close file due to no file attributes'

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

    
if __name__=='__main__':
    swITch()

