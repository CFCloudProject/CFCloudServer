import mysql
import Config

class Connector(object):
    
    def __init__(self):
        self.conn = mysql.connector.connect(**Config.config)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()
