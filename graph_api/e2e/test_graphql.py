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
            add(input: {description: "test", name: "test"}) {
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
    unit_id = int(data["unit"]["add"]["id"])
    assert data == {
        "unit": {"add": {"id": unit_id, "name": "test", "description": "test"}}
    }

    update_mutation = """
    mutation UpdateUnit {{
        unit {{
            update(input: {{
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
            "update": {
                "id": unit_id,
                "name": "updated test",
                "description": "updated description",
            }
        }
    }

    delete_mutation = """
    mutation DeleteUnit {{
        unit {{
            delete(input: {{
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
            "delete": {
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

    update_document_mutation = """
    mutation UpdateDocument {{
        document {{
            updateDocument(input: {{
                id: {document_id}}},
                name: "document_name",
                content: {{ "co2": "10 ton"}},
                description: "document_description"
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
        document_id=document_id
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
                "name": "test",
                "description": None,
                "content": {},
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
                "name": "test",
                "description": None,
                "content": {},
            }
        }
    }

    # update_unit_mutation = """
    # mutation UpdateUnit {{
    #     unit {{
    #         update(input: {{
    #             id: {unit_id},
    #             name: "updated test",
    #             description: "updated description"
    #         }}) {{
    #             id,
    #             name,
    #             description
    #         }}
    #     }}
    # }}
    # """.format(
    #     unit_id=unit_id
    # )

    # response = client.post(
    #     url="/v1/graphql",
    #     json={"query": update_unit_mutation},
    # )
    # assert response.status_code == status.HTTP_200_OK

    # data = response.json()["data"]
    # assert data == {
    #     "unit": {
    #         "update": {
    #             "id": unit_id,
    #             "name": "updated test",
    #             "description": "updated description",
    #         }
    #     }
    # }

    # delete_unit_mutation = """
    # mutation DeleteUnit {{
    #     unit {{
    #         delete(input: {{
    #             id: {unit_id}
    #         }}) {{
    #             id,
    #             name,
    #             description
    #         }}
    #     }}
    # }}
    # """.format(
    #     unit_id=unit_id
    # )

    # response = client.post(
    #     url="/v1/graphql",
    #     json={"query": delete_unit_mutation},
    # )
    # assert response.status_code == status.HTTP_200_OK

    # data = response.json()["data"]
    # assert data == {
    #     "unit": {
    #         "delete": {
    #             "id": unit_id,
    #             "name": "updated test",
    #             "description": "updated description",
    #         }
    #     }
    # }
