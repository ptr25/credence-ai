import io
import numpy as np
from PIL import Image,ImageDraw,ImageEnhance,ImageFilter
from app.services.pdf_service import make_pdf,FIELDS,image_pdf
from app.services.vision_service import render,embedding,compare

def variant(im,kind,rng):
    if kind=='original': return im.copy()
    if kind=='jpeg':
        buf=io.BytesIO(); im.save(buf,format='JPEG',quality=75); return Image.open(io.BytesIO(buf.getvalue())).convert('RGB')
    if kind=='resize': return im.resize((720,509)).resize(im.size)
    if kind=='rerender': return render(image_pdf(im))
    if kind=='blur': return im.filter(ImageFilter.GaussianBlur(.35))
    if kind=='brightness': return ImageEnhance.Brightness(im).enhance(.96)
    if kind=='contrast': return ImageEnhance.Contrast(im).enhance(.95)
    if kind=='noise': return Image.fromarray(np.clip(np.asarray(im).astype(float)+rng.normal(0,1,np.asarray(im).shape),0,255).astype('uint8'))
    out=im.copy(); d=ImageDraw.Draw(out)
    regions={'grade':(365,401,535,437),'name':(265,193,635,237),'course':(150,320,750,352),'id':(330,490,570,510),'cover':(250,260,600,286),'insert':(200,360,620,385),'remove':(335,370,560,398)}
    box=regions[kind]; d.rectangle(box,fill=(247,250,255))
    if kind not in ['cover','remove']: d.text((box[0]+5,box[1]+6),'Grade: O' if kind=='grade' else 'ALTERED CREDENTIAL CONTENT',fill=(20,30,60),font_size=24)
    return out

def generate(n=36):
    rng=np.random.default_rng(42); rows=[]
    good=['original','jpeg','resize','rerender','blur','brightness','contrast','noise']; bad=['grade','name','course','id','cover','insert','remove']
    for i in range(n):
        f={**FIELDS,'studentName':['Aarav Sharma','Meera Nair','Ishaan Rao','Ananya Patel'][i%4]+' '+str(i),'studentId':f'AI2026{i:03d}','course':['Artificial Intelligence and Machine Learning','Data Science','Computer Networks','Software Engineering'][i%4],'grade':['A+','A','B+'][i%3]}
        im=render(make_pdf(f,f'CRED-IIITK-2026-{i+1:06d}')); emb=embedding(im)
        for kind in good+bad:
            feat,_,_=compare(im,variant(im,kind,rng),emb); rows.append({'base':i,'kind':kind,'label':int(kind in bad),'features':feat})
        print(f'Features: base {i+1}/{n}',flush=True)
    return rows
