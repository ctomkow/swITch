####################################################################
# Craig Tomkow
# December 16, 2014
#
# This is a Cisco device specific class
####################################################################

import pexpect

class cDevice():
	def __init__(self, uname, passwd, ip):
		sshKey = 'Are you sure you want to continue connecting'
		loginString = 'ssh ' + str(uname) + '@' + str(ip)
		self.child = pexpect.spawn(loginString)
		i = self.child.expect([pexpect.TIMEOUT, sshKey, 'assword:'])
		if i == 0: # timeout
			errstr = 'Connection to ' + ip + ' timed out!'
			self.killDev(errstr)
		elif i == 1: # new ssh key handling
			self.child.sendline('yes')
			# Missing the 'P' because some Cisco switches prompt 'Password:' and some 'password:' 
			self.child.expect('assword:')
			self.child.sendline(passwd)
			self.child.expect('>')	
		elif i == 2: # connection successful
			self.child.sendline(passwd)
			self.child.expect('>')
					
	def expect(self, response):
		return self.child.expect(response, timeout=10)
	
	def send(self, command):
		self.child.sendline(command)

	def killDev(self, errstr):
		print errstr
		self.child.terminate()	
			
	def enable(self, passwd):
		self.child.sendline('en')
		#same as above, leave it this way
		self.child.expect('assword:')
		self.child.sendline(passwd)
		self.child.expect('#')	
	
	def output(self):
		return self.child.before

