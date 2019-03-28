import mysql
import config

class block_index():

    def __init__(self, connector, table):
        self.conn = mysql.connector.connect(**config.mysql_config)
        self.cursor = self.conn.cursor()
        sql = "CREATE TABLE IF NOT EXISTS `b_index` (`block_id` VARCHAR(255) NOT NULL, `container_id` INT, `offset` INT, `size` INT)"
        self.cursor.execute(sql)

    def __del__(self):
        self.conn.close()

    def insert(self, block):
        sql = "INSERT INTO `b_index` (`block_id`, `container_id`, `offset`, `size`) VALUES ('%s', %d, %d, %d)" \
            % (block['block_id'], block['container_id'], block['offset'], block['size'])
        try:
           self.cursor.execute(sql)
           self.conn.commit()
           return True
        except:
           self.conn.rollback()
           return False

    def delete(self, block_id):
        sql = "DELETE FROM `b_index` WHERE `block_id` = '%s'" % (block_id)
        try:
           self.cursor.execute(sql)
           self.conn.commit()
           return True
        except:
           self.conn.rollback()
           return False

    def update(self, block):
        sql = "UPDATE `b_index` SET `container_id` = %d, `offset` = %d, `size` = %d WHERE `block_id` = '%s'" \
           % (block['container_id'], block['offset'], block['size'], block['block_id'])
        try:
           self.cursor.execute(sql)
           self.conn.commit()
           return True
        except:
           self.conn.rollback()
           return False
    
    def select(self, block_id):
        sql = "SELECT * FROM `b_index` WHERE `block_id` = '%s'" % (block_id)
        try:
           self.cursor.execute(sql)
           ret = self.conn.cursor.fetchone()
           if ret is None:
               return None
           return { 'block_id': ret[0], 'container_id': ret[1], 'offset': ret[2], 'size': ret[3] }
        except:
           return None
