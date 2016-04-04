# Installation and Usage 

## NETWORK DEVICE AUTOMATION

A python program which allows you to push commands to network devices.  It
can then dump the output to a file for later analysis.

I have decided to re-factor this code to work with Netmiko (work by Kirk Byers).
Better to solve new problems instead of re-inventing the wheel.


### DEVICE SUPPORT

* See Currently Cisco and HP. I will be implementing support for the devices that netmiko does. https://github.com/ktbyers/netmiko

### FUTURE DEVELOPMENT

* Allowing to specify which section of config in the cli.config file gets pushed out to certain IP ranges.  Then you can list all the config for various devices (e.g. multi-vendor devices).

### SETUP

1. Install python 
  * `sudo apt-get install python`


2. Install paramiko
  * `sudo apt-get install paramiko`


3. Install Netmiko
  * `sudo pip install netmiko`


4. Create the following files

  1. `ip.list` (1<sup>st</sup> - n<sup>th</sup> line: IP address, device type)


    ```
    172.30.30.30,hp_procurve
    172.30.30.31,cisco_ios
    ```


  2. `cli.config` (1<sup>st</sup> - n<sup>th</sup> line: cli command)


    ```
    config t
    show interfaces
    ```


  3. `port.desc` (1<sup>st</sup> line: config t, 2<sup>nd</sup> - n<sup>th</sup> line: interface, port description)


    ```
    config t
    interface gi0/1,description Port C001 : 1-52
    interface gi0/2,description Port C002 : 1-53
    .
    .
    .
    interface gi0/48,description Port C048 : 1-87
    ```


  4. `auth.txt` (1<sup>st</sup> line: username, 2<sup>nd</sup> line: password, 3<sup>rd</sup> line: enable password)


    ```
    joe
    password
    enableME
    ```


### RUN

Examples


`$python ./swITch.py -h`


`$python ./swITch.py -i '192.168.0.4,cisco_ios' -c 'show vlan' -a auth.txt`


`$python ./swITch.py -e -i ip.list -c cli.config -a auth.txt`


`$python ./swITch.py -e -i ip.list -p port.desc -a auth.txt`
