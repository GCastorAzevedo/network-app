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
