import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.ai.dataset import generate
Path('backend/app/results/dataset.json').write_text(json.dumps(generate()))
