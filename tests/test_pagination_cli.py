from click.testing import CliRunner
from main import cli
from unittest.mock import patch, MagicMock

def test_cli_pagination_args():
    runner = CliRunner()
    with patch('main.APIClient') as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '[]'
        mock_instance.get.return_value = mock_response
        
        result = runner.invoke(cli, ['query', '--limit', '50', '--offset', '10'])
        
        assert result.exit_code == 0
        
        # Verify API call
        mock_instance.get.assert_called_once()
        args, kwargs = mock_instance.get.call_args
        assert 'LIMIT 50 OFFSET 10' in kwargs['params']['$query']
