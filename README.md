# Installation and Usage 

## NETWORK DEVICE AUTOMATION

A python wrapper for netmiko which allows you to push commands to network infrastructure devices. It can then dump the output to a file for later analysis.

New: Support for Sentry PDU's (Sentry Switched CDU).

Implements netmiko's SCP file transfer for Cisco devices. Use -f to transfer files to the device (specifies flash: directory only. This is a netmiko limitation). Remember, Cisco's scp server implementation relies on authentication AND authorization.


### DEVICE SUPPORT

* What to append at the end of each IP address
  * `,cisco_ios`
  * `,hp_procurve`
  * `,sentry_pdu`
  * `,juniper_junos`
  * `,paloalto_panos`

### FUTURE DEVELOPMENT

* Implementing the capability to directly pass the device type to netmiko. This will provide the ability to use any netmiko device type without explicit support from this wrapper.
* Allowing to specify which section of config in the cli.config file gets pushed out to certain IP ranges.  Then you can list all the config for various devices (e.g. multi-vendor devices).
* Implement multi-threading to push out commands/files concurrently.

### SETUP

1. `sudo apt-get install python3`
2. `pip3 install netmiko`
3. Create the following files
* `ip.list` (1<sup>st</sup> - n<sup>th</sup> line: IP address, device type)
    ```
    172.30.30.30,hp_procurve
    172.30.30.31,cisco_ios
    ...
    ```
* `cli.cmd` (1<sup>st</sup> - n<sup>th</sup> line: cli command)
    ```
    show interfaces
    ...
    ```
* `cli.set` (1<sup>st</sup> - n<sup>th</sup> line: cli command)
    ```
    ip name-server 1.1.1.1
    ...
    ```
* `auth.txt` (1<sup>st</sup> line: username, 2<sup>nd</sup> line: password, 3<sup>rd</sup> line: enable password)
    ```
    joe
    password
    enableME
    ```
(note: port description below is currently legacy that doesn't use the newer send_config_set netmiko method. It still works on Cisco devices as-is, however.)
* `port.desc` (1<sup>st</sup> line: config t, 2<sup>nd</sup> - n<sup>th</sup> line: interface, port description)
    ```
    config t
    interface gi0/1,description Port C001 : 1-52
    interface gi0/2,description Port C002 : 1-53
    .
    .
    .
    interface gi0/48,description Port C048 : 1-87
    ```

### RUN

A common command sequence.

`$python ./swITch.py -eva auth.txt -i ip.list -c 'show runn'`

Other examples.

`$python ./swITch.py -h`

`$python ./swITch.py -i '192.168.0.4,cisco_ios' -c 'show vlan' -a auth.txt`

`$python ./swITch.py -e -i 172.30.30.30 -f c3560-ios-image.bin -a auth.txt`

`$python ./swITch.py -e -i ip.list -c cli.cmd -a auth.txt`

`$python ./swITch.py -e -i ip.list -s 'ip name-server 1.1.1.1' -a auth.txt`

`$python ./swITch.py -e -i ip.list -p port.desc -a auth.txt`

`$python ./swITch.py -i '10.0.0.10,sentry_pdu' -c 'LIST PORTS' -a auth.txt`


### Notes
* You can comment out lines in (port desc, ip list, cli conf)input files with a '#'. 

