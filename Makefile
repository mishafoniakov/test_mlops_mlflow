.DEFAULT_GOAL := up

.PHONY: help up down restart restart_prune env push

help:
	@echo ""
	@echo "  make                 -- Create .env if missing, build and start all services"
	@echo "  make down            -- Stop and remove containers"
	@echo "  make restart         -- Stop, rebuild and start all services"
	@echo "  make restart_prune   -- Stop, prune, rebuild and start all services"
	@echo "  make push MSG=\"message\" -- git add + commit + push"
	@echo ""

env:
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env from .env.example"; fi

up: env
	docker compose up -d --build

down:
	docker compose down

restart: env
	docker compose down
	docker compose up -d --build

restart_prune: env
	docker compose down
	docker system prune -af
	docker compose up -d --build

MSG ?= update

push:
	git add .
	@git diff --cached --quiet || git commit -m "$(MSG)"
	git push -u origin HEAD
