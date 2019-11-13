Taxi Administrator - CYBER YA Project
Author: Fima Muzmaher							May 2019

The main focus of this project is to demonstrate an MVC architecture based connection, administrating taxis and clients in a city. 


Files:
- TaxiServer.py, the server side of the program.
- TaxiClient.py, the client side of the program.
- TaxiAdmin.py, the Admin side of the program.
- Objects.py and Communication.py, utils files that include
  the classes used in the code.


Notes:
Please ensure python 2.7.x is installed on your machine correctly, and all .py files of this project are in the same directory.
The connection will only work if you run all .py files on the same machine, a wider type of connection might be added in the future.I apologize if there are any problems or crashes while running the code. 
Modules that are mainly used in the script are:
- socket: for configuring sockets in the code.
- select: for reading and writing between distant sockets.
- pickle: makes it EXTREMELY easy to transfer data between two
          sides because it is able to send any type of object   
          you would like, as well as instances of private 		     classes you create.
- Tkiner: for creation of GUI for Admin and Client.


General Instuction:
Start the program by running the TaxiServer.py code. You may now run either the client script or the admin script as you 
perfer.

As a client, after connecting and seeing the screen getting colored, you may order a taxi between two squares.
IMPORTANT: YOU NEED TO PRESS ON AN EMPTY SQUARE (GRAY) AND
ONLY THEN ON A PUBLIC PLACE SQUARE (GREEN). TAXIS ONLY GO BETWEEN THOSE TWO TYPES OF PLACES. after ordering a ride, 
a taxi shall be coming for you and you will notice:
- a yellow square which shows real time position of the taxi
- a purple outline that shows real time position of you.

As a server, after connecting and seeing the screen getting colored, you may press on any square to get information about it.
Each taxi is numbered and colored in yellow, clients are outlined with purple color. 

Futhur Explaination:
The project is based on OOP structure, most objects inherit from each other and use shared variables. it makes the code 
much more readable and clean, although I'm sure it could have been much better, I apologize. Each machine that connects to 
the server is tagged as a 'User'. after the machine sends a message with a correct code, whether it may be the Admin's or
Client's password, the tagging for the machine changes accordingly. Later on, the server disscusses with the machine through 
sending Objects of classes defined in 'Communication.py' which are all pickled by pickle. If there is a disconnection, the server removes the user from its list.


