
.PHONY: post-graph-db-conenctor
post-graph-db-connector:
	@curl -i -X POST -H "Accept:application/json" \
  		-H "Content-Type:application/json" localhost:8083/connectors/ \
  		-d @graph_db_connector.json

.PHONY: post-elasticsearch-sink
post-elasticsearch-sink:
	@curl -i -X POST -H "Accept:application/json" \
  		-H "Content-Type:application/json" localhost:8084/connectors/ \
  		-d @elasticsearch_sink.json
