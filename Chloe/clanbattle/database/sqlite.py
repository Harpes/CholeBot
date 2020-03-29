import os
import sqlite3
from datetime import datetime, timedelta, timezone

DB_PATH = 'clanbattle.db'


def getMonth(time: datetime) -> str:
    day = time - timedelta(hours=5)
    if day.day < 10:
        day -= timedelta(days=day.day)

    return day.strftime("%Y%m")


class DataBaseIO(object):
    def connect(self):
        return sqlite3.connect(DB_PATH)

    def createTable(self, table_name: str, cols: list) -> sqlite3.Connection:
        conn = self.connect()
        create_sql = 'CREATE TABLE IF NOT EXISTS %s(%s)' % (
            table_name, ','.join(cols))
        conn.execute(create_sql)
        return conn

    def createClan(self) -> sqlite3.Connection:
        return self.createTable('clan', [
            'gid INT PRIMARY KEY NOT NULL', 'name TEXT NOT NULL', 'server INT NOT NULL'])

    def addClan(self, gid: int, name: str, server: int):
        conn = self.createClan()

        insert_sql = 'INSERT INTO clan VALUES (%d, "%s", %d)' % (
            gid, name, server)
        conn.execute(insert_sql)

        conn.commit()
        conn.close()

    def getClan(self, gid: int) -> list:
        conn = self.createClan()
        cur = conn.cursor()

        select_sql = 'SELECT name, server FROM clan WHERE gid = %d' % (gid, )
        cur.execute(select_sql)
        result = cur.fetchone()

        conn.commit()
        conn.close()

        return result

    def createMember(self) -> sqlite3.Connection:
        return self.createTable('member', ['gid INT NOT NULL', 'uid INT NOT NULL', 'name TEXT NOT NULL', 'PRIMARY KEY (gid, uid)'])

    def addMember(self, gid: int, uid: int, name: str):
        conn = self.createMember()

        insert_sql = 'INSERT INTO member VALUES (%d, %d, "%s")' % (
            gid, uid, name)
        conn.execute(insert_sql)

        conn.commit()
        conn.close()

    def getMember(self, gid: int, uid: int = None):
        conn = self.createMember()
        cur = conn.cursor()

        select_sql = 'SELECT uid, name FROM member WHERE gid = %d' % (gid, )
        if not uid is None:
            select_sql += ' AND uid = %d' % (uid, )
        cur.execute(select_sql)
        result = cur.fetchall()

        conn.commit()
        conn.close()

        return result

    def createRecs(self) -> list:
        month = getMonth(datetime.now())
        return (self.createTable('rec' + month, ['recid INTEGER PRIMARY KEY AUTOINCREMENT',
                                                 'gid INT NOT NULL', 'uid INT NOT NULL',
                                                 'time TIMESTAMP NOT NULL', 'round INT NOT NULL',
                                                 'boss INT NOT NULL', 'dmg INT NOT NULL',
                                                 'flag INT NOT NULL']), month)

    def addRec(self, gid: int, uid: int, r: int, b: int, dmg: int, flag: int):
        conn, month = self.createRecs()

        insert_sql = 'INSERT INTO rec%s VALUES (NULL, %d, %d, "%s", %d, %d, %d, %d)' % (
            month, gid, uid, datetime.now().strftime('%Y/%m/%d %H:%M'), r, b, dmg, flag)
        conn.execute(insert_sql)

        conn.commit()
        conn.close()

    def getRec(self, gid: int, uid: int = None, time: datetime = None) -> list:
        conn, month = self.createRecs()
        cur = conn.cursor()

        select_sql = 'SELECT * FROM rec%s WHERE gid = %d' % (month, gid)
        if not uid is None:
            select_sql += ' AND uid = %d' % (uid, )
        if not time is None:
            select_sql += ' AND time > "%s"' % (
                time.strftime('%Y/%m/%d %H:%M'), )
        cur.execute(select_sql)
        result = cur.fetchall()

        conn.commit()
        conn.close()

        return result

    def delRec(self, recid: int):
        conn, month = self.createRecs()

        delete_sql = 'DELETE FROM rec%d WHERE recid = %d' % (month, recid)
        conn.execute(delete_sql)

        conn.commit()
        conn.close()