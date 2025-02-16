
.PHONY: run
run:
	@export DATABASE_URI="postgresql://postgres:postgres@localhost:5432/postgres" && \
	fastapi run main.py --host 0.0.0.0 --port 80 --reload
