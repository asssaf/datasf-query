import click
from click.testing import CliRunner
import sys
import os
from unittest.mock import patch, MagicMock

# Add the root directory to sys.path to allow importing from the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import cli

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'SF Property Data CLI' in result.output

def test_cli_query_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['query', '--help'])
    assert result.exit_code == 0
    assert '--bedrooms' in result.output
    assert '--bathrooms' in result.output
    assert '--parcel-number' in result.output
    assert '--area-min' in result.output
    assert '--area-max' in result.output
    assert '--date-start' in result.output
    assert '--date-end' in result.output
    assert '--district' in result.output

def test_cli_query_sf_data():
    runner = CliRunner()
    with patch('main.APIClient') as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '[{"parcel_number": "1234"}]'
        mock_instance.get.return_value = mock_response
        
        result = runner.invoke(cli, [
            'query', 
            '--bedrooms', '2', 
            '--area-min', '500', 
            '--district', '9',
            '--parcel-number', '3776182',
            '--verbose'
        ])
        
        assert result.exit_code == 0
        assert 'Executing SoQL: SELECT' in result.output
        assert 'number_of_bedrooms IN ("2.0")' in result.output
        assert 'property_area >= 500' in result.output
        assert 'caseless_one_of(assessor_neighborhood_district, "9")' in result.output
        assert 'parcel_number = "3776182"' in result.output
        
        # Verify API call
        mock_instance.get.assert_called_once()
        args, kwargs = mock_instance.get.call_args
        assert '$query' in kwargs['params']
        assert 'SELECT' in kwargs['params']['$query']
        assert 'WHERE' in kwargs['params']['$query']

def test_cli_query_table_format():
    runner = CliRunner()
    with patch('main.APIClient') as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '[{"parcel_number": "1234", "area": "500"}]'
        mock_instance.get.return_value = mock_response
        
        result = runner.invoke(cli, ['query', '--format', 'table'])
        
        assert result.exit_code == 0
        assert 'parcel_number | area' in result.output
        assert '1234          | 500' in result.output

def test_cli_query_api_error():
    runner = CliRunner()
    with patch('main.APIClient') as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.side_effect = Exception("API Down")
        
        result = runner.invoke(cli, ['query'])
        
        assert result.exit_code != 0
        assert 'Error: API Request failed: API Down' in result.output
