
.PHONY: run
run:
	@export DATABASE_URI="postgresql://postgres:postgres@localhost:5432/postgres" && \
	fastapi run main.py --host 0.0.0.0 --port 80 --reload

.PHONY: build
build:
	@ docker build -t supply_chain_api -f ./Dockerfile ..

.PHONY: run-docker
run-docker:
	@ docker run --rm \
		-e DATABASE_URI="postgresql://postgres:postgres@localhost:5432/postgres" \
		-p 8964:80 \
		supply_chain_api \
		fastapi run supply_chain_api/main.py --host 0.0.0.0 --port 80 --reload

.PHONY: test
test:
	@ pwd && cd .. && pwd && ls
	@ pwd
