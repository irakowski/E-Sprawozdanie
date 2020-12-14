import pytest
from django.urls import reverse

def test_landing_page_response(client):
    """
    Confirms the landing page returns 200 OK upon access
    """
    response = client.get(reverse("landing-page"))
    assert response.status_code == 200