.PHONY: build run stop logs dev dev-backend dev-frontend install

# ── Docker ───────────────────────────────────────────────
build:
	docker compose build

run:
	docker compose up -d

stop:
	docker compose down

logs:
	docker compose logs -f app

# ── Local development ────────────────────────────────────
install:
	pip install -r requirements.txt -r backend/requirements.txt
	cd frontend && npm install

dev:
	./run_app.sh

dev-backend:
	cd backend && python3 -m uvicorn main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev
