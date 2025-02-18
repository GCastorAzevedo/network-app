# Makefile to export Alembic environment variables

export ALEMBIC_USERNAME=postgres
export ALEMBIC_PASSWORD=postgres
export DATABASE_NAME=postgres

.PHONY: export
export:
	@echo "Environment variables exported."

.PHONY: add_non_superuser_symlink
add_non_superuser_symlink:
# https://age.apache.org/age-manual/master/intro/setup.html
	@echo "Creating symbolic link for AGE extension..."
	@ln -sf /usr/lib/postgresql/16/lib/age.so /usr/lib/postgresql/16/lib/plugins/age.so
	@echo "Symbolic link created."

.PHONY: upgrade_alembic_from_graph_db
upgrade_alembic_from_graph_db:
	@echo "Upgrading Alembic..."
	@PYTHONPATH=../ alembic upgrade head
	@echo "Alembic upgraded."

.PHONY: run_alembic_from_root
run_alembic_from_root:
	@ PYTHONPATH=. alembic -c graph_db/alembic.ini current
