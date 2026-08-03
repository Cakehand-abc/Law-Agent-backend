def test_read_root(client):
    """
    Test the root endpoint / of the FastAPI application.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to LawShield API" in response.json()["message"]
