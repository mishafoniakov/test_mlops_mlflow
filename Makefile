.PHONY: help restart restart_prune push

help:
	@echo ""
	@echo "  make restart -- Stop, rebuild and start all services"
	@echo "  make restart_prune -- Stop, clean, rebuild and start all services"
	@echo "  make push MSG=\"message\" -- git add + commit + push"
	@echo ""
	@echo "  Windows: .\\make restart"
	@echo ""

restart:
	docker compose down
	docker compose up -d --build

restart_prune:
	docker compose down
	docker system prune -af
	docker compose up -d --build

MSG ?= update

push:
	git add .
	@git diff --cached --quiet || git commit -m "$(MSG)"
	git push -u origin HEAD
