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

class swITch:
	def __init__(self):
		# Arg Parsing
		parser = argparse.ArgumentParser(description='This program can log into devices using expect, issue commands, and capture the result.')
		parser.add_argument('-e','--enable', help='Privileged exec mode', action='store_true',required=False)
		parser.add_argument('-i','--iplist', help='Txt file with one IP per line',required=True)
		parser.add_argument('-c','--commands', help='Txt file with one device command per line',required=True)
		parser.add_argument('-a', '--access', help='Txt file with uname on first line,passwd on second,enablePasswd on third')
		parser.add_argument('-p', '--port', help='#NOT IMPLEMENTED YET# CSV (comma delimited) file that has interface number,description part1,description part2')
		args = parser.parse_args()
	
		self.main(args.enable, args.iplist, args.commands, args.access, args.port)


	#-------------------- Main Loop ----------------------------------

	def main(self, enable, iplist, commands, access, port):
			
		#Get file descriptors for each provided txt file
		openIPlist = self.openFile(iplist, 'r')	
		openCommands = self.openFile(commands, 'r')
		openOutputFile = self.openFile('output.txt', 'a')	
		openAccess = self.openFile(access, 'r')

		# Extract uname and passwd's
		uname = openAccess.readline().rstrip('\n')
		passwd = openAccess.readline().rstrip('\n')
		enPasswd = openAccess.readline().rstrip('\n')

		# Initialize commands list
		QueueOfCommands = []

		# Parse commands from file
		for command in openCommands:
			command = command.rstrip('\n')
			QueueOfCommands.append(command)
			
		# Parse IPs from file
		####### Add in here parsing to differentiate between types of switches, then have different classes for each different switch
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
				i = ciscoDev.expect(['#', pexpect.EOF, pexpect.TIMEOUT])
				if i == 0: # command sent successfully
					print ciscoDev.output()
					self.writeTo(openOutputFile, ciscoDev.output())
				elif i == 1: # EOF
					pass
					rint ciscoDev.output()
				elif i == 2: # Timeout
					pass
					print ciscoDev.output()

			# Cleanup
			ciscoDev.killDev('Device is done it\'s work')
													
		# Cleanup
		self.closeFile(openOutputFile)
		self.closeFile(openCommands)
		self.closeFile(openIPlist)
		self.closeFile(openAccess)
			
#------------------ Methods -----------------------------------------
# Handling files. Add exception handling in these methods. Should
# these methods be in a class? There is already the python file
# class that these methods call...
#--------------------------------------------------------------------
	def openFile(self, file, operation):
		f = open(file, operation)
		return f

	def closeFile(self, file):
		file.close()

	def writeTo(self, file, str):
		file.write(str)
	
if __name__=="__main__":
	swITch()
