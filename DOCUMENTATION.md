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

## Tuesday Class Protocols

To lessen development time in programming, UDP sockets have been used instead of TCP for connectionless broadcasting  
This allows the application to send data despite other nodes being offline.

Default values are as follows:  
>	**Port:** 12345  
>	**Pseudo-infinity Value:** 100  
>	**Interval between broadcasts:** 10 seconds

Nodes should broadcast part of their routing tables (destination and cost) in this format:  
>	\<ip address\> \<port\> \<cost\>\n  
>	\<ip address\> \<port\> \<cost\>\n  
>	...

Specifications also require that the node should advertise itself as well on the sent routing table as having no (0) cost or the infinity value if it is about to go down.  
Values sent must also not exceed the pseudo-infinity value set.

## Implementation

### Multithreading Architecture

Instead of implementing a polling method for sending the routing table and receiving routing tables in a single process, a multithreaded architecture was made. The thread splits into two upon initialization of variables and loading of data.  
Instead of a standard thread, a `threading.Timer` object was used for the thread that will periodically send data.

To be able to send data repeatedly, a global object variable was used and the thread will create a new instance of the object and store it there so that the main thread can stop it anytime it needs to (i.e. exiting).

The main thread handles the processing of received tables and updates the routing table being maintained and sent. It also terminates the broadcasting thread whenever a `KeyboardInterrupt` exception is raised (CTRL + C). It also broadcasts a self cost equivalent to the infinity value before finally cleaning up and exiting.


### Data Types

The program has two custom classes, namely `nodecost` and `nodeinfo`.

The `nodeinfo` object stores an individual entry from the routing table. Collecting these entries into a list constitues the node's routing table.  
Functions are exposed in the nodeinfo object to provide formatted versions of its elements. It can also maintain a value hold counter used for holding the infinity value when poisoned reverse is in place. The threshold is a static value. It can be increased to help the node to not count to infinity but setting it too high will increase the time it will take to recalculate a shorter path to other nodes that previously used the path to the offline node. Decreasing it will decrease the time it takes to recalculate the node paths but can render the poisoning useless as it may count to infinity in other complex network structures.

The `nodecost` object stores individual neighbor data that comes from the file or a neighbor's routing table. This is collected into a list to constitute either the cost to neighbor list or the routing table to be compared to the current routing table.

### Functions

The `costparser` function takes a list of strings in the format specified and outputs a list of `nodecost` objects parsed from the list of strings. This allows the input file to also follow the format of the data received for code reusability.

The `tabledump` function takes no variables, but uses global variables, namely the routing table variable `routing_table` and the neigbor list `costlist` to display the table and broadcast it to all neighbors.

The `sendingthread` function is the function to be executed by the spawning thread object. It monitors a global variable that changes value when the main function is about to exit. It also runs the tabledump function before respawning another thread object upon exit.

