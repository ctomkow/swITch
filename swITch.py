#!/usr/bin/env python

# Craig Tomkow
# August 4, 2016
#
# Send a config to a list of switches, specified in config files. Uses netmiko
# for handling switch interaction.


import datetime
import logger
import device_connector
import config
import argparse
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter


class swITch:


    def __init__(self):

        # Arg Parsing
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, add_help=False,
            description="""
            This program logs into network devices over SSH utilizing netmiko/paramiko,
            issue commands, and sends STOUT to output.log file. Need to minimally
            define login credentials in a conf.yaml file.\n
            Two typical examples:\n
            swITch.py (specifying device details in the conf.yaml file)
            ... or ...
            swITch.py -ei 172.30.30.30 -t cisco_ios -c 'show version'""")
      
        optFlags = parser.add_argument_group('General flags')
        optFlags.add_argument('-e', '--enable', action='store_true', required=False,
            help="""Privileged exec mode.""")
        optFlags.add_argument('-h', '--help', action='help', 
            help="""show this help message and exit""")
        optFlags.add_argument('-p', '--port', required=False, action='store_true', 
            help="""Indicating that port descriptions are in the yaml file
            instead of general config commands. 'int gi1/0/1,des C001'""")
           
        overFlags = parser.add_argument_group('Override (parts of) configuration file')
        overFlags.add_argument('-i', '--ip', required=False, metavar='\b',
            help="""A single IP with device type. e.g. '172.30.30.30'""")
        overFlags.add_argument('-t', '--type', required=False, metavar='\b',
            help="""Define the device type. e.g. 'cisco_ios'""")
        overFlags.add_argument('-c', '--cmd', required=False, metavar='\b',
            help="""A single command. e.g. 'show version'""")
        overFlags.add_argument('-f', '--file', required=False, metavar='\b',
            help="""File name that will be transfered to device.""")
            
        outputFlags = parser.add_argument_group('Logging level (debug --> verbose --> default --> log-only --> suppress)')
        outputFlags.add_argument('-d', '--debug', required=False, action='store_true',
            help="""Prints all additional session information.""")
        outputFlags.add_argument('-l', '--log-only', action='store_true', required=False,
            help="""Send only the device STDOUT to log file.""")
        outputFlags.add_argument('-s', '--suppress', action='store_true', required=False,
            help="""Suppress all STDOUT, also no log file entries.""")
        outputFlags.add_argument('-v', '--verbose', action='store_true', required=False,
            help="""Prints out additional cli information.""")
        outputFlags.add_argument('-z', '--zomg', action='store_true', required=False,
            help=argparse.SUPPRESS)
        
        args = parser.parse_args()
        
        self.main(args.cmd, args.debug, args.enable, args.ip, args.type, args.log_only,
            args.port, args.suppress, args.file, args.verbose, args.zomg)

    #--------------------------------------------------------------------------#
    #                               Main Loop                                  #
    #--------------------------------------------------------------------------#
    def main(self, cli_cmd, debug, enable, cli_ip, cli_type, log_only, int_desc, suppress, file_image, verbose, zomg):      
    
        ### LOGGING STUFF ###
        if debug:
            log = logger.logger("debug")
        elif verbose:
            log = logger.logger("verbose")
        elif log_only:
            log = logger.logger("log_only")
        elif suppress:
            log = logger.logger("suppress")
        else: # Default output, no flags needed for this
            log = logger.logger("info")
    
        # Initialize IP and command lists
        list_of_IPs      = []
        list_of_commands = []
    
        if cli_ip:
            log.event('debug', 'DEBUG: Assuming "' + cli_ip + '" is a valid IP')
            list_of_IPs = [cli_ip]
        if cli_cmd:
            log.event('debug', 'DEBUG: Assuming "' + cli_cmd + '" is a valid command')
            list_of_commands = [cli_cmd]
        if cli_type:
            log.event('debug', "DEBUG: Assuming " + cli_type + " is a valid device type")
#        if port_list:
#            port_list_file = self.open_file(port_list, 'r')
#            if port_list_file == -1:
#                log.event('debug', 'DEBUG: File name that can\'t be opened: ' + port_list)
#                raise IOError('Can\'t open port list file')

#        # Parse port description file
#        if port_list: 
#            for raw_cmd in port_list_file:
#                cmd = self.strip_new_line(raw_cmd)
#                if cmd.find(',') == -1:
#                    list_of_commands.append(cmd)
#                else:
#                    cmd_array = cmd.split(',')
#                    interface_cmd = cmd_array[0]
#                    interface_cmd = interface_cmd.replace('\t', '')
#                    description_cmd = cmd_array[1]
#                    description_cmd = description_cmd.replace('\t', '')
#                    list_of_commands.append(interface_cmd)
#                    list_of_commands.append(description_cmd)

        # Check whether general device config is being provided, or interface descriptions
        # and set flags appropriately to be fed into the config class so it knows
        if int_desc:
            gen_conf_state = False
            int_desc_state = True
        else:
            gen_conf_state = True
            int_desc_state = False
            
        # Instantiate config class singleton
        try:
            config_singleton = config.config(gen_conf_state, int_desc_state)
        except ValueError:
            log.event('info', "WARNING: Could not read yaml config file! Ensure it is named 'conf.yaml'")

        #CLI overriding the config file for the IP, command, and device type
        if cli_ip:
            config_singleton.set_a_device_group(cli_ip, cli_cmd, cli_type)

        ### MAIN LOOP TO PARSE THROUGH ALL DEVICE GROUPS
        while config_singleton.get_config_length() > 0:
            
            # Get details of a device grouping
            device_type, list_of_IPs, list_of_commands = config_singleton.get_a_device_group()
            
            ### Pre-processing of interface description list into proper format (should be a put in a function)
            if int_desc_state:
                for cmd in list_of_commands:
                    tmp_list.append('conf t')
                    cmd_array = cmd.split(',')
                    interface_cmd = cmd_array[0]
                    interface_cmd = interface_cmd.replace('\t', '')
                    description_cmd = cmd_array[1]
                    description_cmd = description_cmd.replace('\t', '')
                    tmp_list.append(interface_cmd)
                    tmp_list.append(description_cmd)
                list_of_commands = tmp_list
        
            # All Device IPs of that specific group
            for ip in list_of_IPs:

                ### SWITCH CONNECTION LOGIC ###  
                try:
                    dev = device_connector.device_connector(ip, config_singleton.get_username(),
                    config_singleton.get_password(), device_type, config_singleton.get_enable_password())
                except ValueError:
                    log.event('info', "WARNING: Could not connect to " + ip + 
                    "\nWARNING: Unsupported device or missing device type. Skipping it!")
                    continue #skips the rest of the for loop for this one device
                log.event('info', "SSH connection open to " + dev.ip)
                if enable:
                    log.event('verbose', dev.enable())
                    
                ### COMMAND EXECUTION LOGIC ###
                if gen_conf_state or int_desc_state:
                    for cmd in list_of_commands:
                        log.event('verbose', dev.find_prompt() + cmd)
                        log.event('log_only', dev.send_command(cmd)) # send command
                        log.event('debug', "DEBUG PROMPT:" + dev.find_prompt())
                    dev.disconnect()
                    log.event('info', "SSH connection closed to " + ip)

                ### FILE TRANSFER LOGIC ###
                if file_image:
                    log.event('debug', "DEBUG PROMPT:" + dev.enable_scp())
                    if zomg:
                        log.event('debug', "DEBUG PROMPT:" + dev.enable_authorization())
                    log.event('info', "Start transfer process: " + str(datetime.datetime.now()))
                    log.event('info', dev.transfer_file(file_image))  
                    log.event('info', "End transfer process " + str(datetime.datetime.now()))
                    log.event('debug', "DEBUG PROMPT:" + dev.disable_scp())
                    if zomg:
                        log.event('debug', "DEBUG PROMPT:" + dev.disable_authorization())

        ### CLEANUP ###     
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
    
    
if __name__=='__main__':
    swITch()

