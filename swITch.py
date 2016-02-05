#!/usr/bin/env python

# Craig Tomkow
# February 5, 2016
#
# Set a config to a list of switches, specified in config files
#
#  !!!!!  NOTE TO SELF !!!!! 
# In the send commands loop, its send/expect

import sys
import argparse

import pexpect

import cDevice
import hDevice
import dDevice

import devThread


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
    def main(self, enable, iplist, commands, auth, portlist):      
    
        ##### FILE STUFF #####
    
        # Attempt to get file descriptors for each provided txt file
        if iplist is not None:
            openIPlist = self.open_file(iplist, 'r')
            if openIPlist == -1:
                print 'Hokay, assuming this is an IP not a file'
                openIPlist = [iplist] 
        if commands is not None:
            openCommands = self.open_file(commands, 'r')
            if openCommands == -1:
                print 'Hokay, assuming this is a cmd not a file'
                openCommands = [commands]
        if portlist is not None:
            openPortList = self.open_file(portlist, 'r')
        openOutputFile = self.open_file('output.txt', 'a')   
        openAccess = self.open_file(auth, 'r')
        
        uname = openAccess.readline()
        uname = self.strip_new_line(uname)      
        passwd = openAccess.readline()
        passwd = self.strip_new_line(passwd)       
        enPasswd = openAccess.readline()
        enPasswd = self.strip_new_line(enPasswd)

        # Initialize command, IP, and device lists
        QueueOfCommands = []
        QueueOfIPs      = []
        QueueOfDevices  = []

        # Parse port description file
        if portlist is not None: 
            for portCommand in openPortList:
                portCommand = self.strip_new_line(portCommand)
                if portCommand.find(',') == -1:
                    QueueOfCommands.append(portCommand)
                else:
                    portCommandArray = portCommand.split(',')
                    portInt = portCommandArray[0]
                    portInt = portInt.replace('\t', '')
                    portDesc = portCommandArray[1]
                    portDesc = portDesc.replace('\t', '')
                    QueueOfCommands.append(portInt)
                    QueueOfCommands.append(portDesc)
        # Parse cli commands
        if commands is not None:    
            for command in openCommands:
                command = self.strip_new_line(command)
                QueueOfCommands.append(command) 
        # Parse IPs from file
        if iplist is not None:
            for ip in openIPlist:
                ip = self.strip_new_line(ip)
                QueueOfIPs.append(ip)
        
        ##### SWITCH CONNECTION AND EXECUTION LOGIC #####                       
        for ip in QueueOfIPs:
            # IF CISCO, DO THIS
            if ip.find('cisco') is not -1:
                QueueOfCommands.insert(0, 'term length 0')
                ip = ip.rstrip(',cisco')
                #Object  filename.classname
                dev = cDevice.cDevice(uname, passwd, ip, enPasswd, 'cisco')
                dev.connect()
            # IF HP, DO THIS
            elif ip.find('hp') is not -1:
                QueueOfCommands.insert(0, 'term length 1000')
                ip = ip.rstrip(',hp')
                dev = hDevice.hDevice(uname, passwd, ip, enPasswd, 'hp') 
                dev.connect()
            # IF DELL, DO THIS
            elif ip.find('dell') is not -1:
                QueueOfCommands.insert(0, 'term length 0')
                ip = ip.rstrip(',dell')
                # Object  filename.classname
                dev = dDevice.dDevice(uname, passwd, ip, enPasswd, 'dell')
                dev.connect()
            
            if dev.state == 0: # Continue because object is good
                if enable:
                    dev.enable()
                else:
                    print """***** Warning! -e flag not set. Not all commands may
                    function properly *****"""
                for cmd in QueueOfCommands: # Run all commands on this device
                    print QueueOfCommands
                    dev.send(cmd)
                    if not enable:
                        i = dev.expect(['>', pexpect.EOF, pexpect.TIMEOUT])
                        print 'NO enable'
                    else:
                        i = dev.expect(['#', pexpect.EOF, pexpect.TIMEOUT])
                        print 'YES enable'
                    if i == 0: # command sent successfully
                        print 'cmd:', cmd
                        print dev.output()
                        self.write_to(openOutputFile, dev.output())
                    elif i == 1: # EOF
                        print 'EOF when expecting from: ' + cmd
                    elif i == 2: # Timeout
                        print 'Timeout when expecting from: ' + cmd
            # Device ip cleanup
            QueueOfCommands.pop(0)
            dev.state = -1 # Not needed as I am killing the child next...
            dev.kill_dev('Device is done it\'s work') # Kill connection         
                                                    
        # Close all files if they are open
        self.close_file(openOutputFile)
        if commands:
            self.close_file(openCommands)
        if portlist:
            self.close_file(openPortList)
        self.close_file(openIPlist)
        self.close_file(openAccess)
            
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

