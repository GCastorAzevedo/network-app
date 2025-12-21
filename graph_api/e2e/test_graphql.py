from fastapi.testclient import TestClient
from fastapi import status
from graph_api.main import app

client = TestClient(
    app,
    base_url="http://testserver",
    raise_server_exceptions=True,
    root_path="",
    backend="asyncio",
    backend_options=None,
    cookies=None,
    headers=None,
    follow_redirects=True,
    client=("testclient", 50000),
)


def test_add_and_delete_unit():
    add_mutation = """
    mutation CreateUnit {
        unit {
            addUnit(input: {description: "test", name: "test"}) {
                id,
                name,
                description
            }
        }
    }
    """

    response = client.post(
        url="/v1/graphql",
        json={"query": add_mutation},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    unit_id = int(data["unit"]["addUnit"]["id"])
    assert data == {
        "unit": {"addUnit": {"id": unit_id, "name": "test", "description": "test"}}
    }

    update_mutation = """
    mutation UpdateUnit {{
        unit {{
            updateUnit(input: {{
                id: {unit_id},
                name: "updated test",
                description: "updated description"
            }}) {{
                id,
                name,
                description
            }}
        }}
    }}
    """.format(
        unit_id=unit_id
    )

    response = client.post(
        url="/v1/graphql",
        json={"query": update_mutation},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    assert data == {
        "unit": {
            "updateUnit": {
                "id": unit_id,
                "name": "updated test",
                "description": "updated description",
            }
        }
    }

    delete_mutation = """
    mutation DeleteUnit {{
        unit {{
            deleteUnit(input: {{
                id: {unit_id}
            }}) {{
                id,
                name,
                description
            }}
        }}
    }}
    """.format(
        unit_id=unit_id
    )

    response = client.post(
        url="/v1/graphql",
        json={"query": delete_mutation},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    assert data == {
        "unit": {
            "deleteUnit": {
                "id": unit_id,
                "name": "updated test",
                "description": "updated description",
            }
        }
    }


def test_add_and_delete_unit_with_documents():
    add_unit_mutation = """
    mutation CreateUnit {
        unit {
            addUnit(input: {description: "test", name: "test"}) {
                id,
                name,
                description
            }
        }
    }
    """

    response = client.post(
        url="/v1/graphql",
        json={"query": add_unit_mutation},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    unit_id = int(data["unit"]["addUnit"]["id"])
    assert data == {
        "unit": {"addUnit": {"id": unit_id, "name": "test", "description": "test"}}
    }

    get_unit_query = """
    query GetUnit($id: Int = {unit_id}) {{
        unit(id: $id) {{
            id
            name
            description
        }}
    }}
    """.format(
        unit_id=unit_id
    )

    response = client.post(
        url="/v1/graphql",
        json={"query": get_unit_query},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    unit_id = int(data["unit"]["id"])
    assert data == {"unit": {"id": unit_id, "name": "test", "description": "test"}}

    add_document_mutation = """
    mutation CreateDocument {{
        document {{
            addDocument(input: {{unitId: {unit_id}, name: "test"}}) {{
                id
                unitId
                name
                content
                description
            }}
        }}
    }}
    """.format(
        unit_id=unit_id
    )
    response = client.post(
        url="/v1/graphql",
        json={"query": add_document_mutation},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    document_id = int(data["document"]["addDocument"]["id"])
    assert data == {
        "document": {
            "addDocument": {
                "id": document_id,
                "unitId": unit_id,
                "name": "test",
                "description": None,
                "content": {},
            }
        }
    }

    get_document_query = """
    query GetDocument($id: Int = {document_id}) {{
        document(id: $id) {{
            id
            unitId
            name
            content
            description
        }}
    }}
    """.format(
        document_id=document_id
    )

    response = client.post(
        url="/v1/graphql",
        json={"query": get_document_query},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    assert data == {
        "document": {
            "id": document_id,
            "unitId": unit_id,
            "name": "test",
            "description": None,
            "content": {},
        }
    }

    update_document_mutation = """
    mutation UpdateDocument {{
        document {{
            updateDocument(
                input: {{
                    id: {document_id},
                    content: "{{\\\"co2\\\": \\\"10 ton\\\"}}",
                    description: "document_description",
                    name: "document_name"
                }}
            ) {{
                id
                unitId
                name
                content
                description
            }}
        }}
    }}
    """.format(
        document_id=document_id,
    )
    response = client.post(
        url="/v1/graphql",
        json={"query": update_document_mutation},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    document_id = int(data["document"]["updateDocument"]["id"])
    assert data == {
        "document": {
            "updateDocument": {
                "id": document_id,
                "unitId": unit_id,
                "name": "document_name",
                "description": "document_description",
                "content": {"co2": "10 ton"},
            }
        }
    }

    delete_document_mutation = """
    mutation DeleteDocument {{
        document {{
            deleteDocument(input: {{id: {document_id}}}) {{
                id
                unitId
                name
                content
                description
            }}
        }}
    }}
    """.format(
        document_id=document_id
    )
    response = client.post(
        url="/v1/graphql",
        json={"query": delete_document_mutation},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    document_id = int(data["document"]["deleteDocument"]["id"])
    assert data == {
        "document": {
            "deleteDocument": {
                "id": document_id,
                "unitId": unit_id,
                "name": "document_name",
                "description": "document_description",
                "content": {"co2": "10 ton"},
            }
        }
    }

    delete_unit_mutation = """
    mutation DeleteUnit {{
        unit {{
            deleteUnit(input: {{
                id: {unit_id}
            }}) {{
                id,
                name,
                description
            }}
        }}
    }}
    """.format(
        unit_id=unit_id
    )

    response = client.post(
        url="/v1/graphql",
        json={"query": delete_unit_mutation},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    assert data == {
        "unit": {
            "deleteUnit": {
                "id": unit_id,
                "name": "test",
                "description": "test",
            }
        }
    }


def test_add_units_connected_by_edge():
    add_units_mutation = """
    mutation CreateUnit {
        n1: unit {
            addUnit(input: {description: "test", name: "test"}) {
                id, name, description
            }
        },
        n2: unit {
            addUnit(input: {description: "test", name: "test"}) {
                id, name, description
            }
        },
        n3: unit {
            addUnit(input: {description: "test", name: "test"}) {
                id, name, description
            }
        },
        n4: unit {
            addUnit(input: {description: "test", name: "test"}) {
                id, name, description
            }
        },
        n5: unit {
            addUnit(input: {description: "test", name: "test"}) {
                id, name, description
            }
        }
    }
    """
    response = client.post(url="/v1/graphql", json={"query": add_units_mutation})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    assert sorted(data.keys()) == ["n1", "n2", "n3", "n4", "n5"]
    unit_ids = [
        int(data[node]["addUnit"]["id"]) for node in ["n1", "n2", "n3", "n4", "n5"]
    ]

    add_edges_mutation = """
    mutation CreateEdges {{
        e1: edge {{
            addEdge(input: {{targetUnitId: {u2}, sourceUnitId: {u1}}}) {{
                sourceUnitId, targetUnitId
            }}
        }},
        e2: edge {{
            addEdge(input: {{targetUnitId: {u3}, sourceUnitId: {u2}}}) {{
                sourceUnitId, targetUnitId
            }}
        }},
        e3: edge {{
            addEdge(input: {{targetUnitId: {u4}, sourceUnitId: {u3}}}) {{
                sourceUnitId, targetUnitId
            }}
        }},
        e4: edge {{
            addEdge(input: {{targetUnitId: {u2}, sourceUnitId: {u4}}}) {{
                sourceUnitId, targetUnitId
            }}
        }},
        e5: edge {{
            addEdge(input: {{targetUnitId: {u2}, sourceUnitId: {u5}}}) {{
                sourceUnitId, targetUnitId
            }}
        }}
    }}
    """.format(
        u1=unit_ids[0],
        u2=unit_ids[1],
        u3=unit_ids[2],
        u4=unit_ids[3],
        u5=unit_ids[4],
    )

    response = client.post(url="/v1/graphql", json={"query": add_edges_mutation})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    assert data == {
        "e1": {"addEdge": {"sourceUnitId": unit_ids[0], "targetUnitId": unit_ids[1]}},
        "e2": {"addEdge": {"sourceUnitId": unit_ids[1], "targetUnitId": unit_ids[2]}},
        "e3": {"addEdge": {"sourceUnitId": unit_ids[2], "targetUnitId": unit_ids[3]}},
        "e4": {"addEdge": {"sourceUnitId": unit_ids[3], "targetUnitId": unit_ids[1]}},
        "e5": {"addEdge": {"sourceUnitId": unit_ids[4], "targetUnitId": unit_ids[1]}},
    }

    get_units_query = """
    query MyQuery {{
        u1: unit(id: {u1}) {{
            descendants
            ancestors
        }},
        u2: unit(id: {u2}) {{
            descendants
            ancestors
        }},
        u3: unit(id: {u3}) {{
            descendants
            ancestors
        }},
        u4: unit(id: {u4}) {{
            descendants
            ancestors
        }},
        u5: unit(id: {u5}) {{
            descendants
            ancestors
        }}
    }}
    """.format(
        u1=unit_ids[0],
        u2=unit_ids[1],
        u3=unit_ids[2],
        u4=unit_ids[3],
        u5=unit_ids[4],
    )

    response = client.post(
        url="/v1/graphql",
        json={"query": get_units_query},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    assert data == {
        "u1": {"descendants": unit_ids[1:-1], "ancestors": []},
        "u2": {"descendants": unit_ids[1:-1], "ancestors": unit_ids},
        "u3": {"descendants": unit_ids[3:4], "ancestors": unit_ids[:2]},
        "u4": {"descendants": unit_ids[1:-1], "ancestors": unit_ids},
        "u5": {"descendants": unit_ids[1:-1], "ancestors": []},
    }

    delete_units_mutation = """
    mutation DeleteUnits {{
        u1: unit {{ deleteUnit(input: {{ id: {u1} }}) {{ id }} }},
        u2: unit {{ deleteUnit(input: {{ id: {u2} }}) {{ id }} }},
        u3: unit {{ deleteUnit(input: {{ id: {u3} }}) {{ id }} }},
        u4: unit {{ deleteUnit(input: {{ id: {u4} }}) {{ id }} }},
        u5: unit {{ deleteUnit(input: {{ id: {u5} }}) {{ id }} }}
    }}
    """.format(
        u1=unit_ids[0],
        u2=unit_ids[1],
        u3=unit_ids[2],
        u4=unit_ids[3],
        u5=unit_ids[4],
    )

    response = client.post(
        url="/v1/graphql",
        json={"query": delete_units_mutation},
    )
    assert response.status_code == status.HTTP_200_OK

    # TODO: add edge by ID resolverrs, check the edges are gone
    get_edges_query = "query MyQuery { edges { sourceUnitId, targetUnitId } }"
    response = client.post(url="/v1/graphql", json={"query": get_edges_query})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]
    edges = [
        edge
        for edge in data["edges"]
        if (edge["sourceUnitId"] in unit_ids or edge["targetUnitId"] in unit_ids)
    ]
