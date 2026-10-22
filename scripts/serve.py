"""Run the public frontend and internal inference server in one container."""
import os, signal, subprocess, sys, time
children = [
    subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000']),
    subprocess.Popen(['node', 'node_modules/next/dist/bin/next', 'start', '--hostname', '0.0.0.0', '--port', os.environ.get('PORT', '3000')], cwd='/app/frontend'),
]
def stop(*args):
    for child in children:
        child.terminate()
signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
try:
    while all(child.poll() is None for child in children):
        time.sleep(1)
finally:
    stop()
    for child in children:
        try: child.wait(timeout=10)
        except subprocess.TimeoutExpired: child.kill()
sys.exit(1)
