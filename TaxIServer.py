from socket import *
import thread, random, select, pickle, re, time
from math import sqrt
from Objects import Position, User, Taxi, User, Admin, Client
from Communication import *
from sqlite3 import *


class City(object):
    def __init__(self):
        self.width = 30
        self.hight = 20
        self.users = {}
        self.charger_position = Charger((self.width/2, self.hight/2), True)
        self.empty_positions = [Position((x,y)) for x in range(self.width) for y in range(self.hight) if x != self.width/2 and y != self.hight/2]
        self.taxis = [Taxi(self.empty_positions.pop(self.empty_positions.index(random.choice(self.empty_positions))), i) for i in range(1,4)]
        self.public_places_poistions = [self.empty_positions.pop(self.empty_positions.index(random.choice(self.empty_positions))) for i in range(30)]
        self.delay = 0.1
        self.db = 'rides.db'
        self.in_table = []
        for pos in self.public_places_poistions + [self.charger_position]:
            pos.set_occupied()

        self.admin_password = '1234'
        self.client_password = '4321'

    def add_user(self, conn, addr):
        #self.users.append(User(None, conn, addr, None))
        self.users[User(None, None, randint(0,10))] = (conn, addr)

    def delete_user(self, conn, addr):
        for c, v in self.users.items():
            if v == (conn, addr):
                if type(c) == Client:
                    client_taxi = c.taxi
                    if client_taxi:
                        client_taxi.direction = None
                        client_taxi.client = None
                del self.users[c]

                
    
    def get_user(self, conn, addr):
        for c, v in self.users.items():
            if v == (conn, addr):
                return c

    def update_user(self, user):
        for c, v in self.users.items():
            if c == user:
                del self.users[c]
                self.users[user] = v

    def add_to_table(self, start, end, taxinum, time):
        
        conn = connect(self.db)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS RIDES (START TEXT, END TEXT, TAXINUM INT, TIME TEXT)")
        cursor.execute('''INSERT INTO RIDES(START, END, TAXINUM, TIME) VALUES(?,?,?,?)''', (str(start), str(end), taxinum, str(time)))
        conn.commit()
        conn.close()
        return True
       
    def find_taxi_for_client(self, user):
        available_taxis = [taxi for taxi in self.taxis if not taxi.is_busy()]
        available_taxis = sorted(available_taxis, key = lambda taxi: user.distance(taxi))
        if not available_taxis:
            return False
        chosen_taxi = available_taxis.pop(0)
        chosen_taxi.client = user
        chosen_taxi.direction = user.get_position()
        user.set_taxi(chosen_taxi)
        return chosen_taxi

    def check_if_arrived(self, city):
        for taxi in self.taxis:
            if taxi.client:
                if not taxi.client.is_waiting:
                    near_positions = taxi.get_near_positions()
                    for pos in near_positions:
                        if taxi.client.destination == pos.get_position():
                            message = self.user_message(taxi.client, **{'type': Request, 'payload': 'END'})
                            sock, addr = self.users[taxi.client]
                            sock.send(message)
                            if (taxi.client.start_point, taxi.client.destination, taxi.index, time.ctime()) not in self.in_table:
                                if self.add_to_table(taxi.client.start_point, taxi.client.destination, taxi.index, time.ctime()):
                                    self.in_table.append((taxi.client.start_point, taxi.client.destination, taxi.index, time.ctime()))
                            self.delete_user(sock, addr)
                            break
            else:
                if taxi.direction == self.charger_position.get_position():
                    near_positions = taxi.get_near_positions()
                    for pos in near_positions:
                        if pos.get_position() == self.charger_position.get_position():
                            taxi.direction = None

    def update_state(self, data):
        try:
            for taxi in self.taxis:
                if taxi.needs_battery():
                    if taxi.charge(self.charger_position):
                        print 'Taxi Number %d Going to charge' % taxi.index
                        taxi.client.taxi = None
                        taxi.client.is_waiting = True
                        self.find_taxi_for_client(taxi.client)
                        sock, addr = self.users[taxi.client]
                        message = self.user_message(taxi.client, **{'type': Reply, 'payload':'RESET'})
                        sock.send(message)
                        taxi.client = None
                        taxi.charging = True

                if taxi.client != None:
                    taxi_pos = taxi.get_position()
                    client_pos = taxi.client.get_position()
                    if int(client_pos[0]) == int(taxi_pos[0]) and int(client_pos[1]) == int(taxi_pos[1]) and taxi.client.is_waiting:
                        taxi.set_direction(taxi.client.destination)
                        taxi.client.is_waiting = False
                
                if taxi.client == None and not taxi.is_busy():
                    for user in self.users.keys():
                        if type(user) == Client:
                            if not user.taxi and user.destination:
                                taxi.client = user
                                taxi.direction = user.get_position()
                                user.set_taxi(taxi)

                taxi.fix_problem()

                


            for taxi in self.taxis:
                city = [self.charger_position] + self.public_places_poistions + self.empty_positions + self.taxis
                city = dict([(obj.get_position(), obj) for obj in city])
                taxi.move(city)
                taxi.update_time(self.delay)
            
            self.charger_position.check_for_taxis(city)
            self.charger_position.charge()
            self.check_if_arrived(city)

            for user in self.users.keys():
                if type(user) == Client:
                    if user.position and user.destination and user.taxi == None:
                        taxi = self.find_taxi_for_client(user)
                        if taxi:
                            print 'taxi number %d is coming for user' %taxi.index
            
            try:
                for user, info in data:
                    d = pickle.loads(info) 
                    if type(d) == Reply:
                        if re.match(self.admin_password, d.get_payload()):
                            admin = Admin(user)
                            self.update_user(admin)
                        

                        if re.match(self.client_password, d.get_payload()):
                            client = Client(user)
                            self.update_user(client)

                        if re.match('SYNC', d.get_payload()):
                            user.is_new_user = False

                        if re.match('END', d.get_payload()):
                            if type(user) == Client:
                                user.taxi.client = None
                                user.taxi = None
                            sock, addr = self.users[user]
                            self.delete_user(sock, addr)
                            
    

                    elif type(d) == Request:
                        if re.match('RIDE', d.get_payload()):
                            if type(user) == Client:
                                
                                user.position , user.destination = d.get_objects()[0].get_position(), d.get_objects()[1].get_position()
                                taxi = self.find_taxi_for_client(user)
                                user.start_point = user.position
                                if taxi:
                                    message = self.user_message(user, **{'taxi':taxi, 'type' : Request,'payload': 'RIDE'})
                                    sock , addr = self.users[user]
                                    sock.send(message)
                        
            except EOFError:
               print 'Pickle is stupid'         

        except ValueError as error:

            raise error



    def user_message(self, user, **kwargs):
        if kwargs.get('type') == Reply:
            if type(user) ==  Admin:
                if user.is_new_user:
                    objects = [self.charger_position] + self.public_places_poistions + self.taxis + [user for user in self.users if type(user) != Admin]
                else:
                    users = [user for user in self.users if type(user) != Admin]
                    objects = self.taxis + users + [self.charger_position]

                message = Reply(objects, '')
                return pickle.dumps(message)
            
            elif type(user) == Client:
                if kwargs.get('payload') == 'RESET':
                    message = Reply([], 'RESET')
                    return pickle.dumps(message)

                

                if user.is_new_user:
                    objects = [self.charger_position] + self.public_places_poistions + [user.taxi] 
                else:
                    objects = [user.taxi]
                
                if user.get_position():
                    objects.append(user)
                message = Reply(objects, '')
                return pickle.dumps(message)

        elif kwargs.get('type') == Request:
            if kwargs.get('payload') == 'RIDE':
               objects = []
               message = Reply(objects, 'RIDE')
               return pickle.dumps(message)
            
            if kwargs.get('payload') == 'END':
                    message = Request([], 'END')
                    return pickle.dumps(message)
        
    


    def tell_users(self):
        for user in self.users:
            try:
                message = self.user_message(user, **{'type': Reply})
                if message:
                    #print 'sending  to' , type(user)
                    sock, addr = self.users[user]
                    sock.send(message)
            except error:
                print str(error)
            
        


def get_my_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def get_open_port():
    """
    Return an open port in ranges of 10,000 to 65,000
    """
    min_port, max_port = 10000, 65000
    s = socket(AF_INET, SOCK_STREAM)
    for port in range(min_port, max_port):
        try:
            s.bind(('localhost', port))
            s.close()
            return port
        except: 
            continue



def main():
    #Size Of City: 30x20
    city = City()
    server_port = get_open_port()
    #getting an open port for the server socket
    server_ip = get_my_ip()
    #getting the ip of the server
    with open('info.txt','w') as f:
        f.write(str(server_port) +'\n' + server_ip)

    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.bind((server_ip, server_port))
    serversock.listen(3)
    inputs = [serversock]
    delay = city.delay #0.1 between each update
    while True:
        data = []
        try:
            readables, _, _ = select.select(inputs, [], [], delay) 
            for s in readables:
                if s is serversock:
                    conn, addr = serversock.accept()
                    inputs.append(conn)
                    city.add_user(conn, addr)
                    print 'new connection with ', (conn, addr)
                else:
                    try:
                        data.append((city.get_user(conn, addr), s.recv(1024*50)))
                    except Exception:
                        inputs.remove(s)
                        city.delete_user(conn, addr)
                        conn.close()
                        print conn , 'has left the connection'
            city.update_state(data)
            city.tell_users()
        except error:
            continue 
                

        


        
        
if __name__ == '__main__':
    main()