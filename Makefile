.PHONY: restart push

restart:
	docker compose down
	docker compose up -d --build

MSG ?= update

push:
	git add .
	git commit -m "$(MSG)"
	git push origin HEAD
