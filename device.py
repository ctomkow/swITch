import pexpect


class device():


    def __init__(self):
        pass
                    
    def expect(self, response):

        return self.child.expect(response, timeout=10)
    
    def send(self, command):

        self.child.sendline(command)

    def kill_dev(self, errstr):

        print errstr
        self.child.terminate()  
    
    def output(self):

        return self.child.before