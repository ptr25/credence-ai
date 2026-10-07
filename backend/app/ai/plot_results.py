"""Render the saved evaluation in the Credence UI palette, without retraining."""
import json
from pathlib import Path
import joblib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import confusion_matrix, roc_curve, roc_auc_score

ROOT=Path(__file__).resolve().parents[1]

def save_plots(x,y,test,model,out):
    paper='#fffefa'; ink='#4c2800'; muted='#947c5b'; gold='#f2a900'; orange='#cc7100'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':ink,'axes.labelcolor':muted,'xtick.color':muted,'ytick.color':muted,'axes.edgecolor':'#e5dac8','axes.facecolor':paper,'figure.facecolor':paper,'savefig.facecolor':paper,'axes.spines.top':False,'axes.spines.right':False})
    pred=model.predict(x[test]); prob=model.predict_proba(x[test])[:,1]
    cm=confusion_matrix(y[test],pred,labels=[0,1])
    fig,ax=plt.subplots(figsize=(5.8,4.4))
    cmap=LinearSegmentedColormap.from_list('credence',['#fff8e6','#f2a900','#4c2800'])
    ax.imshow(cm,cmap=cmap,vmin=0,vmax=max(1,cm.max()))
    for row in range(2):
        for col in range(2): ax.text(col,row,str(cm[row,col]),ha='center',va='center',fontsize=27,fontweight='medium',color=paper if cm[row,col]>cm.max()/2 else ink)
    ax.set_xticks([0,1],['Authentic / transformed','Tampered'],fontsize=9)
    ax.set_yticks([0,1],['Authentic /\ntransformed','Tampered'],fontsize=9)
    ax.set_xlabel('Predicted class',labelpad=14); ax.set_ylabel('Actual class',labelpad=12)
    ax.tick_params(length=0,pad=10)
    for spine in ax.spines.values(): spine.set_visible(False)
    fig.tight_layout(pad=1.4);fig.savefig(out/'confusion_matrix.png',dpi=160);plt.close(fig)
    fpr,tpr,_=roc_curve(y[test],prob)
    fig,ax=plt.subplots(figsize=(5.8,4.4))
    ax.plot(fpr,tpr,color=orange,lw=2.5,label=f'ROC-AUC = {roc_auc_score(y[test],prob):.2f}')
    ax.fill_between(fpr,tpr,alpha=.12,color=gold)
    ax.plot([0,1],[0,1],color='#d2bea0',lw=1,linestyle='--',label='Chance')
    ax.set(xlim=(-.025,1.025),ylim=(-.025,1.025),xlabel='False positive rate',ylabel='True positive rate')
    ax.grid(alpha=.35,color='#e8decd',lw=.5);ax.legend(loc='lower right',frameon=False,fontsize=9)
    fig.tight_layout(pad=1.4);fig.savefig(out/'roc_curve.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,5,figsize=(16,3.4))
    for i,ax in enumerate(axes):
        for label,color in [(0,gold),(1,ink)]: ax.hist(x[y==label,i],bins=15,alpha=.72,label=['Authentic','Tampered'][label],color=color)
        ax.set_title(['Global similarity','Average patch','Minimum patch','SSIM','Pixel difference'][i],fontsize=10,pad=14,color=ink)
        ax.tick_params(labelsize=8);ax.grid(axis='y',alpha=.2,color='#e8decd')
    axes[0].legend(fontsize=8,frameon=False);fig.tight_layout(pad=1.6);fig.savefig(out/'feature_distributions.png',dpi=150);plt.close(fig)

if __name__=='__main__':
    rows=json.loads((ROOT/'results/dataset.json').read_text())
    x=np.array([r['features'] for r in rows]);y=np.array([r['label'] for r in rows]);groups=np.array([r['base'] for r in rows])
    test=np.isin(groups,np.random.default_rng(42).permutation(36)[30:])
    save_plots(x,y,test,joblib.load(ROOT/'models/tamper_classifier.joblib'),ROOT/'results')
