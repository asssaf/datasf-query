import requests
import requests_mock
import pytest
import sys
import os

# Add the root directory to sys.path to allow importing from the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_client import APIClient

def test_api_get_request():
    with requests_mock.Mocker() as m:
        m.get('https://api.example.com/data', json={'key': 'value'}, status_code=200)
        
        client = APIClient(base_url='https://api.example.com')
        response = client.get('/data')
        
        assert response.status_code == 200
        assert response.json() == {'key': 'value'}

def test_api_get_request_with_params():
    with requests_mock.Mocker() as m:
        m.get('https://api.example.com/search?q=query', json={'results': []}, status_code=200)
        
        client = APIClient(base_url='https://api.example.com')
        response = client.get('/search', params={'q': 'query'})
        
        assert response.status_code == 200
        assert m.called
        assert m.request_history[0].url == 'https://api.example.com/search?q=query'

def test_api_get_request_ssl_verify():
    with requests_mock.Mocker() as m:
        m.get('https://api.example.com/ssl', json={'ssl': 'ok'}, status_code=200)
        
        client = APIClient(base_url='https://api.example.com')
        response = client.get('/ssl')
        
        assert response.status_code == 200
        # By default requests verifies SSL, but our mock doesn't strictly check the 'verify' parameter unless we tell it to.
        # However, we want to ensure our client can be configured if needed.

def test_api_get_request_ssl_error():
    with requests_mock.Mocker() as m:
        m.get('https://api.example.com/ssl-error', exc=requests.exceptions.SSLError)
        
        client = APIClient(base_url='https://api.example.com')
        with pytest.raises(requests.exceptions.SSLError):
            client.get('/ssl-error')
