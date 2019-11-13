from math import sqrt
from random import randint, choice

def distance(tup1, tup2):
    if isinstance(tup1, tuple) and isinstance(tup2, tuple):
        return sqrt((tup1[0]-tup2[0])**2 + (tup1[1]-tup2[1])**2)

class Position(object):
    def __init__(self, position, is_occupied = False):
        self.position = None
        if isinstance(position, Position):
            self.position = position.position
        elif isinstance(position, tuple):
            self.position = position
        self.is_occupied = is_occupied
        
    
    def get_position(self):
        return self.position

    def move(self, next_hop, multiplyer):
        x = multiplyer*(next_hop[0] - self[0]) 
        y = multiplyer*(next_hop[1] - self[1])
        self.position = (self.position[0] + x, self.position[1] + y)
        

    def get_near_positions(self):
        near_positions = [Position((self[0], self[1]+1)) ,Position((self[0], self[1]-1)), Position((self[0]-1, self[1])), Position((self[0]+1, self[1]))]
        return near_positions

    def set_occupied(self):
        if not self.is_occupied:
            self.is_occupied = True

    def distance(self, other):
        if isinstance(other, Position):
            other_position = other.get_position()
            return sqrt((self.position[0]-other_position[0])**2 + (self.position[1]-other_position[1])**2)
        elif isinstance(other, tuple):
            return sqrt((self.position[0]-other[0])**2 + (self.position[1]-other[1])**2)
        else:
            return 0

    def __eq__(self, other):
        if type(other) == Position:
            return other.get_position() == self.position

    def __getitem__(self, index):
        return int(self.position[index])


    def __str__(self):
        return str(self.position)


class Charger(Position):
    def __init__(self, position, is_occupied):
        super(Charger, self).__init__(position, is_occupied)
        self.charging_taxis = []
        self.charge_per_turn = 1

    def charge(self):
        for taxi in self.charging_taxis:
            if taxi.battery < 100:
                taxi.battery += self.charge_per_turn
                
            else:
                self.charging_taxis.remove(taxi)
                taxi.charging = False
                print 'taxi number %d finished charging' %taxi.index
            
    def check_for_taxis(self, city):
        near_positions = [pos.get_position() for pos in self.get_near_positions()]
        for pos, obj in city.items():
            if type(obj) == Taxi:
                x , y = pos
                obj_pos = int(x), int(y)
                if obj_pos in near_positions and obj not in self.charging_taxis and obj.needs_battery():
                    self.charging_taxis = self.charging_taxis + [obj]



class User(Position):
    def __init__(self, position, is_occupied, index):
        self.position = position
        if self.position:
            super(User, self).__init__(position, is_occupied)
        #self.socket = socket
        #self.address = address
        self.is_new_user = True
        self.index = index

    def get_position(self):
        return super(User, self).get_position()

    def __eq__(self, other):
    #    return self.socket == other.socket and self.address == other.address   
        if isinstance(other, User):
            return other.index == self.index

    


class Client(User):
    
    def __init__(self, user):
        super(Client, self).__init__(user.position, True, user.index)
        self.is_waiting = True
        self.taxi = None
        self.destination = None
        self.start_point = None

    def get_position(self):
        return super(Client, self).get_position()

    def distance(self, other):
        return super(Client, self).distance(other)

    def set_taxi(self, taxi):
        self.taxi = taxi

    def __str__(self):
        if self.taxi.index:
            return ''' 
        
Client
Position: %s
Destination: %s
Taxi Number: %d
        ''' % (self.position, self.destination, self.taxi.index)
        else:
            return ''' 
        
Client
Position: %s
Destination: %s
        ''' % (self.position, self.destination)

class Admin(User):
    def __init__(self, user):
        super(Admin, self).__init__(user.position, False, user.index)

    
class Problem(object):

    def __init__(self):
        self.potential_problems = ['Pancher', 'Window Broke', 'Engine Broke', 'Egzoz Broke']
        self.time_for_fix = 0
        self.explain = ''
        self.num_of_problems = 0

    def generate_problem(self, number):
        if number != randint(1, 1000* (self.num_of_problems+1)):
            return 
        self.explain = choice(self.potential_problems)
        self.time_for_fix = randint(0, 500)
        self.num_of_problems =+ 1
        print 'Taxi Got a Problem'


    def fix(self):
        if self.time_for_fix > 0:
            self.time_for_fix = self.time_for_fix - 1
            if self.time_for_fix == 0:
                print 'fixed'
        else:
            self.explain = ''

    def __str__(self):
        if self.time_for_fix:
            return '''
The Problem is: %s
Time untill fixed: %d

''' % (self.explain, self.time_for_fix*0.1)
        else:
            return 'No Problem :D'


class Taxi(Position):
    def __init__(self, position, index):
        super(Taxi, self).__init__(position, is_occupied = True)
        #self.state = 'empty'
        self.index = index
        self.battery = 100
        self.speed =  0.03333333333
        self.client = None
        self.direction = None
        self.problem = Problem()
        self.charging = False
        self.estimated_time = 0
        self.battery_per_turn = 0.1


    def __eq__(self, other):
        if isinstance(other, Position):
            return self.position == other.get_position()

    def get_position(self):
        return super(Taxi, self).get_position()

    def go_to(self, city):
        near_positions = self.get_near_positions()
        for pos in near_positions:
            if city.get(pos.get_position()):
                if city.get(pos.get_position()).get_position() == self.direction:
                    return pos
                elif city.get(pos.get_position()).is_occupied or type(city.get(pos.get_position())) == Taxi:
                    near_positions.remove(pos)
        direction = self.direction
        
        return min(near_positions, key = lambda pos: pos.distance(direction))

    def needs_battery(self):
        return self.battery < 20 or self.distance(self.direction) / self.speed * self.battery_per_turn > self.battery

    def generate_problem(self):
        self.problem.generate_problem(self.index * randint(0,5))

    def fix_problem(self):
        self.problem.fix()

    def move(self, city):
        if self.direction != None and self.problem.time_for_fix == 0:
            near_positions = self.get_near_positions()
            if not near_positions:
                return False
            next_hop = self.go_to(city).get_position()
            super(Taxi, self).move(next_hop, self.speed)
            if self.client:
                if not self.client.is_waiting:
                    x, y = self.position
                    self.client.position = int(x), int(y)
            self.battery = self.battery - self.battery_per_turn
            self.generate_problem()
            return True
        else:
            return False

    def update_time(self, delay):
        if not self.direction:
            self.estimated_time = 0
        else:
            self.estimated_time = delay * self.distance(self.direction) / self.speed 

    def charge(self, charger):
        if not self.charging or self.direction != charger.get_position():
            if self.client:
                self.direction = charger.get_position()
                return True
            else:
                self.direction = charger.get_position()
                return False



    def is_busy(self):
        return not (self.client == None and self.battery > 20 and self.direction == None and self.problem.time_for_fix == 0 and not self.charging)

    def set_client(self, client):
        self.client = client

    def set_direction(self, direction):
        self.direction = direction

    def __str__(self):
        ret = '''
Taxi
Index: %d
Estimated Time: %d
Busy: %s
Battery: %d
Speed: %f
Direction: %s
Problem: %s '''%(self.index, self.estimated_time, self.is_busy(), self.battery, self.speed, self.direction, str(self.problem))
        return ret