import os,io,json,sqlite3,hashlib,secrets,datetime
from pathlib import Path
from contextlib import asynccontextmanager
import joblib,numpy as np
from PIL import Image
from fastapi import FastAPI,HTTPException,UploadFile,File,Form,Header,Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.vision_service import engine,render,embedding,compare
from app.services.pdf_service import make_pdf,FIELDS,extract,image_pdf
from app.ai.dataset import variant
ROOT=Path(__file__).parent; STORAGE=ROOT/'storage'; STORAGE.mkdir(exist_ok=True)
TOKENS={}; LAST=None
SALT=b'credence-demo-user-v1'
PASSWORD=hashlib.pbkdf2_hmac('sha256',b'credence123',SALT,200000).hex()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def db():
    c=sqlite3.connect(STORAGE/'registry.db'); c.row_factory=sqlite3.Row; return c
def init():
    with db() as c:
        c.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,email TEXT UNIQUE,passwordHash TEXT,role TEXT)')
        c.execute('INSERT OR IGNORE INTO users VALUES(1,?,?,?,?)',('Institute Administrator','admin@iiitk.ac.in',PASSWORD,'admin'))
        c.execute('CREATE TABLE IF NOT EXISTS certificates(id INTEGER PRIMARY KEY AUTOINCREMENT,certificateId TEXT UNIQUE,data TEXT,status TEXT,createdAt TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS verifications(id INTEGER PRIMARY KEY AUTOINCREMENT,certificateId TEXT,data TEXT,createdAt TEXT)')
@asynccontextmanager
async def lifespan(app):
    init(); engine()
    if not (ROOT/'models/tamper_classifier.joblib').exists(): raise RuntimeError('Train classifier before starting: PYTHONPATH=backend .venv/bin/python -m app.ai.train_classifier')
    yield
app=FastAPI(title='Credence AI',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:3000'],allow_methods=['*'],allow_headers=['*'])
app.mount('/storage',StaticFiles(directory=STORAGE),name='storage'); app.mount('/results',StaticFiles(directory=ROOT/'results'),name='results')
def admin(authorization:str=Header(default='')):
    token=authorization.removeprefix('Bearer ')
    if TOKENS.get(token,0)<datetime.datetime.now().timestamp(): raise HTTPException(401,'Sign in required')
class Login(BaseModel):
    email:str; password:str
@app.post('/api/auth/login')
def login(body:Login):
    p=hashlib.pbkdf2_hmac('sha256',body.password.encode(),SALT,200000).hex()
    if body.email!='admin@iiitk.ac.in' or not secrets.compare_digest(p,PASSWORD): raise HTTPException(401,'Incorrect login')
    token=secrets.token_urlsafe(32); TOKENS[token]=datetime.datetime.now().timestamp()+28800
    return {'token':token,'name':'Institute Administrator'}
def get_cert(cid):
    with db() as c: r=c.execute('SELECT * FROM certificates WHERE certificateId=?',(cid,)).fetchone()
    if not r: raise HTTPException(404,'Certificate not found')
    return {**json.loads(r['data']),'status':r['status'],'createdAt':r['createdAt']}
@app.post('/api/certificates/issue',dependencies=[Depends(admin)])
def issue(fields:dict):
    f={**FIELDS,**{k:str(v)[:200] for k,v in fields.items() if k in FIELDS}}
    with db() as c:
        c.execute('BEGIN IMMEDIATE'); cur=c.execute('INSERT INTO certificates(data,status,createdAt) VALUES(?,?,?)',('{}','ACTIVE',now()))
        cid=f'CRED-IIITK-2026-{cur.lastrowid:06d}'; data=make_pdf(f,cid); path=STORAGE/(cid+'.pdf'); path.write_bytes(data)
        im=render(data); im.save(STORAGE/(cid+'.png')); emb=embedding(im)
        obj={**f,'certificateId':cid,'documentHash':hashlib.sha256(data).hexdigest(),'globalEmbedding':emb[0].tolist(),'patchEmbeddings':emb[1:].tolist(),'referenceImagePath':cid+'.png','filePath':cid+'.pdf','credenceIdHash':hashlib.sha256(cid.encode()).hexdigest()}
        c.execute('UPDATE certificates SET certificateId=?,data=? WHERE id=?',(cid,json.dumps(obj),cur.lastrowid))
    return get_cert(cid)
@app.get('/api/certificates',dependencies=[Depends(admin)])
def certificates():
    with db() as c:
        rows=c.execute('SELECT certificateId FROM certificates ORDER BY id DESC').fetchall()
        counts=dict(c.execute('SELECT certificateId,count(*) FROM verifications GROUP BY certificateId').fetchall())
    return [{k:v for k,v in {**get_cert(r[0]),'verificationCount':counts.get(r[0],0)}.items() if k not in ['globalEmbedding','patchEmbeddings']} for r in rows]
@app.get('/api/certificates/{cid}')
def certificate(cid:str): return {k:v for k,v in get_cert(cid).items() if k not in ['globalEmbedding','patchEmbeddings','studentEmail']}
@app.get('/api/certificates/{cid}/download')
def download(cid:str): return FileResponse(STORAGE/get_cert(cid)['filePath'],media_type='application/pdf',filename=cid+'.pdf')
@app.post('/api/certificates/{cid}/revoke',dependencies=[Depends(admin)])
def revoke(cid:str,body:dict):
    obj=get_cert(cid); reason=str(body.get('reason','')).strip()
    if not reason: raise HTTPException(400,'Revocation reason required')
    obj.update(revocationReason=reason,revokedAt=now())
    with db() as c: c.execute('UPDATE certificates SET status=?,data=? WHERE certificateId=?',('REVOKED',json.dumps(obj),cid))
    return {'status':'REVOKED'}
def verify_bytes(data,cid):
    global LAST
    try: im=render(data)
    except Exception as e: raise HTTPException(400,'Invalid document: '+str(e))
    hidden=extract(im); cid=cid or hidden
    if not cid: return {'result':'NOT_FOUND','message':'Enter the registered certificate ID; transformed files may lose the prototype watermark.'}
    try: obj=get_cert(cid)
    except HTTPException: return {'result':'NOT_FOUND','certificateId':cid}
    ref=Image.open(STORAGE/obj['referenceImagePath']).convert('RGB'); a=np.array([obj['globalEmbedding']]+obj['patchEmbeddings'])
    f,ps,diff=compare(ref,im,a); model=joblib.load(ROOT/'models/tamper_classifier.joblib'); prob=model.predict_proba([f])[0]; pred=int(model.predict([f])[0]); confidence=float(prob[pred])
    match=hashlib.sha256(data).hexdigest()==obj['documentHash']; result='TAMPERING_SUSPECTED' if pred else ('VERIFIED' if match else 'TRANSFORMED_COPY')
    if confidence<.65: result='REVIEW_RECOMMENDED'
    if obj['status']=='REVOKED': result='REVOKED'
    uid=secrets.token_hex(8); strength=np.clip(diff.mean(axis=2)*6,0,1); overlay=np.array(im).astype(float); overlay[:,:,0]=overlay[:,:,0]*(1-strength)+255*strength; overlay[:,:,1:]*=(1-strength[:,:,None]); Image.fromarray(overlay.astype('uint8')).save(STORAGE/(uid+'.png'))
    LAST=now(); out={'certificateId':cid,'uploadedHash':hashlib.sha256(data).hexdigest(),'hashMatch':match,'globalSimilarity':f[0],'averagePatchSimilarity':f[1],'minimumPatchSimilarity':f[2],'structuralSimilarity':f[3],'pixelDifference':f[4],'patchSimilarities':ps,'mostAnomalousPatch':int(np.argmin(ps))+1,'modelPrediction':['AUTHENTIC_OR_TRANSFORMED','TAMPERED'][pred],'modelConfidence':confidence,'credenceIdStatus':'VALID' if hidden==cid else ('MISMATCH' if hidden else 'UNAVAILABLE'),'result':result,'heatmapPath':'/storage/'+uid+'.png','createdAt':LAST,'revocationReason':obj.get('revocationReason')}
    with db() as c: c.execute('INSERT INTO verifications(certificateId,data,createdAt) VALUES(?,?,?)',(cid,json.dumps(out),LAST))
    return out
@app.post('/api/verify')
async def verify(file:UploadFile=File(...),certificateId:str=Form(default='')):
    data=await file.read(15*1024*1024+1)
    if len(data)>15*1024*1024: raise HTTPException(413,'Maximum file size is 15 MB')
    return verify_bytes(data,certificateId.strip())
@app.get('/api/verifications',dependencies=[Depends(admin)])
def history():
    with db() as c: return [json.loads(r[0]) for r in c.execute('SELECT data FROM verifications ORDER BY id DESC LIMIT 500')]
@app.get('/api/ai/metrics')
def metrics(): return json.loads((ROOT/'results/metrics.json').read_text())
@app.get('/api/ai/status')
def status(): return {'online':True,'model':'ResNet18','weights':'ImageNet pretrained','embeddingDimensions':512,'patchGrid':'3 × 3','classifier':metrics()['classifier'],'testAccuracy':metrics()['accuracy'],'lastInference':LAST}
@app.get('/api/analytics',dependencies=[Depends(admin)])
def analytics():
    hs=history(); cs=certificates()
    return {'certificates':len(cs),'verifications':len(hs),'tamperingAlerts':sum(x['result']=='TAMPERING_SUSPECTED' for x in hs),'verified':sum(x['result'] in ['VERIFIED','TRANSFORMED_COPY'] for x in hs),'history':hs}
@app.post('/api/demo/{cid}/{kind}',dependencies=[Depends(admin)])
def demo(cid:str,kind:str):
    if kind not in ['transform','tamper']: raise HTTPException(400,'Unknown demo')
    obj=get_cert(cid); im=Image.open(STORAGE/obj['referenceImagePath']).convert('RGB'); changed=variant(im,'jpeg' if kind=='transform' else 'grade',np.random.default_rng(42)); data=image_pdf(changed); name=cid+'-'+kind+'.pdf'; (STORAGE/name).write_bytes(data)
    return {'downloadUrl':'/storage/'+name,'verification':verify_bytes(data,cid)}
