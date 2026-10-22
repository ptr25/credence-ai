import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
export default (phase)=>({outputFileTracingRoot:root,async rewrites(){const backend=process.env.BACKEND_URL||'http://127.0.0.1:8000';return ['api','storage','results'].map(route=>({source:`/${route}/:path*`,destination:`${backend}/${route}/:path*`}));},distDir:phase==='phase-development-server'?'.next-dev':'.next'});
