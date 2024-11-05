class Message:
    def __init__(self, sender, message):
        self.sender = sender
        self.message = message
    def __repr__(self):
        return f'Message(Sender: {self.sender}, Message: {self.message})'

    def serialize(self):
        return {
            'sender': self.sender,
            'message': self.message
        }
    