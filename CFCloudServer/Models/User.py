class User(object):
    
    def __init__(self, email, password, firstname, lastname):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname

def from_dict(dict):
    return User(dict.get('email'), 
                dict.get('password'),
                dict.get('firstname'),
                dict.get('lastname'))


