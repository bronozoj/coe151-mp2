# CoE 151 MP2

This documentation is also available in my [Github Repository](https://github.com/bronozoj/coe151-mp2) along with my codes

This explains a lot about my implementation of a distance vector routing model  
Note that these applications have been rigorously tested on python3 and may not always work as intended in other earlier versions of python (python2.7 perhaps)  

`mp2.py` - Distance Vector Routing Modeler full implementation  
`timertest.py` - sample code for an auto-respawning timed thread (used in broadcasting)
`net1` - straight line network topology  
`net2` - mixed network topology  

## Command Line Arguments

`--poison` - activates poison reverse  
`--config <file>` - specifies file containing neighbor link costs  
`--port <port>` - specifies port **(default is 12345)**  
`--ip <ip address>` - specify the external ip address when not in local testing **(default is 127.0.0.1)**  
`--period <seconds>` - specifies period between broadcasts **(default is 10 seconds)**  
`--pseudo <number>` - specifies the value considered to be the pseudo-infinity value **(default is 100)**  

## Documentation

More in depth documentation is available in [here](DOCUMENTATION.md)
