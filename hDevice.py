####################################################################
# Craig Tomkow
# February 5, 2016
#
# This is a HP device specific class
####################################################################
from device import device
import pexpect

class hDevice(device):

        
    def connect(self):
        
        loginString = 'ssh ' + str(self.uname) + '@' + str(self.ip)
        self.child = pexpect.spawn(loginString)
        i = self.child.expect([pexpect.TIMEOUT, self.sshKey, 'assword:'])
        if i == 0: # timeout
            errstr = 'Connection to ' + self.ip + ' timed out!'
            self.kill_dev(errstr)
            self.state = False
        elif i == 1: # new ssh key handling
            self.child.sendline('yes')
            # Missing the 'P' because some switches prompt
            # 'Password:' and some 'password:' 
            self.child.expect('assword:')
            self.child.sendline(self.passwd)
            self.child.expect('>')
            self.expectString = ('>')
            self.state = True
        elif i == 2: # connection successful, send carriage return, then passwd
            self.child.sendline(self.passwd)
            self.child.expect('any key to continue')
            self.child.sendline('\n')
            self.child.expect('>')
            self.expectString = ('>')
            self.state = True
            print 'logged in'
        elif i == 3: # Connection failed
            errstr = 'Connection to ' + self.ip + ''' failed. No SSH? SSH version
            mismatch? Incorrect IP address?'''
            self.kill_dev(errstr)
            self.state = False
            
    def enable(self):

        self.child.sendline('en')
        #For HP TACACS+/radius, it expects a username and password again
        self.child.expect('ame:')
        self.child.sendline(self.uname)
        self.child.expect('assword:')
        self.child.sendline(self.passwd)
        self.child.expect('#')
        self.expectString = ('#')
        self.enabled = True

