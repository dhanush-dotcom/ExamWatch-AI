import base64, threading
try:
    import cv2, numpy as np
except ImportError:
    cv2=None
class Vision:
    def __init__(self):
        self.face=None; self.lock=threading.Lock(); self.previous={}; self.object_model=None
        if cv2 is not None:
            self.face=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
            if self.face.empty(): self.face=None
        from config import ROOT
        path=ROOT/'models/yolo11n.pt'
        if path.exists():
            try:
                from ultralytics import YOLO
                self.object_model=YOLO(str(path))
            except Exception: pass
    def decode(self,data):
        if not isinstance(data,str) or len(data)>3000000: raise ValueError('Invalid image size')
        raw=base64.b64decode(data.split(',')[-1],validate=True)
        if cv2 is None: raise ValueError('OpenCV unavailable')
        img=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
        if img is None or img.shape[0]*img.shape[1]>4000000: raise ValueError('Invalid image')
        return img
    def analyze(self,img,sid):
        if self.face is None: return {'mode':'unavailable','events':[],'message':'Face detector unavailable; no predictions made.'}
        with self.lock:
            gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            faces=self.face.detectMultiScale(gray,1.1,5,minSize=(35,35)); n=len(faces); events=[]
            def add(t,d,c=None): events.append({'type':t,'description':d,'confidence':c})
            if n==0: add('Face not detected','No frontal face detected in this frame.')
            if n>1: add('Multiple faces detected',f'{n} frontal face regions detected.')
            old=self.previous.get(sid); center=None
            if n==1:
                x,y,w,h=faces[0]; center=((x+w/2)/img.shape[1],(y+h/2)/img.shape[0])
            if old is not None:
                if old[0]!=n: add('Face count changed','Visible face count changed; entry or exit is not confirmed.')
                if center and old[1] and sum(abs(a-b) for a,b in zip(center,old[1]))>.22: add('Face position changed','Face bounding box moved substantially; head orientation is unknown.')
            self.previous[sid]=(n,center)
            if self.object_model:
                for result in self.object_model.predict(img,verbose=False,device='cpu',conf=.5):
                    for b in result.boxes:
                        if result.names[int(b.cls.item())]=='cell phone': add('Possible phone visible','Object model detected a possible phone.',float(b.conf.item()))
            return {'mode':'opencv','faces':n,'events':events}
