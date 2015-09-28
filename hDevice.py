####################################################################
# Craig Tomkow
# December 16, 2014
#
# This is a HP device specific class
####################################################################

import device


class hDevice(device):


    def __init__(self, uname, passwd, ip):

        sshKey = 'Are you sure you want to continue connecting'
        loginString = 'ssh ' + str(uname) + '@' + str(ip)
        self.child = pexpect.spawn(loginString)
        i = self.child.expect([pexpect.TIMEOUT, sshKey, 'assword:'])
        if i == 0: # timeout
            errstr = 'Connection to ' + ip + ' timed out!'
            self.kill_dev(errstr)
        elif i == 1: # new ssh key handling
            self.child.sendline('yes')
            # Missing the 'P' because some switches prompt
            # 'Password:' and some 'password:' 
            self.child.expect('assword:')
            self.child.sendline(passwd)
            self.child.expect('>')  
        elif i == 2: # connection successful, send carriage return, then passwd
            self.child.sendline(passwd)
            self.child.expect('')
            self.child.sendline('\n')
            self.child.expect('>')
            
    def enable(self, uname, passwd):

        self.child.sendline('en')
        #For HP TACACS+, it expects a username and password again
        self.child.expect('Username:')
        self.child.sendline(uname)
        self.child.expect('assword:')
        self.child.sendline(passwd)
        self.child.expect('#')  

