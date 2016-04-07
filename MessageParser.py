import json

class MessageParser():
    def __init__(self):

        self.possible_responses = {
            'error': self.parse_error,
            'info': self.parse_info,
            'message': self.parse_message,
            'help': self.parse_help,
            'username': self.parse_username,
            'history': self.parse_history
	    # More key:values pairs are needed	
        }

    def parse(self, payload):
        """
        Convert message from json to ASCII, checks if it's 
        valid. If it's valid, the proper method is called and 
        information is displayed to the user
        """
        payload = json.loads(payload)
        
        if payload['response'] in self.possible_responses:
            return self.possible_responses[payload['response']](payload)
        else:
            print 'Response not valid'

    def parse_error(self, payload):
        return payload['content']
    
    def parse_info(self, payload):
        return payload['content']
    
    def parse_message(self, payload):
        return 'User \'' + payload['sender'] + '\' said: ' + payload['content']

    def parse_help(self, payload):
        return payload['content']
    
    def parse_username(self, payload):
        return payload['content']

    def parse_history(self, payload):
        return payload['content']
    
    def parse_dataToSend(self, data):
        if data.startswith('login'):
            username = data[6:]
            data = {'request': 'login', 'content': username}
        elif data.startswith('logout'):
            data = {'request': 'logout', 'content': None}
        elif data.startswith("msg"):
            msg = data[4:]
            data = {'request': 'msg', 'content': msg}
        elif data.startswith('names'):
            data = {'request': 'names', 'content': None}
        elif data.startswith('help'):
            data = {'request': 'help', 'content': None} 
        elif data.startswith('username'):
            data = {'request': 'username', 'content': None} 
        else:
            print "Invalid message. Server will ignore message."
            data = {'request': 'error', 'content': None}
            
        #print data
        return json.dumps(data)
            
