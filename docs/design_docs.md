# Lab 3: Asterix and Double Trouble  --  Replication, Caching, and Fault Tolerance


## Lab Overview

This project added caching, replication, and fault tolerance to the stock bazaar application in lab2. 
Like in lab 2, the server is made with the front-end part and the back-end parts. 
The front-end server communicates with the client directly,
 while the back-end servers proceeds the requests with catalog server or order server depending on what type the request is. 

We used flask package to help the implementation. 
Flask is a micro web framework written in Python, 
which support client requests and send responses from the server to the clients with routing.
For instance, with `@app.route()`, we pass a URL into the function `route()`, and define a specific function call related to that URL.

We also have implemented functionality like caching, replication, and fault tolerance in this lab. 


## components

### FRONTEND

front_end.py composites with serveral parts. The cache contains a list of stock items in json formate. 
The lock is used to synchronize access to the cache that guarantees no concurrent access leading to data corruption.
REST API enables the server listens to HTTP requests on selected port and URL routes the requests to according functionalities.
Leader Election is done periodically with a leader election algorithm. 
The algorithm pings the order servers periodically, where the server is considered dead if it fails to respond the ping. 
select a new leader upon the time when the current leader fails.

API:

@front_server.route('/rm', methods=['GET']) removes a stock item from the cache.

@front_server.route('/stocks', methods=['GET']) retrieves stock json data with the stock name. 
The server first checks if the stock data is available in the cache. If it's available in the cache, the server will return the stock json object.
Otherwise the server will retrieve the stock data by sending a query request to the catalog server, then caches the data in the cache and return the stock json object.

@front_server.route('/orders', methods=['POST', 'GET']) will create a new order on the order server if the method is 'POST' and will retrieve the order status for a given order number if the method is 'GET'. 

@front_server.route('/leader',methods=['GET']) will return the current leader order server ID.


## Part 1: Caching

front-end & caching to the front-end

s. The front-end server starts with an empty in-memory cache. Upon receiving a stock query
request, it first checks the in-memory cache to see whether it can be served from the cache. If not,
the request will then be forwarded to the catalog service, and the result returned by the catalog
service will be stored in the cache.

Cache consistency

 needs to be addressed whenever a stock is bought or sold. You should implement a
server-push technique: the catalog server sends invalidation requests to the front-end server after each
trade. The invalidation requests cause the front-end service to remove the corresponding stock from
the cache.

## Part 2: Replication

To make sure that our stock bazaar doesn't lose any order information due to crash failures, we want
to replicate the order service. When you start the stock bazaar application, you should first start
the catalog service. Then you start three replicas of the order service, each with a unique id
number and its own database file. There should always be 1 leader node and the rest are follower
nodes. You do **NOT** need to implement a leader election algorithm. Instead the front-end service
will always try to pick the node with the highest id number as the leader.

When the front-end service starts, it will read the id number and address of each replica of the
order service (this can be done using configuration files/environment variables/command line
parameters). It will ping (here ping means sending a health check request rather than the `ping`
command) the replica with the highest id number to see if it's responsive. If so it will notify all
the replicas that a leader has been selected with the id number, otherwise it will try the replica
with the second highest id number. The process repeats until a leader has been found.

When a trade request or an order query request arrives, the front-end service only forwards the
request to the leader. In case of a successful trade (a new order number is generated), the leader
node will propagate the information of the new order to the follower nodes to maintain data
consistency.

## Part 3: Fault Tolerance

In this part you will handle failures of the order service. In this lab you only need to deal with
crash failure tolerance rather than Byzantine failure tolerance.

First We want to make sure that when any replica crashes (including the leader), trade requests and
order query requests can still be handled and return the correct result. To achieve this, when the
front-end service finds that the leader node is unresponsive, it will redo the leader selection
algorithm as described in [Part2](#part-2-replication).

We also want to make sure that when a crashed replica is back online, it can synchronize with the
other replicas to retrieve the order information that it has missed during the offline time. When a
replica comes back online from a crash, it will look at its database file and get the latest order
number that it has and ask the other replicas what orders it has missed since that order number.

## Part 4: Testing and Evaluation with Deployment on AWS

First, write some simple test cases to verify that your code works as expected. You should test both
each individual microservice as well as the whole application. Submit your test cases and test
output in a test directory.

Next, deploy your application on an `m5a.xlarge` instance in the `us-east-1` region on AWS. We will
provide instructions on how to do this in lablet 5. Run 5 clients on your local machine. Measure
the latency seen by each client for different types of requests. Change the probability p of a
follow up trade request from 0 to 80%, with an increment of 20%, and record the result for each p
setting. Make simple plots showing the values of p on the X-axis and the latency of different types
of request on the y-axis. Also do the same experiments but with caching turned off, estimate how
much benefits does caching provide by comparing the results.

Finally, simulate crash failures by killing a random order service replica while the client is
running, and then bring it back online after some time. Repeat this experiment several times and
make sure that you test the case when the leader is killed. Can the clients notice the failures?
(either during order requests or the final order checking phase) or are they transparent to the
clients? Do all the order service replicas end up with the same database file?

## What to submit

Your solution should contain source code for both parts separately inside the `src` directory. Then
under the directory for each part, you should have a separate folder for each
component/microservice, e.g., a `client` folder for client code, a `front-end` folder for the
front-end service, etc.

A short README file on how to run your code. Include build/make files if you created any, otherwise
the README instructions on running the code should provide details on how to do so.

Submit the following additional documents inside the docs directory. 1) A Brief design document (1
to 2 pages) that explains your design choices (include citations, if you used Internet
sources), 2) An Output file (1 to 2 pages), showing sample output or screenshots to indicate that your
program works, and 3) An Evaluation doc (2 to 3 pages), for part 4 showing plots and making
observations.

