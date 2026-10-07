import type {ReactNode} from 'react';

export function Icon({name='shield',size=20,className=''}:{name?:string;size?:number;className?:string}) {
  const paths:Record<string,ReactNode>={
    shield:<><path d="M12 3 4 6v6c0 5 8 9 8 9s8-4 8-9V6l-8-3Z"/><path d="m8.5 12 2.3 2.3 4.7-4.8"/></>,
    grid:<><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></>,
    plus:<><path d="M12 5v14M5 12h14"/></>,
    certificate:<><path d="M14 21H5V3h14v10M8 7h8M8 11h5"/><circle cx="17" cy="16" r="3"/><path d="m15 18-1 4 3-1 3 1-1-4"/></>,
    scan:<><path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5M2 12h20"/><path d="M8 7h8M8 17h8"/></>,
    spark:<><path d="m12 3 2.6 6.4L21 12l-6.4 2.6L12 21l-2.6-6.4L3 12l6.4-2.6L12 3Z"/></>,
    history:<><path d="M3 11a9 9 0 1 1 2 7M3 4v7h7"/><path d="M12 7v5l3 2"/></>,
    chart:<><path d="M4 3v17h17M8 16v-5m5 5V7m5 9V4"/></>,
    book:<><path d="M12 5v16M3 3h5a4 4 0 0 1 4 2 4 4 0 0 1 4-2h5v16h-5a4 4 0 0 0-4 2 4 4 0 0 0-4-2H3V3Z"/></>,
    settings:<><path d="m9 3-1 3-3 1 1 3-2 2 2 2-1 3 3 1 1 3h6l1-3 3-1-1-3 2-2-2-2 1-3-3-1-1-3H9Z"/><circle cx="12" cy="12" r="3"/></>,
    arrow:<path d="M5 12h14m-6-6 6 6-6 6"/>,
    up:<path d="M6 18 18 6M6 6h12v12"/>,
    chevron:<path d="m9 5 7 7-7 7"/>,
    upload:<><path d="M12 16V3m-5 5 5-5 5 5M4 15v6h16v-6"/></>,
    download:<><path d="M12 3v13m-5-5 5 5 5-5M4 17v4h16v-4"/></>,
    check:<path d="m5 12 4 4L19 6"/>,
    alert:<><path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v5m0 3v1"/></>,
    lock:<><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 5v2"/></>,
    search:<><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></>,
    file:<><path d="M14 3H5v18h14V8l-5-5Z"/><path d="M14 3v5h5M8 13h8M8 17h5"/></>,
    close:<path d="m6 6 12 12M6 18 18 6"/>,
    menu:<path d="M4 6h16M4 12h16M4 18h16"/>,
    logout:<><path d="M9 3H4v18h5M9 12h12m-5-5 5 5-5 5"/></>,
    globe:<><circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/></>,
  };
  return <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]||paths.shield}</svg>;
}
export const percent=(n:number|undefined)=>n==null?'—':`${(n*100).toFixed(2)}%`;
export function Badge({value}:{value:string}) {
  const labels:Record<string,string>={VERIFIED:'Verified',TRANSFORMED_COPY:'Transformed copy',TAMPERING_SUSPECTED:'Tampering suspected',REVOKED:'Revoked',NOT_FOUND:'Not found',REVIEW_RECOMMENDED:'Review recommended',ACTIVE:'Active'};
  const tone=['REVOKED','TAMPERING_SUSPECTED'].includes(value)?'danger':['REVIEW_RECOMMENDED','NOT_FOUND'].includes(value)?'neutral':'good';
  return <span className={`badge ${tone}`}><span className="status-dot"/>{labels[value]||value}</span>;
}
export function PageHeading({eyebrow,title,description,action}:{eyebrow?:string;title:string;description:string;action?:ReactNode}) {
  return <div className="page-heading"><div>{eyebrow&&<div className="eyebrow">{eyebrow}</div>}<h1>{title}</h1><p>{description}</p></div>{action}</div>;
}
export function EmptyState({title,description}:{title:string;description:string}) {
  return <div className="empty-state"><span className="icon-tile"><Icon name="file" size={25}/></span><h3>{title}</h3><p>{description}</p></div>;
}
export function DocumentArt(){return <div className="document-art" aria-hidden="true"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="floating-label"><span className="status-dot"/>Neural fingerprint</div><div className="art-document"><div className="art-doc-top"><span className="mini-brand">C</span><span>CREDENCE AI<br/><i>VERIFIED CREDENTIAL</i></span></div><div className="doc-rule"/><div className="art-doc-title">Certificate of<br/><em>Achievement</em></div><div className="doc-line long"/><div className="doc-line"/><div className="doc-line short"/><div className="art-doc-bottom"><span className="seal"><Icon size={30}/></span><div className="art-qr">▦</div></div><div className="scan-line"/></div><div className="floating-check"><Icon name="check" size={22}/></div></div>}
export function Analysis({result,api}:{result:any;api:string}) {
  if(!result)return null;
  return <section className="card analysis-card" aria-live="polite"><div className="section-heading"><div><div className="eyebrow">CREDENCE VISION ANALYSIS</div><h2>Your verification results</h2></div><Badge value={result.result}/></div>
    <p>{result.result==='TRANSFORMED_COPY'?'The file has changed at byte level. Its visual content is consistent with the registered credential.':result.message||'Deep visual comparison against the registered authentic certificate.'}</p>
    {result.revocationReason&&<div className="notice danger-notice">Revoked: {result.revocationReason}</div>}
    {result.globalSimilarity!=null&&<><div className="prediction-strip"><span className="icon-tile"><Icon name={result.modelPrediction==='TAMPERED'?'alert':'shield'}/></span><div><small>Model prediction</small><strong>{result.modelPrediction==='TAMPERED'?'Tampering detected':'Authentic or transformed'}</strong></div><div className="confidence"><strong>{percent(result.modelConfidence)}</strong><small>Classifier confidence</small></div></div>
    <div className="similarities">{[['Global similarity',result.globalSimilarity],['Average patch',result.averagePatchSimilarity],['Minimum patch',result.minimumPatchSimilarity],['Structural similarity',result.structuralSimilarity]].map(([label,value]:any)=><div key={label}><small>{label}</small><strong>{percent(value)}</strong><div className="meter"><span style={{width:percent(value)}}/></div></div>)}</div>
    <div className="integrity-row"><span><Icon name="lock" size={16}/>SHA-256 <b>{result.hashMatch?'Match':'Different'}</b></span><span><Icon name="shield" size={16}/>CredenceID <b>{result.credenceIdStatus.toLowerCase()}</b></span></div>
    <div className="analysis-detail"><div><div className="eyebrow">REGION BY REGION</div><h3>Neural patch comparison</h3><p>Nine regions. A closer look at every detail.</p><div className="patches">{result.patchSimilarities.map((v:number,i:number)=><div className={i+1===result.mostAnomalousPatch?'anomalous':''} key={i}><small>0{i+1}</small><strong>{percent(v)}</strong></div>)}</div><small>Most anomalous region: patch {result.mostAnomalousPatch}<br/>Mean pixel difference: {result.pixelDifference.toFixed(5)}</small></div><div><div className="eyebrow">VISUAL DIFFERENCE MAP</div><h3>See what changed</h3><p>Highlighted areas show differences from the reference.</p><a href={api+result.heatmapPath} target="_blank" rel="noreferrer"><img className="difference-image" src={api+result.heatmapPath} alt="Visual difference overlay highlighting changed certificate regions"/></a></div></div>
    {result.downloadUrl&&<a className="button secondary" href={api+result.downloadUrl} target="_blank" rel="noreferrer"><Icon name="download" size={17}/>Download demo copy</a>}</>}
  </section>
}
