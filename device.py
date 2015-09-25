import pexpect


class device():


    def __init__(self, uname, ip):

        sshKey = 'Are you sure you want to continue connecting'
        loginString = 'ssh ' + str(uname) + '@' + str(ip)
        self.child = pexpect.spawn(loginString)
        i = child.expect([pexpect.TIMEOUT, sshKey,         
        i = child.expect([pexpect.TIMEOUT, sshKey child.sendline(command)   

    def expect(self, response):

        child.expect(response)

    def kill_dev(self, errstr):

        print errstr
        child.terminate()   
            
