import hashlib,joblib
import numpy as np
from fastapi.testclient import TestClient
from app.main import app,ROOT
from app.services.vision_service import render,embedding,patches,compare
from app.services.pdf_service import FIELDS,extract

def test_complete_demo():
    with TestClient(app) as c:
        assert c.post('/api/auth/login',json={'email':'bad','password':'bad'}).status_code==401
        token=c.post('/api/auth/login',json={'email':'admin@iiitk.ac.in','password':'credence123'}).json()['token']; headers={'Authorization':'Bearer '+token}
        a=c.post('/api/certificates/issue',json=FIELDS,headers=headers); assert a.status_code==200,a.text
        obj=a.json(); cid=obj['certificateId']; assert cid.startswith('CRED-IIITK-2026-')
        other=c.post('/api/certificates/issue',json=FIELDS,headers=headers).json(); assert other['certificateId']!=cid
        data=c.get('/api/certificates/'+cid+'/download').content
        assert hashlib.sha256(data).hexdigest()==obj['documentHash']
        im=render(data); assert extract(im)==cid
        assert len(patches(im))==9
        e=embedding(im); assert e.shape==(10,512); assert np.allclose(np.linalg.norm(e,axis=1),1)
        f,_,_=compare(im,im,e); assert f[0]>.99999
        assert hasattr(joblib.load(ROOT/'models/tamper_classifier.joblib'),'predict_proba')
        original=c.post('/api/verify',files={'file':('original.pdf',data,'application/pdf')},data={'certificateId':cid}).json(); assert original['result']=='VERIFIED',original
        transformed=c.post('/api/demo/'+cid+'/transform',headers=headers).json()['verification']; assert not transformed['hashMatch']; assert transformed['result']=='TRANSFORMED_COPY',transformed
        tampered=c.post('/api/demo/'+cid+'/tamper',headers=headers).json()['verification']; assert tampered['result']=='TAMPERING_SUSPECTED',tampered
        assert c.get(tampered['heatmapPath']).status_code==200
        assert c.post('/api/certificates/'+cid+'/revoke',json={'reason':''},headers=headers).status_code==400
        assert c.post('/api/certificates/'+cid+'/revoke',json={'reason':'Demo revocation'},headers=headers).status_code==200
        revoked=c.post('/api/verify',files={'file':('original.pdf',data)},data={'certificateId':cid}).json(); assert revoked['result']=='REVOKED'
        assert c.get('/api/ai/metrics').json()['testSize']>0
        assert c.get('/api/analytics',headers=headers).status_code==200
