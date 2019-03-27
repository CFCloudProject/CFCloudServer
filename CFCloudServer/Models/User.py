import Global

class User(object):
    
    def __init__(self, email, password, firstname, lastname, userid = None):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.userid = userid
        if self.userid is None:
            self.userid = Global.get_new_user_id()


def from_dict(dict):
    return User(dict.get('email'), 
                dict.get('password'),
                dict.get('firstname'),
                dict.get('lastname'),
                dict.get('userid'))


