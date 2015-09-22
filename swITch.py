#!/usr/bin/env python
####################################################################################
# Craig Tomkow
# April 13, 2015
#
# Set a config to a list of switches, specified in config files
#
#  !!!!!  NOTE TO SELF !!!!! 
# In the send commands loop, its send/expect
# Use 'term len 0' as the first command so any output displays all and you don't have to hit space bar
####################################################################################
import pexpect
import sys
import argparse
import cDevice
import hDevice
import devThread

class swITch:
	def __init__(self):
		# Arg Parsing
		parser = argparse.ArgumentParser(description='This program can log into devices using expect, issue commands, and capture the result.')
		parser.add_argument('-e','--enable', help='Privileged exec mode', action='store_true',required=False)
		parser.add_argument('-i','--iplist', help='Txt file with one IP per line. Or a single IP in single quotes.',required=True)
		parser.add_argument('-c','--commands', help='Txt file with one device command per line. Or a single command in single quotes.',required=False)
		parser.add_argument('-a', '--auth', help='Txt file with uname on first line,passwd on second,enablePasswd on third',required=True)
		parser.add_argument('-p', '--portlist', help='File that has interface and port descriptions seperated by a comma per line. "int gi1/0/1 , des C001".  Tip, use an excel sheet to generate the list.',required=False)
		args = parser.parse_args()
	
		self.main(args.enable, args.iplist, args.commands, args.auth, args.portlist)


	#-------------------- Main Loop ----------------------------------

	def main(self, enable, iplist, commands, auth, portlist):
		
	
		# Attempt to get file descriptors for each provided txt file
		openIPlist = self.openFile(iplist, 'r')	
		if openIPlist == -1:
			print 'Hokay, assuming this is an IP not a file'
			openIPlist = [iplist]
		
		if commands:
			openCommands = self.openFile(commands, 'r')
			if openCommands == -1:
				print 'Hokay, assuming this is a cmd not a file'
				openCommands = [commands]

		if portlist:
			openPortList = self.openFile(portlist, 'r')

		openOutputFile = self.openFile('output.txt', 'a')	

		openAccess = self.openFile(auth, 'r')
		
		# Extract uname and passwd's
		uname = openAccess.readline().rstrip('\n')
		passwd = openAccess.readline().rstrip('\n')
		enPasswd = openAccess.readline().rstrip('\n')

		# Initialize command, IP, and device lists
		QueueOfCommands = []
                QueueOfIPs      = []
                QueueOfDevices  = []

		# Add 'term length 0' to beginning of cmd list. THIS IS CISCO SPECIFIC, I SHOULD MOVE THIS CODE SOMEWHERE MORE MEANINGFUL!
		QueueOfCommands.insert(0, 'term length 0')

		# Parse commands from file
		if portlist: 
			for command in openPortList:
				portCommand = command.rstrip('\n')
				if portCommand.find(',') == -1:
					print portCommand
					QueueOfCommands.append(portCommand)
				else:
					portCommandArray = portCommand.split(",")
					portInt = portCommandArray[0]
					portInt = portInt.replace('\t', "")
					print portInt
					portDesc = portCommandArray[1]
					portDesc = portDesc.replace('\t', "")
					print portDesc
					QueueOfCommands.append(portInt)
					QueueOfCommands.append(portDesc)
					print QueueOfCommands
		if commands:	
			for command in openCommands:
				command = command.rstrip('\n')
				QueueOfCommands.append(command)
			
# Merged old code
#		for command in openCommands:
#			command = command.rstrip('\n')
#			QueueOfCommands.append(command)
		
                # Parse IP's into a list
#                for ip in openIPlist:
#                        ip = ip.rstrip('\n')
#                        QueueOfIPs.append(ip)
                        
                # INSERT THREADING LOGIC HERE! Create a thread by calling devThread.py.  That class will have all the cDevice.py calls that are currently below here.
#                devThread.devThread(uname, passwd, enPasswd, QueueOfIPs.popleft())
# End merged old code 

                 
		# Parse IPs from file
		####### Add in here parsing to differentiate between types of switches, then have different classes for each different switch
                ########## Most of this creating a device object stuff is getting moved to devThread.py

		
		for ip in openIPlist:
			ip = ip.rstrip('\n')	
			
			# Object   filename.classname
			ciscoDev = cDevice.cDevice(uname, passwd, ip)

			if enable:
				print enPasswd
				ciscoDev.enable(enPasswd)
			else:
				print '***** Warning! -e flag not set. Not all commands may function properly *****'
					
			
			for cmd in QueueOfCommands:			
				ciscoDev.send(cmd)

				if not enable:
					i = ciscoDev.expect(['>', pexpect.EOF, pexpect.TIMEOUT])
				else:
					i = ciscoDev.expect(['#', pexpect.EOF, pexpect.TIMEOUT])

				if i == 0: # command sent successfully
					print '###', cmd
					print ciscoDev.output()
					self.writeTo(openOutputFile, ciscoDev.output())
				elif i == 1: # EOF
					pass
					print ciscoDev.output()
				elif i == 2: # Timeout
					pass
					print ciscoDev.output()

			# Cleanup
			ciscoDev.killDev('Device is done it\'s work')
													
		# Cleanup
		self.closeFile(openOutputFile)
		if commands:
			self.closeFile(openCommands)
		if portlist:
			self.closeFile(openPortList)
		self.closeFile(openIPlist)
		self.closeFile(openAccess)
			
#------------------ Methods -----------------------------------------
# Handling files. Add exception handling in these methods. Should
# these methods be in a class? There is already the python file
# class that these methods call...
#--------------------------------------------------------------------
	def openFile(self, file, operation):
		try:
			f = open(file, operation)
		except IOError:
			print 'Can\'t open file because I can\'t find file to open.'
			return -1
		return f

	def closeFile(self, file):
		try:
			file.close()
		except AttributeError:
			print 'Can\'t close file due to no file attributes'

	def writeTo(self, file, str):
		file.write(str)
	
if __name__=="__main__":
	swITch()
