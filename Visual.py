from socket import *
from Tkinter import *
import thread, re, time, pickle
from Objects import *
from math import floor
import sys

class Visual(object):
    def __init__(self, root, socket):
        self.root = root
        self.socket = socket
        self.first_sync = False
        self.width = 600
        self.height = 400
        self.colums = 30
        self.rows = 20
        x = (root.winfo_screenwidth() - self.width)/2
        y = (root.winfo_screenheight() - self.height)/2
        root.geometry("%dx%d+%d+%d"%(self.width, self.height, x, y))

        self.w = Canvas(root, width=self.width, height=self.height)
        self.w.pack()
        self.places = {}

        
        self.taxi_numbers = dict([(1, None), (2, None), (3, None)])

        self.dx = self.width/self.colums
        self.dy = self.height/self.rows

        for i in range(0,self.width,self.dx):
            for j in range(0,self.width,self.dy):
                place = self.w.create_rectangle(i, j, i+self.dx, j+self.dy,
                                       fill = "gray", outline = "white")
                self.places[(i/self.dx, j/self.dy)] = place
        
        for i in self.taxi_numbers.keys():
            self.taxi_numbers[i] = self.w.create_text(0, 0, text = str(i))

        self.w.bind('<Button-1>', self.leftclick_callback)
        
        thread.start_new_thread(self.update, ())
        
    def exit(self):
        self.root.destroy()
        self.socket.close()
        

    def init_window(self):
        """
        # changing the title of our master widget      
        self.root.title("GUI")

        # allowing the widget to take the full space of the root window

        # creating a menu instance
        menu = Menu(self.root)
        self.root.config(menu=menu)

        # create the file object)
        file = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        file.add_command(label="Exit", command=self.root.destroy)

        #added "file" to our menu
        menu.add_cascade(label="File", menu=file)

        # create the file object)
        edit = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        edit.add_command(label="Undo")

        #added "file" to our menu
        
        menu.add_cascade(label="Edit", menu=edit)
        """
        pass

    def update(self):
        '''
        self.objects = {}
        while 1:
            time.sleep(0.1)
            data = self.socket.recv(1024*50)
            try:
                self.city = pickle.loads(data)
            except error as e:
                print e
            
            for obj in self.city:
                self.objects[obj.get_position()] = obj
                if type(obj) == Taxi:
                    taxi = self.places[obj.get_position()]
                    self.w.itemconfig(taxi, fill = 'yellow')
                elif type(obj) == Position:
                    pos = self.places[obj.get_position()]
                    if obj.is_occupied and obj.get_position() == (self.colums/2, self.rows/2):
                        self.w.itemconfig(pos, fill = 'red')
                    elif obj.is_occupied:
                        self.w.itemconfig(pos, fill = 'green')
        '''
        pass

    def leftclick_callback(self, event):
        '''
        x, y = event.x, event.y
        place = (x /self.dx, y/self.dy)
        pop_up = Tk()
        pop_up.title("Data About Position: " + str(place)) 
        pop_up.geometry("%dx%d" % (self.width/2, self.height/2))  
        obj = self.objects.get(place)
        
        if isinstance(obj, Taxi):
            for line in str(obj).splitlines():
                label = Label(pop_up, text = line)
                label.pack(side = 'top', fill = 'both')
                     
        elif not obj:
            label = Label(pop_up, text = 'Just an Empty Place')
            label.pack(side = 'top', fill = 'both')
            
        else:
            label = Label(pop_up, text = 'A Public Place')
            label.pack(side = 'top', fill = 'both')
            
        close = Button(pop_up, text = 'close', command = pop_up.destroy)
        close.pack(fill = 'both', side = BOTTOM)
        '''
        pass