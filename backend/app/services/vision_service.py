import io, hashlib, os
from pathlib import Path
os.environ.setdefault("TORCH_HOME",str(Path(__file__).resolve().parents[1]/"models/torch"))
from functools import lru_cache
import numpy as np
import torch
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
import fitz
from skimage.metrics import structural_similarity

torch.set_num_threads(2)
SIZE=(900,636)
def render(data):
    if data[:4]==b'%PDF':
        doc=fitz.open(stream=data,filetype='pdf')
        if len(doc)!=1: raise ValueError('Upload a single-page certificate')
        pix=doc[0].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
        im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    else: im=Image.open(io.BytesIO(data)).convert('RGB')
    if im.height>im.width: im=im.rotate(90,expand=True)
    return im.resize(SIZE,Image.Resampling.LANCZOS)
@lru_cache(maxsize=1)
def engine():
    weights=ResNet18_Weights.DEFAULT
    model=resnet18(weights=weights)
    model.fc=torch.nn.Identity(); model.eval()
    return model,weights.transforms()
def patches(im):
    w,h=im.size
    return [im.crop((c*w//3,r*h//3,(c+1)*w//3,(r+1)*h//3)) for r in range(3) for c in range(3)]
def embedding(im):
    model,pre=engine()
    with torch.inference_mode():
        v=model(torch.stack([pre(x) for x in [im]+patches(im)])).numpy()
    return v/np.maximum(np.linalg.norm(v,axis=1,keepdims=True),1e-12)
def compare(ref,candidate,a=None):
    a=embedding(ref) if a is None else a
    b=embedding(candidate); cos=np.clip((a*b).sum(axis=1),0,1)
    x=np.asarray(ref).astype(float)/255; y=np.asarray(candidate).astype(float)/255
    diff=np.abs(x-y)
    s=float(structural_similarity(x,y,data_range=1,channel_axis=2))
    features=[float(cos[0]),float(cos[1:].mean()),float(cos[1:].min()),max(0,s),float(diff.mean())]
    return features,cos[1:].tolist(),diff
