.PHONY: help restart push

help: ## Показать список команд
	@echo ""
	@echo "  make restart              Stop, rebuild and start all services"
	@echo "  make push MSG=\"message\"   git add + commit + push"
	@echo ""
	@echo "  Windows: .\\make restart"
	@echo ""

restart: ## Пересобрать и перезапустить стек
	docker compose down
	docker compose up -d --build

MSG ?= update

push: ## git add + commit + push; пример: make push MSG="chore: ..."
	git add .
	@git diff --cached --quiet || git commit -m "$(MSG)"
	git push -u origin HEAD
