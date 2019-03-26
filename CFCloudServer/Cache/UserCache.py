import Models.User as User
import sqlite3
import uuid

class UserCache(object):

    def __init__(self, dbpath):
        self.conn = sqlite3.connect(dbpath)
        cursor = self.conn.cursor()
        sql = "CREATE TABLE IF NOT EXISTS USER (USERID INT, EMAIL TEXT, PASSWORD TEXT, FIRSTNAME TEXT, LASTNAME TEXT);"
        cursor.execute(sql)
        sql = "CREATE TABLE IF NOT EXISTS SESSION (SESSIONID TEXT, USERID INT);"
        cursor.execute(sql)
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def register(self, email, password, firstname, lastname):
        sql = "SELECT * FROM USER WHERE EMAIL = '%s'" % email
        ret = self.conn.cursor().execute(sql).fetchall()
        if len(ret) > 0:
            return None
        else:
            user = User.User(email, password, firstname, lastname)
            sql = "INSERT INTO USER (USERID, EMAIL, PASSWORD, FIRSTNAME, LASTNAME) VALUES (%d, '%s', '%s', '%s', '%s')" \
                    % (user.userid, email, password, firstname, lastname)
            self.conn.cursor().execute(sql)
            self.conn.commit()
            return user

    def login(self, email, password):
        sql = "SELECT * FROM USER WHERE EMAIL = '%s'" % email
        ret = self.conn.cursor().execute(sql).fetchone()
        if ret is None:
            return 1, None, None, None
        else:
            if ret[2] != password:
                return 2, None, None, None
            else:
                session_id = uuid.uuid1()
                sql = "INSERT INTO SESSION (SESSIONID, USERID) VALUES ('%s', %d)" % (session_id, ret[0])
                self.conn.cursor().execute(sql)
                self.conn.commit()
                return 0, session_id, ret[3], ret[4]

    def logout(self, session_id):
        sql = "DELETE FROM SESSION WHERE SESSIONID = '%s'" % session_id
        self.conn.cursor().execute(sql)
        self.conn.commit()

    def get_user_by_email(self, email):
        sql = "SELECT * FROM USER WHERE EMAIL = '%s'" % email
        ret = self.conn.cursor().execute(sql).fetchone()
        if ret is None:
            return None
        else:
            user = User.User(ret[1], ret[2], ret[3], ret[4], ret[0])
            return user

    def get_user(self, session_id):
        sql = "SELECT * FROM SESSION WHERE SESSIONID = '%s'" % session_id
        ret = self.conn.cursor().execute(sql).fetchone()
        if ret is None:
            return None
        else:
            user = User.User(ret[1], ret[2], ret[3], ret[4], ret[0])
            return user

    def get_sessions(self, user):
        sql = "SELECT * FROM SESSION WHERE USERID = '%s'" % user.userid
        ret = self.conn.cursor().execute(sql).fetchall()
        sessions = []
        for row in ret:
            sessions.append(row[0])
        return sessions