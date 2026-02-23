.PHONY: build run stop logs dev

build:
	docker compose build

run:
	docker compose up -d

stop:
	docker compose down

logs:
	docker compose logs -f app

dev:
	streamlit run dashboard/app_v2.py
