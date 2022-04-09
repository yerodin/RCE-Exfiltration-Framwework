# RCE-Exfiltration-Framework

**Ever found and RCE but just can't seem to get a shell? Well we do have RCE right?? Let's Exfiltrate!!.**

## How It Works
This script works by using different means to quickly exfiltrate the output of RCE. 

We try to smuggle information out of the target using commands such as CURL, WGET, certutil, etc

1. Start by defining a python module with function my_rce_function(cmd) to tell the script what to do to trigger RCE

2. An HTTP server is started to listen to output

3. Script then parses your RCE module and wraps it using the various smuggling commands to send back information to our server

