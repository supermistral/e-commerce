DC = docker-compose -f docker-compose.yml -p e-commerce

API_SERVICE = ms-product


all: up

up:
	$(DC) up

up-build:
	$(DC) up --build

stop:
	$(DC) stop

makemigrations:
	$(DC) exec $(API_SERVICE) alembic revision --autogenerate -m "$(filter-out $@,$(MAKECMDGOALS))"

migrate:
	$(DC) exec $(API_SERVICE) alembic upgrade head

downgrade:
	$(DC) exec $(API_SERVICE) alembic downgrade "$(filter-out $@,$(MAKECMDGOALS))"

delete-db: stop
	$(DC) rm -v api-db

recreate-db: delete-db up
	sleep 8
	$(MAKE) makemigrations "init"
	$(MAKE) migrate
