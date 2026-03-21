import click
from api_client import APIClient
from formatter import format_json, format_table
from query_builder import build_select_clause, build_where_clause

@click.group()
def cli():
    """SF Property Data CLI - Query the San Francisco Data API."""
    pass

@cli.command()
@click.option('--bedrooms', help='Filter by number of bedrooms (e.g., 0, 1, 2).')
@click.option('--bathrooms', help='Filter by number of bathrooms (e.g., 1, 1.5, 2).')
@click.option('--parcel-number', help='Filter by parcel number (e.g., 0001/001).')
@click.option('--area-min', help='Minimum property area in square feet.')
@click.option('--area-max', help='Maximum property area in square feet.')
@click.option('--date-start', help='Filter by sales date (YYYY-MM-DD) - Start.')
@click.option('--date-end', help='Filter by sales date (YYYY-MM-DD) - End.')
@click.option('--district', help='Filter by assessor neighborhood district number.')
@click.option('--limit', type=int, default=100, help='Limit the number of results (default: 100).')
@click.option('--offset', type=int, default=0, help='Offset the results (default: 0).')
@click.option('--format', type=click.Choice(['json', 'table'], case_sensitive=False), default='json', help='Output format (default: json).')
@click.option('--verify/--no-verify', default=True, help='Verify SSL certificates.')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output.')
def query(bedrooms, bathrooms, parcel_number, area_min, area_max, date_start, date_end, district, limit, offset, format, verify, verbose):
    """Execute a specialized property query against the SF Data API."""
    params = {}
    if bedrooms: params['bedrooms'] = bedrooms
    if bathrooms: params['bathrooms'] = bathrooms
    if parcel_number: params['parcel_number'] = parcel_number
    if area_min: params['area_min'] = area_min
    if area_max: params['area_max'] = area_max
    if date_start: params['date_start'] = date_start
    if date_end: params['date_end'] = date_end
    if district: params['district'] = district

    select_clause = build_select_clause()
    where_clause = build_where_clause(params)
    
    soql_query = f"SELECT {select_clause}"
    if where_clause:
        soql_query += f" WHERE {where_clause}"
    
    soql_query += f" LIMIT {limit} OFFSET {offset}"
    
    if verbose:
        click.echo(f"Executing SoQL: {soql_query}", err=True)
    
    # APIClient defaults to https://data.sfgov.org
    client = APIClient(verify=verify)
    endpoint = "/resource/wv5m-vpq2.json"
    
    try:
        # Pass the SoQL query as the '$query' parameter
        response = client.get(endpoint, params={'$query': soql_query})
        
        if format.lower() == 'table':
            formatted_output = format_table(response.text)
        else:
            formatted_output = format_json(response.text)
            
        if verbose:
            click.echo(f"API Response [{response.status_code}]:", err=True)
        click.echo(formatted_output)
    except Exception as e:
        raise click.ClickException(f"API Request failed: {str(e)}")

if __name__ == '__main__':
    cli()
