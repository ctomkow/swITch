####################################################################
# Craig Tomkow
# December 4, 2015
#
# This is a the base device class.  These functions are inherited in each
# sub device class
####################################################################


class device():


    state = 0
    uname = ''
    passwd = ''
    ip = ''
    enPasswd = ''
    type = ''
    sshKey = 'Are you sure you want to continue connecting'
    expectString = ''
    
    def __init__(self, uname, passwd, ip, enPasswd, type):
        
        self.uname = uname
        self.passwd = passwd
        self.ip = ip
        self.enPasswd = enPasswd
        self.type = type
                    
    def expect(self, response):

        return self.child.expect(response, timeout=10)
    
    def send(self, command):

        self.child.sendline(command)

    def kill_dev(self, errstr):

        print errstr
        self.child.terminate()  
    
    def output(self):

        return self.child.before