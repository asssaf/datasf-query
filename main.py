import click
from api_client import APIClient

@click.group()
def cli():
    """A CLI app that executes a rest api which performs a query with multiple arguments."""
    pass

@cli.command()
@click.option('--base-url', default='https://api.example.com', help='Base URL of the REST API.')
@click.option('--endpoint', default='endpoint', help='API endpoint to query.')
@click.option('--param', multiple=True, help='Query parameters in key=value format.')
@click.option('--auth-token', help='Bearer token for authentication.')
@click.option('--api-key', help='API Key for authentication (X-API-Key).')
@click.option('--verify/--no-verify', default=True, help='Verify SSL certificates.')
def query(base_url, endpoint, param, auth_token, api_key, verify):
    """Execute a query with multiple arguments."""
    query_params = {}
    for p in param:
        if '=' not in p:
            raise click.ClickException(f"Invalid parameter format: '{p}'. Use key=value.")
        key, value = p.split('=', 1)
        query_params[key] = value
    
    headers = {}
    if auth_token:
        headers['Authorization'] = f"Bearer {auth_token}"
    if api_key:
        headers['X-API-Key'] = api_key
    
    click.echo(f"Querying {base_url}/{endpoint} with arguments: {query_params}")
    
    client = APIClient(base_url, verify=verify)
    try:
        response = client.get(endpoint, params=query_params, headers=headers)
        click.echo(f"API Response [{response.status_code}]: {response.text}")
    except Exception as e:
        raise click.ClickException(f"API Request failed: {str(e)}")

if __name__ == '__main__':
    cli()
