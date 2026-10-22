# Run locally
From the project root, create a Python environment with `python3 -m venv .venv`, then run `.venv/bin/python -m pip install -r requirements.lock.txt` and `npm run setup:frontend` once. Run `npm run dev` to start both services. Open http://localhost:3000. Local demo login: admin@iiitk.ac.in / credence123.

# Render
Create a Blueprint from this repository. The Docker image contains the Next.js frontend, Python backend, classifier and downloaded ResNet18 weights. QR codes use the assigned Render HTTPS address automatically; PUBLIC_BASE_URL can override it. Use ADMIN_PASSWORD from Render's environment settings at login (the local demo password is not the hosted password).

The default blueprint selects free compute for evaluation, with no persistent storage. Uploaded certificates and registry data can disappear on restart. PyTorch memory requirements may exceed the free instance limit; successful deployment and inference must be checked before using it for a presentation. For durable use, choose an adequately sized paid instance and attach a disk at /data, then set STORAGE_DIR=/data/credence. Confirm any paid resources before provisioning them.

Container builds and remote deployment still require validation on the hosting platform. A healthy backend responds to /api/health; verify issuance and document verification after deployment.
