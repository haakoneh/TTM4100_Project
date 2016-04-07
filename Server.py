# -*- coding: utf-8 -*-
import SocketServer
from datetime import datetime
import json
import string
import sys
import re

#List and dict for users and chatting history
logged_in_users = {} 
history = [] 

"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""

class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """

    def message(self, socket, message):
        """
        Send message if sender has username and adds it to 
        history list. Prints out user and message for the server
        """
        if(self.username == None):
            self.send_server_message(socket, 'error', 'You cannot send messages when not logged in')
            return
        response = self.make_response(self.username, 'message', message)
        self.broadcast_message(response)

        history.append(response)
        print('User \'' + self.username + '\' said: ' + message)

    def send_history(self, socket):
        """
        Sends all messages in history list to given user. 
        It have some limitations. If the list is large, 
        the delay may be unacceptable
        """
        history_msg = ''
        for message in history: 
            msg = json.loads(message)
            history_msg += 'User \'' + msg['sender'] + '\' said: ' + msg['content'] + '\n'
        history_response = self.make_response('Server', 'history', history_msg)
        self.send_message(socket, history_response)
        
    def login(self, socket, username):
        """
        When new user is added, the username is checked if it's valid 
        and if it's not already logged in
        """
        global history

        alnum_check = re.compile('^[a-zA-Z0-9_]*$')
        if not(alnum_check.match(username)):
            self.send_server_message(socket, 'error', 'Invalid username')
            return

        if(self.username != None):
            self.send_server_message(socket, 'error', 'You are already logged in')
            return

        if(username not in logged_in_users):
            logged_in_users[username] = socket
            self.username = username
            self.send_history(socket)
            #self.send(self.make_response('system', 'history', history))

            response = self.make_response('Server', 'info', (self.username + ' signed in'))
            self.broadcast_message(response)
            print('User \'' + self.username + '\' connected')
        else:
            self.send_server_message(socket, 'error', 'Username "' + username + '" already taken')

    def logout(self, socket):
        """
        Checks if username is valid, if so, username is removed from
        list of participating users
        """
        if(self.username != None):
            response = self.make_response('Server', 'info', (self.username + ' signed out'))
            self.broadcast_message(response)
            del logged_in_users[self.username]
            self.username = None
            
    #def send(self, payload):
    #       self.connection.send(payload)

    def helper(self, socket):
        """
        Sends message with info about the different commands 
        and logged in users
        """
        help_message = ('login <username> - Log onto the server with given username \n' +
            'logout - Log out of the server\n' +
            'msg <message> - Send a message to other logged in members\n' +
            'names - List all logged in users\n' +
            'help - View this text"')

        self.send_server_message(socket, 'info', help_message)
        
    def error_handling(self):
        """
        Prints message to user of server, does nothing else
        """
        print 'Invalid message recieved. Do nothing'

    def usernames(self):
        """
        Makes a string containing all logged in users, 
        and send it to a specific user
        """
        username_msg = 'List of user(s):\n'
        for iter_username, iter_socket in logged_in_users.items():
            username_msg +=  '- ' + str(iter_username) + '\n' 
        self.send_server_message(self.connection, 'info', username_msg)

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.username = None
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request

        valid_chars = set(string.ascii_letters + string.digits)
        
        print("Client connected @" + self.ip + ":" + str(self.port))
		
        self.helper(self.connection)        
        
        while True:
            received_string = self.connection.recv(4096).strip()
            # TODO: Add handling of received payload from client
            # print 
            try:
                received_json = json.loads(received_string)

                if(     'request' not in received_json or
                        'content' not in received_json):
                    print 'no req or cont'
                    raise ValueError
            except:
                if not received_json:
                    if self.username is not None:
                        del logged_in_users[self.username]
                    break; # Shutdown thread if empty request recieved
                self.send_message(self.request, 'Invalid request format')
                continue


            request_type = received_json['request']

            if request_type == 'msg':
                self.message(self.connection, received_json['content'])
            elif request_type == 'history':
                self.send_history(self.connection)
            elif request_type == 'login':
                self.login(self.connection, received_json['content'])
            elif request_type == 'logout':
                self.logout(self.connection)
            elif request_type == 'help' or request_type == 'info':
                self.helper(self.connection)
            elif request_type == 'error':
                self.error_handling()
            elif request_type == 'name':
                self.usernames()       

    def broadcast_message(self, response):
        """
        Traverse through list of users and send message to 
        everyone
        """
        global logged_in_users
        for iter_username, iter_socket in logged_in_users.items():
            self.send_message(iter_socket, response)

    def send_server_message(self, socket, response_type,  message):
        """
        Transform message to proper form and send message to 
        correct user
        """
        response = self.make_response('Server', response_type, message)
        self.send_message(socket, response)
    
    def send_message(self, socket, message):
        """
        Sends message to given user, if possible. Socket is given as 
        input because of the broadcast_message method. Not used elsewhere
        """
        try:
            socket.send(message) 
        except:
            print 'Error: Unable to send message'
  
    def make_response(self, sender, response_type, content):
        """
        Transform given message to proper format to send to 
        users
        """
        response = {
            'timestamp': datetime.now().strftime('%d.%M.%Y %H:%M'), # Use DD.MM.YY HH:MM timestamp format
            'sender': sender,
            'response': response_type,
            'content': content }

        return json.dumps(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    This class is present so that each client connected will 
    be ran as a own thread. In that way, all clients will be 
    served by the server.

    No alterations are necessary
    """
    allow_reuse_address = True

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 8888
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
