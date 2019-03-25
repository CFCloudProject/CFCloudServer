import mysql.connector
import Global

class Connector(object):
    
    def __init__(self):
        self.conn = mysql.connector.connect(**Global.mysql_config)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()
