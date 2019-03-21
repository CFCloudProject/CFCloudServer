import Connector
import mysql
from Models import Block

class BIDConnector(Connector):

    def __init__(self):
        return super().__init__()

    def create_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS BID_TABLE")
        sql = """CREATE TABLE BID_TABLE (
                 B_ID  INT NOT NULL,
                 C_ID  INT,
                 U_START INT,  
                 U_COUNT INT,  
                 SIZE INT)"""
        self.cursor.execute(sql)

    def insert(self, block):
        sql = "INSERT INTO BID_TABLE\
            (B_ID, C_ID, U_START, U_COUNT, SIZE) \
           VALUES ('%d', '%d', '%d', '%d', '%d' )" % \
           (block.block_id, block.container_id, block.unit_start, block.unit_count, block.size)
        try:
           # Execute the SQL command
           self.cursor.execute(sql)
           self.conn.commit()
           return True
        except:
           # Rollback in case there is any error
           self.conn.rollback()
           return False
    
    def find(self, block_id):
        sql = "SELECT * FROM BID_TABLE \
               WHERE B_ID = '%d'" % (block_id)
        try:
           # Execute the SQL command
           self.cursor.execute(sql)
           results = self.cursor.fetchall()
           ret = results[0]
           return Block(ret[0], ret[1], ret[2], ret[3], ret[4])
        except:
           return None

