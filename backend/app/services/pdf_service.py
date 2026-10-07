import io, hashlib
from PIL import Image
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode
from .vision_service import render
FIELDS={'studentName':'Aarav Sharma','studentId':'AI2026001','studentEmail':'aarav@example.com','course':'Artificial Intelligence and Machine Learning','qualification':'Certificate of Achievement','grade':'A+','department':'Computer Science','issueDate':'2026-10-06','institution':'Indian Institute of Information Technology Kottayam'}
def make_pdf(fields,cid):
    out=io.BytesIO(); c=canvas.Canvas(out,pagesize=(900,636))
    c.setFillColorRGB(.97,.98,1); c.rect(0,0,900,636,fill=1,stroke=0)
    c.setStrokeColorRGB(.2,.25,.5); c.setLineWidth(3); c.rect(24,24,852,588)
    def text(x,y,s,size=16):
        c.setFillColorRGB(.08,.12,.25); c.setFont('Helvetica',size); c.drawCentredString(x,y,str(s))
    text(450,560,fields['institution'],21); text(450,510,'CERTIFICATE OF ACHIEVEMENT',27)
    text(450,454,'This certifies that',15); text(450,410,fields['studentName'],32)
    text(450,370,'Student ID: '+fields['studentId'],14)
    text(450,328,'has successfully completed',15); text(450,294,fields['course'],20)
    text(450,252,fields['qualification'],16); text(450,208,'Grade: '+fields['grade'],25)
    text(450,168,fields['department']+'  |  Issued: '+fields['issueDate'],14)
    text(450,130,cid,14)
    qr=qrcode.make('http://localhost:3000/verify?id='+cid)
    c.drawImage(ImageReader(qr.get_image()),744,72,84,84)
    text(450,75,'SECURED BY CREDENCE AI',13)
    text(450,53,'AI Visual Fingerprint | SHA-256 | CredenceID Prototype',10)
    c.save()
    im=render(out.getvalue()); im=embed(im,cid)
    return image_pdf(im)
def payload(cid): return cid+'|'+hashlib.sha256(cid.encode()).hexdigest()[:8]
def embed(im,cid):
    arr=np.asarray(im).copy(); bits=np.unpackbits(np.frombuffer((payload(cid)+'\0').encode(),dtype=np.uint8))
    flat=arr.reshape(-1); flat[:len(bits)]=(flat[:len(bits)]&254)|bits
    return Image.fromarray(arr)
def extract(im):
    bits=np.asarray(im).reshape(-1)[:512]&1
    try:
        val=np.packbits(bits).tobytes().split(b'\0')[0].decode(); cid=val.split('|')[0]
        return cid if val==payload(cid) else None
    except Exception: return None
def image_pdf(im):
    out=io.BytesIO(); c=canvas.Canvas(out,pagesize=(900,636)); c.drawImage(ImageReader(im),0,0,900,636); c.save(); return out.getvalue()
