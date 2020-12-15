import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import pathlib

def test_landing_page_response(client):
    """
    Confirms the landing page returns 200 OK upon access
    """
    response = client.get(reverse('landing-page'))
    assert response.status_code == 200


def test_landing_page_content(client):
    """
    Confirms view to return correct content 
    """
    response = client.get(reverse('landing-page'))
    assert b'Inny Podmiot' in response.content


def test_upload_view(client):
    """
    Confirms response for accessing form upload returns OK status
    """
    response = client.get(reverse('esfviewer:upload'))
    assert response.status_code == 200


def test_upload_view_content(client):
    """
    Confirms form in the the content of the response
    """
    response = client.get(reverse('esfviewer:upload'))
    assert b'form' in response.content
    assert b'Upload Xml' in response.content


def test_upload_form_success(client):
    """
    """
    #list_of_test_files = [str(p) for p in pathlib.Path('ESFViewer/pytests/file_cases').iterdir() if p.is_file()]
    url = reverse('esfviewer:report')
    file = "ESFViewer/pytests/file_cases/case1.xml"

    upload = SimpleUploadedFile(name='file_cases/case1.xml', 
                                content=open("ESFViewer/pytests/file_cases/case1.xml", 'rb').read(), 
                                content_type='text/xml')
    response = client.post(url, data={'file': upload })
    assert response.status_code == 200
    assert b'Raport' in response.content
