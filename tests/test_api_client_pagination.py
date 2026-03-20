import requests
import requests_mock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_client import APIClient

def test_api_client_pagination_params():
    with requests_mock.Mocker() as m:
        # Mocking the call with pagination parameters
        m.get('https://data.sfgov.org/resource/wv5m-vpq2.json?%24query=SELECT+%2A+LIMIT+50+OFFSET+10', status_code=200)
        
        client = APIClient()
        client.get(params={'$query': 'SELECT * LIMIT 50 OFFSET 10'})
        
        assert m.called
        assert m.request_history[0].url == 'https://data.sfgov.org/resource/wv5m-vpq2.json?%24query=SELECT+%2A+LIMIT+50+OFFSET+10'
