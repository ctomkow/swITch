# Craig Tomkow
# December 15, 2012
# University of Alberta, IST
# Set a config to a list of switches, specified in config files

####  !!!!!  NOTE TO SELF !!!!! ####
# When coding in this, it starts with a spawn/expect/send/expect. Then in main loop its send/expect
# Also, in the commands.txt, you need to have a blank line at the end so the loop reads the last line....i should fix that...
# When issuing commands that have lots of output which require you to hit space bar...they don't work so well. Because it needs a return.  I have not coded that.
import pexpect
import sys
import argparse
import time

class swITch:
	
	def __init__(self):
		self.argParse()	

	def argParse(self):
		parser = argparse.ArgumentParser(description='This is a config change script!')
		parser.add_argument('-e','--enabled', help='Privileged exec mode', action='store_true',required=False)
		parser.add_argument('-i','--iplist', help='Txt file with IPs',required=True)
		parser.add_argument('-c','--commands', help='Txt file with commands',required=True)
		parser.add_argument('-a', '--access', help='Txt file with uname,passwd,enablePasswd, each per line')
		parser.add_argument('-p', '--port', help='CSV (comma delimited) file that has interface number,description part1,description part2')
		args = parser.parse_args()	
		self.main(args.enabled, args.iplist, args.commands, args.access, args.port)

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
		for ip in openIPlist:
			ip = ip.rstrip('\n')	
			print ip
			child = self.loginToIP(ip, uname, passwd)
			if child == False:
				print 'Remember, a child was killed'
				pass
			else:
				print 'step 1 complete - login'
				# Enable
				if enable is True:
					self.privMode(child, enPasswd)
					print 'step 2 complete - enable'
				else:
					print '-e Enable flag not set!'
					
				# Parse commands from file
				for command in openCommands:
					command = command.rstrip('\n')
					self.send(child, command)	
					i = child.expect(['#', pexpect.EOF, pexpect.TIMEOUT])
					if i == 0:
						print '0:' +  child.before
					elif i == 1:
						print '1:' +  child.before
					elif i == 2:
						print '2: ' + child.before
						#self.killChild(child, 'sw timed out')
					# Write response to file
					self.writeResponse(openOutputFile, child.before)
					
		# Cleanup
		self.closeFile(openOutputFile)
		self.closeFile(openCommands)
		self.closeFile(openIPlist)
		self.closeFile(openAccess)

#------------------ Methods ------------------------------------
# All these methods seem to work fine...even the ssh handling
#--------------------------------------------------------------
	def getFile(self, file, operation):
		f = open(file, operation)
		return f

	def closeFile(self, file):
		file.close()

	def loginToIP(self, ip, uname, passwd):
		loginString = 'ssh ' + str(uname) + '@' + str(ip)
		print loginString

		# New SSH key handling
		sshKey = 'Are you sure you want to continue connecting'
		child = pexpect.spawn(loginString)
		i = child.expect([pexpect.TIMEOUT, sshKey, 'Password:'])
		if i == 0: # Timeout
			errstr = 'Connection to ' + ip + ' timed out!'
			self.killChild(child, errstr)
			return False
		elif i == 1: # ssh key	
			print('new ssh key')
			child.sendline('yes')
			child.expect('Password:')
			child.sendline(passwd)
			child.expect('>')
			return child 	
		elif i == 2: # connect successful, provide passwd
			print 'step 0 complete - loginToIP method'
			child.sendline(passwd)
			child.expect('>')
			return child	
		else:
			print 'loginToIP error!'

	def privMode(self, child, passwd):
		self.send(child, 'en')
		self.expect(child, 'Password:')
		self.send(child, passwd)
		self.expect(child, '#')
				
	def expect(self, child, response):
		child.expect(response)

	def send(self, child, command):	
		child.sendline(command)
		
	def writeResponse(self, file, response):
		file.write(response)
	
	def killChild(self, child, errstr):
		print errstr
		print child.before, child.after
		child.terminate()

if __name__=="__main__":
	swITch()
