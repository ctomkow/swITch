#!/usr/bin/env python

# Craig Tomkow
# July 27, 2016
#
# Send a config to a list of switches, specified in config files. Uses netmiko
# for handling switch interaction.

import datetime
import logger
import device_connector
import argparse
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from netmiko import FileTransfer


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
        reqFlags.add_argument('-a', '--auth', required=True, metavar='\b',
            help="""Txt file with username on first line, passwd on second,
            enablePasswd on third.""")
        reqFlags.add_argument('-i', '--ip', required=True, metavar='\b',
            help="""Txt file with one IP per line. Or a single IP in single 
            quotes.""")
      
        optFlags = parser.add_argument_group('Privilege level')
        optFlags.add_argument('-e', '--enable', action='store_true', required=False,
            help="""Privileged exec mode. Will be ignored if the device drops 
            you into privileged mode on login.""")
           
        mutExclusiveFlags = parser.add_mutually_exclusive_group()
        mutExclusiveFlags.add_argument('-c', '--cmd', required=False, metavar='\b',
            help="""Txt file with one device command per line. Or a single 
            command in single quotes.""")
        mutExclusiveFlags.add_argument('-f', '--file', required=False, metavar='\b',
            help="""File name that will be transfered to device. Usually an image
            upgrade file.""")
        mutExclusiveFlags.add_argument('-p', '--port', required=False, metavar='\b', 
            help="""File that has interface and port descriptions seperated 
            by a comma per line. "int gi1/0/1 ,des C001".  Tip, use an excel 
            sheet to generate the list.""")
            
        outputFlags = parser.add_argument_group('Output flags')
        outputFlags.add_argument('-d', '--debug', required=False, action='store_true',
            help="""Prints out additional session action information beyond 
            the default output and the verbose flag. Debug is a superset of all
            the flags. Debug --> verbose --> default/info --> suppress.""")
        outputFlags.add_argument('-h', '--help', action='help', 
            help="""show this help message and exit""")
        outputFlags.add_argument('-s', '--suppress', action='store_true', required=False,
            help="""Suppress all STDOUT, also no log file entries.  What is happening?! Suppress 
            is a subset of the default/info output. Debug --> verbose --> 
            default/info --> suppress.""")
        outputFlags.add_argument('-v', '--verbose', action='store_true', required=False,
            help="""Prints out additional cli information.  This prints out the 
            cli prompt and command sent. Verbose is a subset of debug. 
            Debug --> verbose --> default/info --> suppress.""")
        outputFlags.add_argument('-z', '--zomg', action='store_true', required=False,
            help=argparse.SUPPRESS)
        
        args = parser.parse_args()
        
    
        self.main(args.auth, args.cmd, args.debug, args.enable, args.ip,
            args.port, args.suppress, args.file, args.verbose, args.zomg)

    #--------------------------------------------------------------------------#
    #                               Main Loop                                  #
    #--------------------------------------------------------------------------#
    def main(self, auth, commands, debug, enable, ip_list, port_list, suppress, file_image, verbose, zomg):      
    
        ### LOGGING STUFF ###
        if debug:
            log = logger.logger("debug")
        elif verbose:
            log = logger.logger("verbose")
        elif suppress:
            log = logger.logger("suppress")
        else: # Default output, no flags needed for this
            log = logger.logger("info")
    
        ### FILE DESCRIPTOR STUFF ###
        # Attempt to get file descriptors for each provided txt file
        if ip_list:
            ip_list_file = self.open_file(ip_list, 'r')
            if ip_list_file == -1:
                log.event('debug', 'DEBUG: Not a file.  Assuming ' + ip_list + ' is a valid IP')
                ip_list_file = [ip_list] 
        if commands:
            cli_file = self.open_file(commands, 'r')
            if cli_file == -1:
                log.event('debug', 'DEBUG: Not a file. Assuming ' + commands + ' is a valid cmd')
                cli_file = [commands]
        if port_list:
            port_list_file = self.open_file(port_list, 'r')
            if port_list_file == -1:
                log.event('debug', 'DEBUG: File name that can\'t be opened: ' + port_list)
                raise IOError('Can\'t open port list file')
        if auth:
            access_file = self.open_file(auth, 'r') 
            if access_file == -1:
                log.event('debug', 'DEBUG: File name that can\'t be opened: ' + auth)
                raise IOError('Can\'t open authentication file')
                
            
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
        if port_list: 
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
        if commands:    
            for raw_cmd in cli_file:
                cmd = self.strip_new_line(raw_cmd)
                list_of_commands.append(cmd) 
        # Parse IPs from file
        if ip_list:
            for raw_ip in ip_list_file:
                ip = self.strip_new_line(raw_ip)
                list_of_IPs.append(ip)
        
        # All Device IPs
        for ip in list_of_IPs:
            
            ### SWITCH CONNECTION LOGIC ###  
            # Add error handling around creating a device to handle if a device type is missing, etc.
            # object = filename.classname
            dev = device_connector.device_connector(ip, uname, passwd, enable_passwd)
            log.event('info', "SSH connection open to " + dev.ip)
            if enable:
                dev.enable()
######            if enable:
######                self.enable(dev, uname)
######            else: # Unsupported device or missing device type, so skip it
######                log.event('info', "Device " + ip + " is an unsupported type, or missing type name. Skipping.")
######                continue
            
            ### COMMAND EXECUTION LOGIC ###
            # Run all commands on this device
            if commands:
                for cmd in list_of_commands:
                    log.event('verbose', dev.find_prompt() + cmd)
                    log_output = dev.send_command(cmd) # send command
                    log.event('info', log_output)
                    log.event('debug', "DEBUG PROMPT:" + dev.find_prompt())

                dev.disconnect()
                log.event('info', "SSH connection closed to " + ip)
                    
            
            ### IMAGE FILE TRANSFER LOGIC ###
            if file_image:
                with FileTransfer(dev, source_file=file_image, dest_file=file_image) as scp_transfer:
                    if scp_transfer.check_file_exists():
                        log.event('info', file_image + " Already Exists")
                    else: ##### make this an elif so the program doesn't break when not enough space available...remove the valueerror...
                        if not scp_transfer.verify_space_available():
                            output = "Insufficient space available on remote device"
                            log.event('info', output)
                            #raise ValueError(output)

                        log.event('verbose', 'Enabling SCP') 
                        log_output = self.scp_handler(dev, 'enable') # Enable SCP  
                        log.event('debug', 'DEBUG: ' + log_output)
                        if zomg:
                            log.event('debug', 'DEBUG: ' + self.enable_authorization(dev))
                        log.event('verbose', 'SCP enabled')
                        log.event('info', "Started Transferring at " + str(datetime.datetime.now()))         
                        scp_transfer.transfer_file() # Transfer file                   
                        log.event('info', "Finished transferring at " + str(datetime.datetime.now()))
                        log.event('verbose', 'Disabling SCP')
                        log_output = self.scp_handler(dev, 'disable') # Disable SCP
                        log.event('debug', 'DEBUG: ' + log_output)
                        if zomg:
                            log.event('debug', 'DEBUG: ' + self.disable_authorization(dev))
                        log.event('verbose', 'SCP disabled')
                        log.event('info', 'Verifying file...')
                        
                        if scp_transfer.verify_file():
                            log.event('info', 'Src and dest MD5 matches')
                        else:
                            output
                            log.event('info', 'MD5 mismatch between src and dest') 
                            #raise ValueError(output)
                                            
 
        ### CLEANUP ###     
        # Close all files if they are open
        if commands:
            op_code = self.close_file(cli_file)
            if op_code == -1:
                log.event('debug', 'DEBUG: File that can\'t be closed: ' + str(cli_file))
        if port_list:
            op_code = self.close_file(port_list_file)
            if op_code == -1:
                log.event('debug', 'DEBUG: File that can\'t be closed: ' + str(port_list_file))
        if ip_list_file:
            op_code = self.close_file(ip_list_file)
            if op_code == -1:
                log.event('debug', 'DEBUG: File that can\'t be closed: ' + str(ip_list_file))
        if access_file:
            op_code = self.close_file(access_file)
            if op_code == -1:
                log.event('debug', 'DEBUG: File that can\'t be closed: '+ str(access_file))
            
        # Last thing, close the output file
        log.close_log_file()
            
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
    
    def scp_handler(self, dev, mode):
        cmd='ip scp server enable'
        if mode == 'disable':
            cmd = 'no ' + cmd
            return dev.send_config_set([cmd])
        return dev.send_config_set([cmd])
    
    def enable_authorization(self, dev):
        return dev.send_config_set(['aaa authorization exec default group TACACS_PLUS local'])
        
    def disable_authorization(self, dev):
        return dev.send_config_set(['no aaa authorization exec default group TACACS_PLUS local'])
    
    
if __name__=='__main__':
    swITch()

