---------------------------- Installation and Usage ----------------------------
================================================================================


SWITCH AUTOMATION
-----------------

A python program which allows you to issue commands to Cisco switches and 
capture the output using pexpect.
Actually the cDevice.py class should work for many types of switches, but it 
depends on '>' and '#' for the expect to work.


I plan on creating more classes that support other switches, but for now there 
is just the cDevice.py class.


SETUP
-----

1. Install python (e.g. sudo apt-get install python)


2. Install pexpect (e.g. sudo apt-get install pexpect)


3. Create the following files
    (optional) iplist.txt (one IP per line)
    (optional) commands.txt (switch commands one per line)
    (optional) portDesc.txt (1st line: config t; 
        nth line: "int [intNum] , des [intDesc]")
    creds.txt (1st line: uname; 2nd line: passwd; 3rd line: enablePasswd)
    

RUN
---

E.g.


$python ./swITch.py -h (for help)

$python ./swITch.py -i 192.168.0.4 -c 'show vlan' -a creds.txt

$python ./swITch.py -e -i iplist.txt -c commands.txt -a creds.txt

$python ./swITch.py -e -i iplist.txt -p portDesc.txt -a creds.txt
