import mysql
from Models.Block import Block
from . import Connector

class BlockIndex():

    def __init__(self, connector, table):
        self.conn = connector
        self.table = table

    def create_table(self):
        self.conn.cursor.execute('DROP TABLE IF EXISTS ' + table)
        sql = "CREATE TABLE %s (BLOCK_ID VARCHAR(255) NOT NULL, CONTAINER_ID INT, OFFSET INT, SIZE INT)" % self.table
        self.conn.cursor.execute(sql)

    def insert(self, block):
        sql = "INSERT INTO %s (BLOCK_ID, CONTAINER_ID, OFFSET, SIZE) VALUES ('%s', %d, %d, %d)" \
            % (self.table, block.block_id, block.container_id, block.offset, block.size)
        try:
           # Execute the SQL command
           self.conn.cursor.execute(sql)
           self.conn.conn.commit()
           return True
        except:
           # Rollback in case there is any error
           self.conn.conn.rollback()
           return False

    def delete(self, block_id):
        sql = "DELETE FROM %s WHERE BLOCK_ID = '%s'" % (self.table, block_id)
        try:
           # Execute the SQL command
           self.conn.cursor.execute(sql)
           self.conn.conn.commit()
           return True
        except:
           # Rollback in case there is any error
           self.conn.conn.rollback()
           return False

    def update(self, block):
        sql = "UPDATE %s SET CONTAINER_ID = %d, OFFSET = %d, SIZE = %d WHERE BLOCK_ID = '%s'" \
           % (self.table, block.container_id, block.offset, block.size, block.block_id)
        try:
           # Execute the SQL command
           self.conn.cursor.execute(sql)
           self.conn.conn.commit()
           return True
        except:
           # Rollback in case there is any error
           self.conn.conn.rollback()
           return False
    
    def select(self, block_id):
        sql = "SELECT * FROM %s WHERE BLOCK_ID = '%s'" % (self.table, block_id)
        try:
           # Execute the SQL command
           self.conn.cursor.execute(sql)
           results = self.conn.cursor.fetchall()
           ret = results[0]
           return Block(ret[0], ret[1], ret[2], ret[3])
        except:
           return None
