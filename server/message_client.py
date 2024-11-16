class Message:
    def __init__(self, sender, message,username):
        self.sender = sender
        self.message = message
        self.username= username
    def __repr__(self):
        return f'Message(Sender: {self.sender}, Message: {self.message})'

    def serialize(self):
        return {
            'sender': self.sender,
            'message': self.message
        }
    