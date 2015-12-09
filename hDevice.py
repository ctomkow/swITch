####################################################################
# Craig Tomkow
# December 16, 2014
#
# This is a HP device specific class
####################################################################
from device import device
import pexpect

class hDevice(device):

        
    def connect(self):
        
        loginString = 'ssh -1 ' + str(self.uname) + '@' + str(self.ip)
        self.child = pexpect.spawn(loginString)
        i = self.child.expect([pexpect.TIMEOUT, self.sshKey, 'assword:'])
        if i == 0: # timeout
            errstr = 'Connection to ' + self.ip + ' timed out!'
            self.kill_dev(errstr)
            self.state = -1
        elif i == 1: # new ssh key handling
            self.child.sendline('yes')
            # Missing the 'P' because some switches prompt
            # 'Password:' and some 'password:' 
            self.child.expect('assword:')
            self.child.sendline(self.passwd)
            self.child.expect('>')
            self.state = 0
        elif i == 2: # connection successful, send carriage return, then passwd
            self.child.sendline(self.passwd)
            self.child.expect('Press any key to continue')
            self.child.sendline('\n')
            self.child.expect('>')
            self.state = 0
            print 'logged in'
        elif i == 3: # Connection failed
            errstr = 'Connection to ' + self.ip + ' failed. SSH version mismatch?'
            self.kill_dev(errstr)
            self.state = -1
            
    def enable(self):

        self.child.sendline('en')
        #For HP TACACS+, it expects a username and password again
        self.child.expect('ame:')
        self.child.sendline(self.uname)
        self.child.expect('assword:')
        self.child.sendline(self.passwd)
        self.child.expect('#')  

