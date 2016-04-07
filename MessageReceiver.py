# -*- coding: utf-8 -*-
from threading import Thread
#import json

class MessageReceiver(Thread):
    """
    This is the message receiver class. The class inherits Thread, something that
    is necessary to make the MessageReceiver start a new thread, and it allows
    the chat client to both send and receive messages at the same time
    """
    def __init__(self, client, connection):
        """
        This method is executed when creating a new MessageReceiver object
        """
        super(MessageReceiver, self).__init__()
        self.daemon = True
        self.client = client
        self.connection = connection
		
    def run(self):
        """
        Runs in the background and listens for messages from the server
        """
        # print 'Reciever running'
        while True:
            data = self.connection.recv(4096)
			
            if data:
                self.client.receive_message(data)
	
			
