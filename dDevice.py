####################################################################
# Craig Tomkow
# December 4, 2015
#
# This is a Dell device specific class
####################################################################

import device
import pexpect

class dDevice(device.device):


    def __init__(self, uname, passwd, ip):

        sshKey = 'Are you sure you want to continue connecting'
        loginString = 'ssh ' + uname + '@' + ip
        self.child = pexpect.spawn(loginString)
        i = self.child.expect([pexpect.TIMEOUT, sshKey, 'assword:', pexpect.EOF])
        if i == 0: # timeout
            errstr = 'Connection to ' + ip + ' timed out!'
            self.kill_dev(errstr)
            self.state = -1
        elif i == 1: # new ssh key handling
            self.child.sendline('yes')
            # Missing the 'P' because some Cisco switches prompt
            # 'Password:' and some 'password:' 
            self.child.expect('assword:')
            self.child.sendline(passwd)
            self.child.expect('>')  
        elif i == 2: # connection successful
            self.child.sendline(passwd)
            self.child.expect('>') 
        elif i == 3: # Connection failed
            errstr = 'Connection to ' + ip + ' failed. SSH version mismatch?'
            self.kill_dev(errstr)
            self.state = -1
            
    def enable(self, passwd):

        self.child.sendline('en')
        self.child.expect('assword:') # Same as above, let it this way
        self.child.sendline(passwd)
        self.child.expect('#')  

