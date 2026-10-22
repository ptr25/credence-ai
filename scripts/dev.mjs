import {spawn} from 'node:child_process';
import {existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
process.chdir(root);
const python=process.env.PYTHON_EXECUTABLE||'.venv/bin/python';
if(!existsSync(python)||!existsSync('frontend/node_modules')){
 console.error('Install dependencies first: python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.lock.txt; npm run setup:frontend');process.exit(1);
}
const children=[spawn(python,['-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000'],{stdio:'inherit',env:{...process.env,PYTHONPATH:'backend'}}),spawn('npm',['--prefix','frontend','run','dev'],{stdio:'inherit'})];
let stopping=false;
function stop(code=0){if(stopping)return;stopping=true;for(const child of children)child.kill('SIGTERM');process.exitCode=code;}
for(const child of children){child.on('error',e=>{console.error(e.message);stop(1)});child.on('exit',code=>stop(code??1));}
process.on('SIGINT',()=>stop());process.on('SIGTERM',()=>stop());
