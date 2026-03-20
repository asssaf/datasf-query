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

def test_api_get_request_with_auth():
    with requests_mock.Mocker() as m:
        m.get('https://api.example.com/auth', json={'authenticated': True}, status_code=200)
        
        headers = {'Authorization': 'Bearer test_token'}
        client = APIClient(base_url='https://api.example.com')
        response = client.get('/auth', headers=headers)
        
        assert response.status_code == 200
        assert m.request_history[0].headers['Authorization'] == 'Bearer test_token'
