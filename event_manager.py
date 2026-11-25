import sqlite3, uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from config import DB

def now(): return datetime.now(timezone.utc).isoformat()
class Store:
    def __init__(self,path=DB):
        self.path=path
        with self.connect() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, student TEXT, started TEXT, ended TEXT, status TEXT, summary TEXT);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, session_id TEXT REFERENCES sessions(id), type TEXT, description TEXT, timestamp TEXT, confidence REAL, status TEXT DEFAULT 'pending', comments TEXT DEFAULT '', image_path TEXT);
CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY, question TEXT, type TEXT, comment TEXT, timestamp TEXT);''')
    @contextmanager
    def connect(self):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row
        try:
            c.execute('PRAGMA foreign_keys=ON'); yield c; c.commit()
        finally: c.close()
    def rows(self,sql,args=()):
        with self.connect() as c: return [dict(r) for r in c.execute(sql,args)]
    def start(self):
        sid=uuid.uuid4().hex
        with self.connect() as c: c.execute('INSERT INTO sessions VALUES(?,?,?,NULL,?,NULL)',(sid,'DEMO-'+sid[:8],now(),'active'))
        return self.rows('SELECT * FROM sessions WHERE id=?',(sid,))[0]
    def active(self,sid): return bool(self.rows("SELECT id FROM sessions WHERE id=? AND status='active'",(sid,)))
    def end(self,sid,summary):
        with self.connect() as c: return c.execute("UPDATE sessions SET ended=?,status='ended',summary=? WHERE id=? AND status='active'",(now(),summary,sid)).rowcount
    def event(self,sid,kind,description,confidence=None):
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            if not c.execute("SELECT id FROM sessions WHERE id=? AND status='active'",(sid,)).fetchone(): return False
            if c.execute("SELECT id FROM events WHERE session_id=? AND type=? AND julianday(timestamp)>julianday('now','-15 seconds')",(sid,kind)).fetchone(): return False
            c.execute('INSERT INTO events(session_id,type,description,timestamp,confidence) VALUES(?,?,?,?,?)',(sid,kind,description,now(),confidence)); return True
    def review(self,eid,status,comments):
        with self.connect() as c: return c.execute('UPDATE events SET status=?,comments=? WHERE id=?',(status,comments,eid)).rowcount
    def feedback(self,q,t,comment):
        with self.connect() as c: c.execute('INSERT INTO feedback(question,type,comment,timestamp) VALUES(?,?,?,?)',(q,t,comment,now()))
