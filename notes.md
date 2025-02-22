### System Requirements

* Store a graph modelling supply chains
    * Nodes can have access to data from all suppliers at lower levels in the tree.
    * A Node can be a supplier of the node above in the tree
    * Two companies can supply each other (is there a constraint that they can't supply the same "thing")
    * The relation is of the form "Company A supplies product B to company C".
    * Companies have data associated to it, such as "electricity consumption", "Number of cars produced", "Product P", etc
    * Suppliers can have a relationship with multiple parent nodes.
* Queries can answer questions such as:
    * "What is the total emission of CO2 throughout the supply chain of company A?"
    * "How many tons of tea is bought from my supply chain?"
    * "How is the value distributed along the different levels of my supply chain?"
    * "What are the byproducts of the production of my trousers?"
    * "What is the total energy spent thrughout my supply chain? Which percentage is wind?"
    * "Which other suppliers can provide similar/exact products to replace supplier A, but with a lower footprint?"
* Companies can be added to the system voluntarily, pushed by its contractors above in the chain, added by the team or partners.
* Target use case: a company wants to seamlessly track its supplies and measure things like value, emission etc. They push all their suppliers to add relevant information to the system. A supplier can participate in many supply chains.
* Suppliers can provide product information, metadata, and its own data.
* Allow vector search for procurement

# Technology

* Ideas:
    * Neo4j + Elasticsearch
    * Postgres with db vector and apache age extensions
    * Mongodb (atlas)

# Relevant Resources

* https://tembo.io/blog/image-search
* https://www.kaggle.com/datasets/spypsc07/amazon-products?resource=download
* https://www.timescale.com/blog/how-to-build-an-image-search-application-with-openai-clip-postgresql-in-javascript
* https://openai.com/index/clip/
* https://www.timescale.com/blog/postgresql-as-a-vector-database-create-store-and-query-openai-embeddings-with-pgvector
* https://stackoverflow.com/questions/51025607/prevent-infinite-loop-in-recursive-query-in-postgresql
* https://blog.mergify.com/cycle-detection-in-postgresql/
* https://www.elastic.co/elasticsearch/graph
* https://age.apache.org/
* https://medium.com/percolation-labs/cloudnativepg-age-and-pg-vector-on-a-docker-image-step-1-ef0156c78f49
* GRAPHQL:
    * https://medium.com/simform-engineering/building-a-graphql-api-with-fastapi-and-strawberry-an-exciting-adventure-with-test-driven-aa7ed509f218
* Kafka connector:
    * https://hub.docker.com/r/apache/kafka
    * https://docs.confluent.io/platform/current/connect/userguide.html#configuring-workers
    * https://docs.confluent.io/platform/current/installation/docker/config-reference.html#kconnect-long-configuration
    * https://docs.confluent.io/platform/current/installation/configuration/connect/index.html#kconnect-long-configuration-reference-for-cp
    * https://kafka.apache.org/documentation/#connectconfigs
