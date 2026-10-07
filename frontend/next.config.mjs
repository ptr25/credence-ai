import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
export default (phase)=>({outputFileTracingRoot:root,distDir:phase==='phase-development-server'?'.next-dev':'.next'});
