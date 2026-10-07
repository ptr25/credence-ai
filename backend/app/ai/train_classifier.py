import json, pathlib,joblib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,ConfusionMatrixDisplay,RocCurveDisplay
from app.ai.dataset import generate
ROOT=pathlib.Path(__file__).resolve().parents[1]
def scores(y,p,prob): return dict(accuracy=accuracy_score(y,p),precision=precision_score(y,p,zero_division=0),recall=recall_score(y,p,zero_division=0),f1=f1_score(y,p,zero_division=0),rocAuc=roc_auc_score(y,prob))
def train():
    out=ROOT/'results'; out.mkdir(exist_ok=True); rows=generate(); (out/'dataset.json').write_text(json.dumps(rows))
    x=np.array([r['features'] for r in rows]); y=np.array([r['label'] for r in rows]); groups=np.array([r['base'] for r in rows])
    ids=np.random.default_rng(42).permutation(36); tr=np.isin(groups,ids[:24]); va=np.isin(groups,ids[24:30]); te=np.isin(groups,ids[30:])
    candidates={'LogisticRegression':make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,random_state=42)),'RandomForest':RandomForestClassifier(n_estimators=150,max_depth=7,random_state=42,class_weight='balanced')}
    best=None; bestscore=-1
    for name,m in candidates.items():
        m.fit(x[tr],y[tr]); s=f1_score(y[va],m.predict(x[va]));
        if s>bestscore: best,bestscore=(name,m),s
    name,m=best; joblib.dump(m,ROOT/'models/tamper_classifier.joblib')
    metrics=scores(y[te],m.predict(x[te]),m.predict_proba(x[te])[:,1]); metrics.update(classifier=name,datasetSize=len(rows),baseCertificates=36,trainSize=int(tr.sum()),validationSize=int(va.sum()),testSize=int(te.sum()),validationF1=bestscore,split='Grouped by base certificate; 24 train / 6 validation / 6 test',comparison=[])
    for title,cols in [('Global CNN only',[0]),('Global + patch',[0,1,2]),('Global + patch + SSIM',[0,1,2,3,4])]:
        ab=RandomForestClassifier(n_estimators=150,max_depth=7,random_state=42); ab.fit(x[tr][:,cols],y[tr]); metrics['comparison'].append({'method':title,**scores(y[te],ab.predict(x[te][:,cols]),ab.predict_proba(x[te][:,cols])[:,1])})
    from app.ai.plot_results import save_plots
    save_plots(x,y,te,m,out)
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2)); print(json.dumps(metrics,indent=2))
if __name__=='__main__': train()
