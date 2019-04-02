import mysql.connector
import config

class block_index():

    def __init__(self):
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

    def update_list(self, blocks):
        sql = "UPDATE `b_index` SET `container_id` = CASE `block_id` \n"
        for block in blocks:
            sql += "WHEN '%s' THEN %d \n" % (block['block_id'], block['container_id'])
        sql += "END, `offset` = CASE `block_id` \n"
        for block in blocks:
            sql += "WHEN '%s' THEN %d \n" % (block['block_id'], block['offset'])
        sql += "END, `size` = CASE `block_id` \n"
        for block in blocks:
            sql += "WHEN '%s' THEN %d \n" % (block['block_id'], block['size'])
        sql += "END WHERE `block_id` IN ("
        for block in blocks:
            sql += "'%s', " % (block['block_id'])
        sql = sql[:-2] + ')'

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

    def select_list(self, ids):
        sql = "SELECT * FROM `b_index` WHERE `block_id` IN ("
        for block_id in ids:
            sql = sql + "'%s', " % (block_id)
        sql = sql[:-2] + ")"
        try:
           self.cursor.execute(sql)
           ret = self.conn.cursor.fetchall()
           if ret is None:
               return None
           blocks = {}
           for row in ret:
               if blocks.get(row[1]) is None:
                   blocks[row[1]] = [{ 'block_id': row[0], 'container_id': row[1], 'offset': row[2], 'size': row[3] }]
               else:
                   blocks[row[1]].append({ 'block_id': row[0], 'container_id': row[1], 'offset': row[2], 'size': row[3] })
           return blocks
        except:
           return None
