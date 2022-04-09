# RCE-Exfiltration-Framework

**Ever found and RCE but just can't seem to get a shell? Well we do have RCE right?? Let's Exfiltrate!!.**

## How It Works
This script works by using different means to quickly exfiltrate the output of RCE. 

We try to smuggle information out of the target using commands such as CURL, WGET, certutil, etc

1. We start by defining a python module with function my_rce_function(cmd) to tell the script what to do to trigger RCE

2. An HTTP server is started to listen to output

3. We parse your RCE module and wrap it in the various smuggling commands to send back information

## Example

```bash
git clone https://github.com/SIRUS-THE-VIRUS/Computer-Security-RAT.git
```

## Usage

* Modify the IP address and Port for the socket connection at your discretion. 

* Get server.py onto the victim computer

* Get the victim to execute the server

* Connect to the server from the attacker's computer using client.py
