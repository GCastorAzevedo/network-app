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
