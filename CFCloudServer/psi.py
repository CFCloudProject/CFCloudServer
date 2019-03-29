import sqlite3

class psi(object):

    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        cursor = self.conn.cursor()
        sql = "CREATE TABLE IF NOT EXISTS PSI (FILEPATH TEXT, PSID TEXT);"
        cursor.execute(sql)
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def insert(self, filepath, psid):
        sql = "INSERT INTO PSI (FILEPATH, PSID) VALUES ('%s', '%s;)" % (filepath, psid)
        self.conn.cursor().execute(sql)
        self.conn.commit()

    def update(self, filepath, psid):
        sql = "UPDATE PSI SET PSID = '%s' WHERE FILEPATH = '%s'" % (psid, filepath)
        self.conn.cursor().execute(sql)
        self.conn.commit()

    def delete_by_filepath(self, filepath):
        sql = "DELETE FROM PSI WHERE FILEPATH = '%s'" % (filepath)
        self.conn.cursor().execute(sql)
        self.conn.commit()

    def delete_by_psid(self, psid):
        sql = "DELETE FROM PSI WHERE PSID = '%s'" % (psid)
        self.conn.cursor().execute(sql)
        self.conn.commit()

    def get_psid_by_filepath(self, filepath):
        sql = "SELECT * FROM PSI WHERE FILEPATH = '%s'" % (filepath)
        ret = self.conn.cursor().execute(sql).fetchone()
        if ret is not None:
            return ret[1]
        else:
            return None
