# Magazine Ana Luiza - Tutorial

Please follow the steps below in order to run the Magazine Ana Luíza application.

## Setting up the environment

Before cloning this repository, please make sure that you have python3 and its pip version installed.

Then, clone the project, get into its root folder and run:

        pip3 install -r requirements.txt
        
This command will install some required libraries like Flask and GeoPy.

## Server

To start a server, you must run the following command:

        python3 server/app.py [server_host] [server_port]

Where `server_host` and `server_port` will compose the address where the server will be listening to requests. 

To enjoy all functionalities of this application, you must start at least three instances of this server.

## Warehouse

To start a warehouse, you must run the following command:

        python3 warehouse/app.py [location] [warehouse_host] [warehouse_port]
        
Where `location` means the real warehouse's address, e.g. `Salvador, Bahia`.

After that you can open your browser in `http://localhost:5001/` and start playing.

Again, you can run more than one instance of this application.

## Node

The node application is required to start playing with customer. It's responsible for keeping the balance between the servers, and redirects incoming customers to different servers, according the Round Robin algorithm.

Before running a node, please open the file `utils.py` and change the list `servers` on line 3. It must contain the addresses of the servers that you just started before.

Then you can run the following command to start a node:

        python3 node/app.py [node_host] [node_port]
        
You don't need more than one running instance of node.
        
## Customer

To start a customer you must run the following command:

        python3 customer/app.py [location] [node_host] [node_port]
        
After that you can open `http://localhost:5000/` in your browser and start playing.

Run more than one instance of customer and have fun.

