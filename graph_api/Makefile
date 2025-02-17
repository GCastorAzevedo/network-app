
.PHONY: run
run:
	@export DATABASE_URI="postgresql://postgres:postgres@localhost:5432/postgres" && \
	fastapi run main.py --host 0.0.0.0 --port 80 --reload

.PHONY: build
build:
	@ docker build -t graph_api -f ./Dockerfile ..

.PHONY: run-docker
run-docker:
	@ docker run --rm \
		-e DATABASE_URI="postgresql://postgres:postgres@localhost:5432/postgres" \
		-p 8964:80 \
		--name whollygraph_api \
		graph_api \
		fastapi run graph_api/main.py --host 0.0.0.0 --port 80 --reload

.PHONY: test
test:
	@ pwd && cd .. && pwd && ls
	@ pwd
