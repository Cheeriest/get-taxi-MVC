from socket import *
from Tkinter import *
from Visual import *
import time, pickle
import thread, random, select, pickle, re
from math import sqrt
from Objects import Position, User, Taxi, User, Admin, Client
from Communication import *
import sys

class ClientVisual(Visual):
    def __init__(self, root, sock):
        self.startup = Tk()
        self.start = False
        Button(self.startup, text = 'Press This Button To Start', padx = 10, pady = 20, command = self.start_callback).pack()
        self.root = root
        self.root.attributes('-alpha', 0)
        self.sock = sock
        self.taxi = None
        self.is_waiting = True
        self.in_ride = False
        self.start_point = None
        self.destination = None
        self.position = None
        self.objects = {}
        self.init_window()
        self.startup.mainloop()
        

        

    def __initIO__(self, root, sock):
        message = Reply([], '4321')
        message = pickle.dumps(message)
        self.sock.send(message)
        super(ClientVisual, self).__init__(root, sock)

    def start_callback(self):
        self.start = True
        self.startup.destroy()
        self.root.attributes('-alpha', 1)
        self.__initIO__(self.root, self.sock)


    def init_window(self):

        # changing the title of our master widget      
        self.root.title("Taxi Client")

        # allowing the widget to take the full space of the root window

        # creating a menu instance
        menu = Menu(self.root)
        self.root.config(menu=menu)

        # create the file object)
        file = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit

        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Exit", command = self.exit)

        #added "file" to our menu
        

        

        # create the file object)
        edit = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        edit.add_command(label = "Info", command = lambda: self.show_info())
        #added "file" to our menu
        menu.add_cascade(label="Info", menu=edit)  

    def show_info(self):
        if not self.position:
            return
        pop_up = Tk()
        pop_up.title("Info About You")
        pop_up.geometry("%dx%d" % (self.width/2, self.height/1.2))
        label = Label(pop_up, text = 'Starting Point: ' + str(self.start_point))
        label.pack(side = 'top', fill = 'both')
        label = Label(pop_up, text = 'Destination: ' + str(self.destination))
        label.pack(side = 'top', fill = 'both')
        
        for line in str(self.taxi).splitlines():
            label = Label(pop_up, text = line)
            label.pack(side = 'top', fill = 'both')
        
        pop_up.mainloop()


    def leftclick_callback(self, event):
        x, y = event.x, event.y
        place = (x /self.dx, y/self.dy)
        obj = self.objects.get(place)


        if self.is_waiting:
            if not self.start_point:
                if not obj:
                    self.start_point = Position(place, False)
                    self.position = self.start_point
                    print str(self.start_point)
            elif not self.destination:
                if obj:
                    self.destination = obj
                    print str(self.destination)
                    message = Request([self.start_point, self.destination], 'RIDE')
                    self.sock.send(pickle.dumps(message))
            

        else:
            pop_up = Tk()
            pop_up.title("Data About Position: " + str(place)) 
            pop_up.geometry("%dx%d" % (self.width/2, self.height/2))  
            if isinstance(obj, Taxi):
                for line in str(obj).splitlines():
                    label = Label(pop_up, text = line)
                    label.pack(side = 'top', fill = 'both')            
            close = Button(pop_up, text = 'close', command = pop_up.destroy)
            close.pack(fill = 'both', side = BOTTOM)






    def update(self):
            while 1:
                time.sleep(1)

                for place in self.places.keys():
                    if self.objects.get(place):
                        if type(self.objects[place]) == Taxi:
                            self.w.itemconfigure(self.places[place], fill = 'gray')
                            
                        if type(self.objects[place]) == Client:
                                self.w.itemconfig(self.places[place], fill = 'gray', outline = 'white', width = 1)

                data = self.socket.recv(1024*50)
                try:
                    self.message = pickle.loads(data)
                except error as e:
                    print e
                
                if type(self.message) == Reply:
                    if self.message.get_payload() == 'RESET':
                        print 'Taxi dropped you, new one is coming!'

            
                    for obj in self.message.get_objects():
                        if obj != None and obj.get_position():
                            x , y = obj.get_position()
                            obj_pos = int(x), int(y)
                            self.objects[obj_pos] = obj
                            if type(obj) == Taxi:
                                taxi = self.places[obj_pos]
                                #taxi_index = obj.index
                                x , y = obj_pos
                                self.w.itemconfig(taxi, fill = 'yellow')
                                self.taxi = obj
                                #self.w.coords(self.taxi_numbers[taxi_index], x*self.dx + self.dx/2, y*self.dy + self.dy/2)
                            elif type(obj) == Charger:
                                pos = self.places[obj_pos]
                                if obj.is_occupied:
                                    self.w.itemconfig(pos, fill = 'red')
                            elif type(obj) == Position:
                                pos = self.places[obj_pos]
                                if obj.is_occupied:
                                    self.w.itemconfig(pos, fill = 'green')

                            if type(obj) == Client:
                                client_pos = obj.get_position()
                                self.w.itemconfig(self.places[client_pos], outline = 'purple', width = 3)

                elif type(self.message) == Request:
                    if self.message.get_payload() == 'END':
                        self.exit()

                if not self.first_sync and len(self.objects) > 1:
                    self.sock.send(pickle.dumps(Reply([], 'SYNC')))
                    self.first_sync = True

                if self.destination and self.position:
                    if self.destination.distance(self.position) <= 1:
                        self.exit()


with open('E:\Python 2.7.9\Scripts\Last Project\info.txt','r') as f:
    text = f.readlines()
    port , ip = int(text[0]), text[1]
    #Getting server ip and port
addr = (ip, port)
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(addr)

root = Tk()
visual = ClientVisual(root, sock)
root.mainloop()
sock.close()