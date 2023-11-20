import pytest
import requests


@pytest.mark.django_db
def test_get_products(request_client):
    response = requests.get("http://127.0.0.1:8080/api/v1/list/")

    assert response.status_code == 200
