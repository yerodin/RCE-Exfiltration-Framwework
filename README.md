# RCE-Exfiltration-Framework

**Ever found and RCE but just can't seem to get a shell? Well we do have RCE right?? Let's Exfiltrate!!.**

## How It Works
This script works by using different means to quickly exfiltrate the output of RCE. 

We try to smuggle information out of the target using commands such as CURL, WGET, certutil, etc

1. We start by defining a python module with function my_rce_function(cmd) to tell the script what to do to trigger RCE

2. An HTTP server is started to listen to output

3. We parse your RCE module and wrap it in the various smuggling commands to send back information


![Screenshot 2022-04-09 at 5 41 49 PM](https://user-images.githubusercontent.com/9205071/162594260-07f3a6eb-3276-4f82-ae94-08a6e9cdc2af.png)
