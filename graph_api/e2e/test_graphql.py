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


def test_main():
    query = """
    query {
        units { id }
    }
    """
    response = client.post(
        url="/v1/graphql",
        json={"query": query},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"] == {"units": []}


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
