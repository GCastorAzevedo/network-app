# Makefile to export Alembic environment variables

.PHONY: export
export:
ifeq ($(OS),Windows_NT)  # Windows (cmd or PowerShell)
	@echo "Exporting environment variables on Windows..."
	set ALEMBIC_USERNAME=postgres
	set ALEMBIC_PASSWORD=postgres
	set DATABASE_NAME=postgres
else  # Linux/macOS
	@echo "Exporting environment variables on Unix-like OS..."
	export ALEMBIC_USERNAME=postgres
	export ALEMBIC_PASSWORD=postgres
	export DATABASE_NAME=postgres
endif


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
