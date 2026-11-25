from flask import Flask,render_template,request,jsonify
from event_manager import Store
from retrieval import Retriever
from vision import Vision
import ai_assistant as ai
from config import DB,MODEL
import sqlite3

def create_app(db=DB):
    app=Flask(__name__); app.config['MAX_CONTENT_LENGTH']=4_000_000
    store=Store(db); retriever=Retriever(); vision=Vision()
    def body():
        d=request.get_json(silent=True)
        if not isinstance(d,dict): raise ValueError('Expected JSON object')
        return d
    def string(d,k,maxlen=2000):
        v=d.get(k,'')
        if not isinstance(v,str) or len(v)>maxlen: raise ValueError('Invalid '+k)
        return v.strip()
    @app.errorhandler(ValueError)
    def invalid(e): return jsonify(error=str(e)),400
    @app.errorhandler(sqlite3.Error)
    def database(e): return jsonify(error='Database operation failed'),500
    @app.errorhandler(413)
    def large(e): return jsonify(error='Request too large'),413
    @app.get('/')
    def home(): return render_template('index.html')
    @app.get('/exam')
    def exam(): return render_template('exam.html')
    @app.get('/dashboard')
    def dashboard(): return render_template('dashboard.html')
    @app.get('/api/health')
    def health(): return jsonify(status='ok',dataset_count=len(retriever.records),model=MODEL,ollama=ai.available(),vision=vision.face is not None,object_detection=vision.object_model is not None)
    @app.post('/api/session/start')
    def start():
        if body().get('consent') is not True: raise ValueError('Consent required')
        return jsonify(store.start())
    @app.post('/api/session/end')
    def end():
        sid=string(body(),'session_id')
        if not store.active(sid): raise ValueError('Invalid active session')
        s=ai.summary(store.rows('SELECT * FROM events WHERE session_id=?',(sid,)))
        store.end(sid,s); vision.previous.pop(sid,None); return jsonify(summary=s)
    @app.post('/api/analyze-frame')
    def frame():
        d=body(); sid=string(d,'session_id')
        if not store.active(sid): raise ValueError('Invalid active session')
        try: img=vision.decode(d.get('image'))
        except Exception: raise ValueError('Invalid image or unavailable decoder')
        result=vision.analyze(img,sid)
        for e in result['events']: e['recorded']=store.event(sid,e['type'],e['description'],e['confidence'])
        return jsonify(result)
    @app.get('/api/events')
    def events(): return jsonify(events=store.rows('SELECT * FROM events ORDER BY id DESC'),sessions=store.rows('SELECT * FROM sessions ORDER BY started DESC'))
    @app.post('/api/events/review')
    def review():
        d=body(); status=string(d,'status')
        if status not in ('reviewed','attention','pending') or not isinstance(d.get('event_id'),int): raise ValueError('Invalid review')
        if not store.review(d['event_id'],status,string(d,'comments')): raise ValueError('Event not found')
        return jsonify(ok=True)
    @app.post('/api/ask')
    def ask():
        q=string(body(),'question')
        if not q: raise ValueError('Enter a question')
        return jsonify(ai.answer(q,retriever))
    @app.post('/api/feedback')
    def feedback():
        d=body(); t=string(d,'type'); q=string(d,'question')
        if t not in ('helpful','not_helpful') or not q: raise ValueError('Invalid feedback')
        store.feedback(q,t,string(d,'comment')); return jsonify(ok=True)
    return app
if __name__=='__main__': create_app().run(host='127.0.0.1',port=5000,debug=False)
