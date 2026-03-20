import click
from click.testing import CliRunner
import sys
import os

# Add the root directory to sys.path to allow importing from the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import cli

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output

def test_cli_query_with_args():
    runner = CliRunner()
    # Test with multiple query arguments
    with patch('main.APIClient') as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'
        mock_instance.get.return_value = mock_response
        
        result = runner.invoke(cli, ['query', '--param', 'key1=value1', '--param', 'key2=value2'])
        assert result.exit_code == 0
        assert "Querying https://api.example.com/endpoint with arguments: {'key1': 'value1', 'key2': 'value2'}" in result.output

from unittest.mock import patch, MagicMock

def test_cli_query_with_auth_token():
    runner = CliRunner()
    with patch('main.APIClient') as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"auth": "ok"}'
        mock_instance.get.return_value = mock_response
        
        result = runner.invoke(cli, ['query', '--auth-token', 'secret_token'])
        
        assert result.exit_code == 0
        mock_instance.get.assert_called_once()
        args, kwargs = mock_instance.get.call_args
        assert kwargs['headers']['Authorization'] == 'Bearer secret_token'
        assert 'API Response [200]: {"auth": "ok"}' in result.output

def test_cli_query_with_api_key():
    runner = CliRunner()
    with patch('main.APIClient') as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"auth": "ok"}'
        mock_instance.get.return_value = mock_response
        
        result = runner.invoke(cli, ['query', '--api-key', 'my_key'])
        
        assert result.exit_code == 0
        mock_instance.get.assert_called_once()
        args, kwargs = mock_instance.get.call_args
        assert kwargs['headers']['X-API-Key'] == 'my_key'
