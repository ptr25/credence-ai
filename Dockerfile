FROM node:22-bookworm-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim-bookworm
COPY --from=frontend /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend /app/frontend /app/frontend
WORKDIR /app
COPY requirements.lock.txt ./
RUN pip install --no-cache-dir torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cpu && pip install --no-cache-dir -r requirements.lock.txt
COPY backend/ backend/
ENV PYTHONPATH=/app/backend TORCH_HOME=/app/weights MALLOC_ARENA_MAX=2 MALLOC_TRIM_THRESHOLD_=131072
RUN python -c "from app.services.vision_service import engine; engine()"
COPY scripts/serve.py scripts/serve.py
CMD ["python", "scripts/serve.py"]
