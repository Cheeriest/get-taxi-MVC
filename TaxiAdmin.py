from socket import *
from Tkinter import *
import thread, re, time, pickle
from Objects import *
from math import floor
from Visual import Visual
from Communication import *
from sqlite3 import * 
class AdminVisual(Visual):
         
    def __init__(self, root, sock):
        self.startup = Tk()
        self.start = False
        Button(self.startup, text = 'Press This Button To Start', padx = 10, pady = 20, command = self.start_callback).pack()
        self.root = root
        self.root.attributes('-alpha', 0)
        self.sock = sock
        self.db = 'rides.db' 
        self.clients = []
        self.taxis = []
        self.init_window()
        self.startup.mainloop()


        

    def __initIO__(self, root, sock):
        message = Reply([], '1234')
        message = pickle.dumps(message)
        sock.send(message)
        super(AdminVisual, self).__init__(root, sock)

    def start_callback(self):
        self.start = True
        self.startup.destroy()
        self.root.attributes('-alpha', 1)
        self.__initIO__(self.root, self.sock)

    def init_window(self):

        # changing the title of our master widget      
        self.root.title("Taxi Admin")

        # allowing the widget to take the full space of the root window

        # creating a menu instance
        menu = Menu(self.root)
        self.root.config(menu=menu)

        # create the file object)
        file = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit

        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Exit", command = lambda: self.exit_callback())

        #added "file" to our menu
        

        

        # create the file object)
        edit = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        edit.add_command(label = "Taxis", command = lambda: self.show_taxis_callback())
        edit.add_command(label = 'Clients', command = lambda: self.show_clients_callback())
        edit.add_command(label = 'Records', command = lambda: self.show_sql())
        #added "file" to our menu
        menu.add_cascade(label="Show", menu=edit)     

    def exit_callback(self):
        conn = connect(self.db)
        cursor = conn.cursor()
        sql_Delete_query =  "DROP TABLE IF EXISTS RIDES"
        cursor.execute(sql_Delete_query)
        
        self.exit()

    def show_taxis_callback(self):
        
        if not self.taxis:
            return
        self.show_objects(self.taxis)

    def show_clients_callback(self):
        
        if not self.clients:
            return
        self.show_objects(self.clients)
    
    def sql_callback(self):
        self.show_sql()

    def show_sql(self):
        conn = connect(self.db)
        try:
            sql_select_Query = "select * from RIDES"
            cursor = conn.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            
            for row in records:
                print("Start Position = ", str(row[0]))
                print("End Position = ", str(row[1]))
                print("Taxi Number  = ", str(row[2]), "")
                print('Time =', str(row[3]))
                print(' ')
                print(' ')
            cursor.close()
        except:
            print 'table doesnt exist'
    def show_objects(self, objects):
        pop_up = Tk()
        pop_up.title("Data About %ss" % (type(objects[0]))) 
        pop_up.geometry("%dx%d" % (self.width/1.5, self.height))  
        objects = list(dict.fromkeys(objects))
        for obj in objects:
            f = Frame(pop_up)
            f.pack(side = 'right', fill = 'both', padx = 1)
            for line in str(obj).splitlines():
                label = Label(f, text = line)
                label.pack(side = 'top', fill = 'both')
        
        pop_up.mainloop()

    def leftclick_callback(self, event):
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

                
    def update(self):
        self.objects = {}
        while 1: 
                time.sleep(1)

                for place in self.places.keys():
                    if self.objects.get(place):
                        
                        if type(self.objects[place]) == Taxi:
                            self.w.itemconfigure(self.places[place], fill = 'gray', outline = 'white', width = 1)
                        
                        if type(self.objects[place]) == Client:
                                self.w.itemconfig(self.places[place], fill = 'gray', outline = 'white', width = 1)



                data = self.socket.recv(1024*50)
                try:
                    self.message = pickle.loads(data)
                except EOFError as e:
                    continue


                if type(self.message) == Reply:
                
                    
                    for obj in self.message.get_objects():
                        if obj and obj.get_position():
                            x , y = obj.get_position()
                            obj_pos = int(x), int(y)
                            self.objects[obj_pos] = obj
                            if type(obj) == Taxi:
                                taxi = self.places[obj_pos]
                                taxi_index = obj.index                                
                                self.w.itemconfig(taxi, fill = 'yellow')
                                self.w.coords(self.taxi_numbers[taxi_index], int(x)*self.dx + self.dx/2, int(y)*self.dy + self.dy/2)

                                for taxi in self.taxis:
                                    if taxi.index == obj.index:
                                        self.taxis.remove(taxi)
                                
                                self.taxis.append(obj)


                            elif type(obj) == Charger:
                                pos = self.places[obj_pos]
                                if obj.is_occupied:
                                    self.w.itemconfig(pos, fill = 'red')
                            elif type(obj) == Position:
                                pos = self.places[obj_pos]
                                if obj.is_occupied:
                                    self.w.itemconfig(pos, fill = 'green')
                                
                            if type(obj) == Client:
                                client_pos = self.places[obj_pos]
                                self.w.itemconfig(client_pos, outline = 'purple', width = 3)
                                
                                for client in self.clients:
                                    if client.destination == obj.destination:
                                        self.clients.remove(client)
                                self.clients.append(obj)


                if not self.first_sync and len(self.objects) > 3:
                    self.sock.send(pickle.dumps(Reply([], 'SYNC')))
                    self.first_sync = True




with open('E:\Python 2.7.9\Scripts\Last Project\info.txt','r') as f:
    text = f.readlines()
    port , ip = int(text[0]), text[1]
    #Getting server ip and port
addr = (ip, port)
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(addr)


root = Tk()
visual = AdminVisual(root, sock)
root.mainloop()
sock.close()


