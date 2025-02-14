from neomodel import config, db

config.DATABASE_URL = "bolt://neo4j:neo4jpass@localhost:7687"

results, meta = db.cypher_query("RETURN 'Hello World' as message")
print(results, meta)
