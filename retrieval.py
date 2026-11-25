import json
from config import ROOT
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
class Retriever:
    def __init__(self):
        self.records=json.loads((ROOT/'data/exam_knowledge.json').read_text(encoding='utf-8'))
        self.vectorizer=TfidfVectorizer(stop_words='english',ngram_range=(1,2))
        self.matrix=self.vectorizer.fit_transform([r['topic']+' '+r['question']+' '+r['answer'] for r in self.records])
    def search(self,q):
        scores=cosine_similarity(self.vectorizer.transform([q]),self.matrix)[0]
        return [dict(self.records[i],score=round(float(scores[i]),4)) for i in scores.argsort()[::-1][:3] if scores[i]>=.08]
