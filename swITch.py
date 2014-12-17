# Craig Tomkow
# December 15, 2012
# University of Alberta, IST
# Set a config to a list of switches, specified in config files
# A minor change for git
####  !!!!!  NOTE TO SELF !!!!! ####
# When coding in this, it starts with a spawn/expect/send/expect. Then in main loop its send/expect
# When issuing commands that have lots of output which require you to hit space bar...they don't work so well (it times out). Because it needs a return.  I have not coded that.
# Use 'term len 0' as the first command so any output displays all and you don't have to hit space bar
import pexpect
import sys
import argparse
import cDevice

class swITch:
	
	def __init__(self):
		# Arg Parsing
		parser = argparse.ArgumentParser(description='This is a config change script!')
		parser.add_argument('-e','--enable', help='Privileged exec mode', action='store_true',required=False)
		parser.add_argument('-i','--iplist', help='Txt file with IPs',required=True)
		parser.add_argument('-c','--commands', help='Txt file with commands',required=True)
		parser.add_argument('-a', '--access', help='Txt file with uname,passwd,enablePasswd, each per line')
		parser.add_argument('-p', '--port', help='CSV (comma delimited) file that has interface number,description part1,description part2')
		args = parser.parse_args()
	
		self.main(args.enable, args.iplist, args.commands, args.access, args.port)


	#-------------------- Main Loop ----------------------------------

	def main(self, enable, iplist, commands, access, port):
			
		#Get file descriptors for each provided txt file
		openIPlist = self.getFile(iplist, 'r')	
		openCommands = self.getFile(commands, 'r')
		openOutputFile = self.getFile('output.txt', 'w')	
		openAccess = self.getFile(access, 'r')

		# Extract uname and passwd's
		uname = openAccess.readline().rstrip('\n')
		passwd = openAccess.readline().rstrip('\n')
		enPasswd = openAccess.readline().rstrip('\n')

		# Parse IPs from file
		####### Add in here parsing to differentiate between types of switches, then have different classes for each different switch
		for ip in openIPlist:
			ip = ip.rstrip('\n')	
			print ip

			# Object   filename.classname
			ciscoDev = cDevice.cDevice(uname, passwd, ip)

			if enable:
				ciscoDev.enable(enPasswd)
			else:
				print '***** Warning! -e flag not set. Not all commands may function properly *****'
					
			# Parse commands from file
			for command in openCommands:
				command = command.rstrip('\n')
				ciscoDev.send(command)
				i = ciscoDev.expect(['#', pexpect.EOF, pexpect.TIMEOUT])
				if i == 0:
					#output = ciscoDev.before
					print '0:' 
					print ciscoDev.output()
					#self.writeOut(openOutputFile, child.before)
				elif i == 1:
					output = ciscoDev.before
					print '1:' + output
				elif i == 2:
					output = ciscoDev.before
					print '2: ' + output
									
		# Cleanup
		self.closeFile(openOutputFile)
		self.closeFile(openCommands)
		self.closeFile(openIPlist)
		self.closeFile(openAccess)
			
#------------------ Methods -----------------------------------------
# All these methods seem to work fine...
#--------------------------------------------------------------------
	def getFile(self, file, operation):
		f = open(file, operation)
		return f

	def closeFile(self, file):
		file.close()

	def writeOut(self, file, str):
		file.write(str)
	
if __name__=="__main__":
	swITch()
