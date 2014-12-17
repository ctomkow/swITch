A python program which allows you to issue commands to Cisco switches and capture the output using pexpect. 
Actually the cDevice.py class should work for many types of switches, but it depends on '>' and '#' for the expect to work.
I plan on creating more classes that support other switches, but for now there is just the cDevice.py class.

-----------------------------------------------------------------------------------------
---------------------------------- Installation and Usage -------------------------------
-----------------------------------------------------------------------------------------

Install python (e.g. sudo apt-get install python)
Install pexpect(e.g. sudo apt-get install pexpect)

Create the following files
	iplist.txt (one IP per line)
	commands.txt (switch commands, one per line)
	creds.txt (1st line: uname, 2nd line: passwd, 3rd line: enablePasswd)

Run the program.

E.g.

$python ./swITch.py -h (for help)
$python ./swITch.py -e -i iplist.txt -c commands.txt -a creds.txt



