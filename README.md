# Installation and Usage 

## NETWORK DEVICE AUTOMATION

A python program which allows you to push commands to network devices.  It
can then dump the output to a file for later analysis.


### DEVICE SUPPORT

* Cisco switches

* HP switches


Note: the cDevice.py class (for Cisco devices) should work for many types of switches that
behave similar to Cisco IOS.


### KNOWN BUGS

* There is a known bug with expecting on '#'.  If you have a hashtag anywhere 
in the config (e.g. port label, or HP 'show runn') then expect hits the 
delimiter and stops.  Consequently you don't get the full output.  I have branch open and I am working on fixing it.


### FUTURE DEVELOPMENT

* I plan on creating more classes that support other devices like Dell, Juniper, etc.
* I am also planning on creating an APC UPS class for managing APC UPS's over SSH. I found that cDevice.py works quite well for it however.
* Multi-threading.  I am planning to make this multi-threaded so it will be more efficient at pushing out changes to many devices at once.
* Allowing to specify which section of config in the cli.config file gets pushed out to certain IP ranges.  Then you can list all the config for various devices (e.g. multi-vendor devices). This will go well together with listing all the IPs in ip.list file.
* Enabling IP ranges using regex in ip.list
* Enable the use of certificates so you don't need to rely on username and passwords sitting in a text file.
* Proper display of program output.  E.g. -v -vv -vvv
* In general, better error handling.

### SETUP

1. Install python 
  * `sudo apt-get install python`


2. Install pexpect
  * `sudo apt-get install pexpect`


3. Create the following files

  1. `ip.list` (1<sup>st</sup> - n<sup>th</sup> line: `IP address`,`device type`)


    ```
    172.30.30.30,hp
    172.30.30.31,cisco
    ```


  2. `cli.config` (1<sup>st</sup> - n<sup>th</sup> line: `cli command`)


    ```
    config t
    show interfaces
    ```


  3. `port.desc` (1<sup>st</sup> line: `config t`, 2<sup>nd</sup> - n<sup>th</sup> line: `interface`,`port description`)


    ```
    config t
    interface gi0/1,description Port C001 : 1-52
    interface gi0/2,description Port C002 : 1-53
    .
    .
    .
    interface gi0/48,description Port C048 : 1-87
    ```


  4. `auth.txt` (1<sup>st</sup> line: `username`, 2<sup>nd</sup> line: `password`, 3<sup>rd</sup> line: `enable password`)


    ```
    joe
    password
    enableME
    ```


### RUN

Examples


`$python ./swITch.py -h`


`$python ./swITch.py -i '192.168.0.4,cisco' -c 'show vlan' -a auth.txt`


`$python ./swITch.py -e -i ip.list -c cli.config -a auth.txt`


`$python ./swITch.py -e -i ip.list -p port.desc -a auth.txt`
