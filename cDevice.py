####################################################################
# Craig Tomkow
# December 16, 2014
#
# This is a Cisco device specific class
####################################################################
from device import device
import pexpect

class cDevice(device):
   
      
    def connect(self):
        
        loginString = 'ssh ' + self.uname + '@' + self.ip 
        #for testing on my old cisco test box...sigh
        #loginString = 'ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 ' + self.uname + '@' + self.ip
        self.child = pexpect.spawn(loginString)
        i = self.child.expect([pexpect.TIMEOUT, self.sshKey, 'assword:', pexpect.EOF])
        if i == 0: # timeout
            errstr = 'Connection to ' + self.ip + ' timed out!'
            self.kill_dev(errstr)
            self.state = -1
        elif i == 1: # new ssh key handling
            self.child.sendline('yes')
            # Missing the 'P' because some Cisco switches prompt
            # 'Password:' and some 'password:' 
            self.child.expect('assword:')
            self.child.sendline(self.passwd)
            self.child.expect('>')
            self.hostname = self.child.before.strip()
            self.state = 0
        elif i == 2: # connection successful
            self.child.sendline(self.passwd)
            self.child.expect('>')
            self.hostname = self.child.before.strip()
            self.state = 0
        elif i == 3: # Connection failed
            errstr = 'Connection to ' + self.ip + ''' failed. No SSH? Or SSH version
            mismatch?'''
            self.kill_dev(errstr)
            self.state = -1
    
    def enable(self):

        self.child.sendline('en')
        self.child.expect('assword:') # Same as above, let it this way
        self.child.sendline(self.enPasswd)
        self.child.expect('#')
        self.hostname = self.child.before.strip()

