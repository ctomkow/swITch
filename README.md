# Installation and Usage 

## SWITCH AUTOMATION

A python program which allows you to issue commands to switches and 
capture the output using pexpect.


### DEVICE SUPPORT

*Cisco switches

*HP switches


Actually the cDevice.py class should work for many types of switches that
behave similar to Cisco switches when you log in.


### KNOWN BUGS

There is a known bug with expecting on '#'.  If you have this anywhere 
in the config (e.g. port label, or HP 'show runn' then expect hits the 
delimiter and stops.  Consequently you don't get the full output.  I am
aware and will work on a fix when I have some time.


### FUTURE DEVELOPMENT

I plan on creating more classes that support other switches like Dell, Juniper, etc.
I am also planning on creating an APC UPS class for managing APC UPS's over SSH.
I found that cDevice.py works quite well for it however.


Multi-threading.  I am planning to make this multi-threaded so it will be
more efficient at pushing out changes to many devices at once.

### SETUP

1. Install python (e.g. 'sudo apt-get install python')


2. Install pexpect (e.g. 'sudo apt-get install pexpect')


3. Create the following files

  * (optional) iplist.txt (one IP address and device type per line)


    [IP_ADDRESS1,DEVICE_TYPE]

    [IP_ADDRESS1,DEVICE_TYPE]

'''
    172.30.30.30,hp

    172.30.30.30,cisco
'''

    ___

  * (optional) cli.txt (one command per line)


    [ENTER_CONFIG_MODE]

    [COMMAND_2]

    [COMMAND_3]


'''
    config t

    show version

    show interfaces status
'''

    ___

  * (optional) portDesc.txt (1st line: config mode, Nth line: int num, int des)


    [ENTER_CONFIG_MODE]

    [INTERFACE_CMD INT_NUM_1], [INTERFACE_DESC_CMD_1, INT_DES_1]

    [INTERFACE_CMD INT_NUM_2], [INTERFACE_DESC_CMD_2, INT_DES_2]
    .

    .

    [INTERFACE_CMD INT_NUM_N], [INTERFACE_DESC_CMD_N, INT_DES_N]

'''
    config t
    interface gi0/1, description Port C001 : 1-52

    interface gi0/2, description Port C002 : 1-53

    .

    .

    interface gi0/48, description Port C048 : 1-87
'''

    ___

  * auth.txt (1st line: uname; 2nd line: passwd; 3rd line: enablePasswd)


    [USERNAME]

    [PASSWORD]

    [ENABLE_PASSWORD]


    joe

    password

    enableME
    


### RUN

E.g.


'$python ./swITch.py -h (for help)'


'$python ./swITch.py -i '192.168.0.4,cisco' -c 'show vlan' -a auth.txt'


'$python ./swITch.py -e -i iplist.txt -c cli.txt -a auth.txt'


'$python ./swITch.py -e -i iplist.txt -p portDesc.txt -a auth.txt'
