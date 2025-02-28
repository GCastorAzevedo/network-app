echo "Upgrading Graph database to Alembic's head"
python -m alembic -c graph_db/alembic.ini upgrade head
