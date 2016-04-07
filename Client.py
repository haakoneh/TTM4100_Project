# -*- coding: utf-8 -*-
import socket
import json
from MessageReceiver import MessageReceiver
from MessageParser import MessageParser

class Client:
    """
    This is the chat client class
    """

    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """

        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # TODO: Finish init process with necessary code
        self.host = host
        self.server_port = server_port
        
        self.messageParser = MessageParser()
        self.messageReceiver = MessageReceiver(self, self.connection)
        self.run()

    def run(self):
        """
        Main process of the client. Waits for input from user
        """
        self.connection.connect((self.host, self.server_port))

        self.messageReceiver.start()
        
        print 'Client running...\nType \'quit\' to end or \'help\' for info'
        
        while True:
            command = raw_input()
  
            if command == 'quit':
                self.disconnect()
                print 'Client closing'
                break
            
            self.send_payload(self.messageParser.parse_dataToSend(command))	
            
    def disconnect(self):
        """
		Close sock connection 
		"""
        self.connection.close()

    def receive_message(self, message):
        """
		Prints received message after it's parsed
		"""
        print self.messageParser.parse(message)

    def send_payload(self, data):
        """
		Sends data to server
		"""
        self.connection.send(data)

if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    client = Client('78.91.18.128', 8888)
