import sqlite3


class db(): 

    def __init__(self) -> None:
        self.connection = sqlite3.connect('TwitterGrabber.db')
        self.cursor = self.connection.cursor()

    def usernames(self):
        self.cursor.execute('SELECT username FROM usernames')
        users = self.cursor.fetchall()

        return users
    

    def GetPublishedAt(self, username):
        self.cursor.execute('SELECT published_at FROM Information WHERE username = ?', (username,))
        LastTweetId = self.cursor.fetchall()
        
        return LastTweetId
    
    def GetLastWorkTime(self):
        self.cursor.execute('SELECT lastWorkTime FROM Information')
        LastWorkTime = self.cursor.fetchall()
        
        return LastWorkTime
    
    def GetCheckPeriod(self):
        self.cursor.execute('SELECT checkPeriod FROM Information')
        CheckPeriod = self.cursor.fetchall()
        
        return CheckPeriod
    
    def GetActive(self):
        self.cursor.execute('SELECT active FROM Information')
        Active = self.cursor.fetchall()
        
        return Active
    
    def Put(self, username, published_at, lastWorktime,checkPeriod, active):
        self.cursor.execute('INSERT INTO Information(username, published_at, lastWorkTime, checkPeriod, Active) VALUES(?,?,?,?,?)', (username, published_at, lastWorktime,checkPeriod, active))
        self.connection.commit()