.PHONY: migrate migrations dry.migrations

migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations

dry.migrations:
	python manage.py makemigrations --dry-run --verbosity 3