Install python (e.g. sudo apt-get install python)
Install pexpect(e.g. sudo apt-get install pexpect)

Create the following files
	iplist.txt (one IP per line)
	commands.txt (switch commands, one per line)
	creds.txt (1st line: uname, 2nd line: passwd, 3rd line: enablePasswd)

Run the program.

E.g.

$python ./swITch.py -e -i iplist.txt -c commands.txt -a creds.txt

python ./swITch.py -h (for help)

