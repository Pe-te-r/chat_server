class User:
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
    
    def setUsername(self,name):
        self.username = name
    
    def setPassword(self,password):
        self.password = password
    
    def serialize(self):
        return {
            'username':self.username
        }