from Objects import *

class Message(object):
    def __init__(self, objects = [], payload = ''):
        self.objects = objects
        self.payload = payload 

    
    

    def get_objects(self):
        return self.objects
    
    def get_payload(self):
        return self.payload

    def __str__(self):
        return str(self.objects) +" "+ str(self.payload)

class Request(Message):
    def __init__(self, objects, payload):
        super(Request, self).__init__(objects, payload)

    

class Reply(Message):
    
    def __init__(self, objects, payload):
        super(Reply, self).__init__(objects, payload)

    
    

    
