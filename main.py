import click
from api_client import APIClient
import json
from formatter import format_json, format_table
from query_builder import build_select_clause, build_where_clause, build_order_by_clause

@click.group()
def cli():
    """SF Property Data CLI - Query the San Francisco Data API."""
    pass

def parse_multi_value_option(values):
    """Parses multiple values from Click multiple=True option and comma-separated strings."""
    if not values:
        return None
    result = []
    for item in values:
        result.extend([x.strip() for x in item.split(',') if x.strip()])
    return result if result else None

@cli.command()
@click.option('--roll-year', help='Filter by closed roll year (e.g., 2021).')
@click.option('--bedrooms', help='Filter by number of bedrooms (e.g., 0, 1, 2).')
@click.option('--bathrooms', help='Filter by number of bathrooms (e.g., 1, 1.5, 2).')
@click.option('--parcel-number', help='Filter by parcel number (e.g., 3776182).')
@click.option('--target-parcel-number', help='Compare results to this parcel number.')
@click.option('--area-min', help='Minimum property area in square feet.')
@click.option('--area-max', help='Maximum property area in square feet.')
@click.option('--date-start', help='Filter by sales date (YYYY-MM-DD) - Start.')
@click.option('--date-end', help='Filter by sales date (YYYY-MM-DD) - End.')
@click.option('--district', multiple=True, help='Filter by assessor neighborhood district number. Can be used multiple times or comma-separated.')
@click.option('--property-class-code', multiple=True, help='Filter by property class code (e.g., D, E). Can be used multiple times or comma-separated.')
@click.option('--limit', type=int, default=100, help='Limit the number of results (default: 100).')
@click.option('--offset', type=int, default=0, help='Offset the results (default: 0).')
@click.option('--format', type=click.Choice(['json', 'table'], case_sensitive=False), default='json', help='Output format (default: json).')
@click.option('--verify/--no-verify', default=True, help='Verify SSL certificates.')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output.')
def query(roll_year, bedrooms, bathrooms, parcel_number, target_parcel_number, area_min, area_max, date_start, date_end, district, property_class_code, limit, offset, format, verify, verbose):
    """Execute a specialized property query against the SF Data API."""
    # APIClient defaults to https://data.sfgov.org
    client = APIClient(verify=verify)
    endpoint = "/resource/wv5m-vpq2.json"

    target_point = None
    if target_parcel_number:
        # Step 1: Lookup target parcel
        lookup_params = {'parcel_number': target_parcel_number}
        lookup_where = build_where_clause(lookup_params)
        lookup_query = f"SELECT the_geom WHERE {lookup_where} LIMIT 1"

        if verbose:
            click.echo(f"Looking up target parcel: {target_parcel_number}", err=True)
            click.echo(f"Executing SoQL: {lookup_query}", err=True)

        try:
            resp = client.get(endpoint, params={'$query': lookup_query})
            data = resp.json()
            if not data:
                raise click.ClickException(f"Target parcel '{target_parcel_number}' not found.")

            the_geom = data[0].get('the_geom')
            if not the_geom or 'coordinates' not in the_geom:
                raise click.ClickException(f"Target parcel '{target_parcel_number}' has no geometry data.")

            target_point = the_geom['coordinates'] # [lon, lat]
        except Exception as e:
            if isinstance(e, click.ClickException):
                raise e
            raise click.ClickException(f"Failed to lookup target parcel: {str(e)}")

    params = {}
    if roll_year: params['roll_year'] = roll_year
    if bedrooms: params['bedrooms'] = bedrooms
    if bathrooms: params['bathrooms'] = bathrooms
    if parcel_number: params['parcel_number'] = parcel_number
    if area_min: params['area_min'] = area_min
    if area_max: params['area_max'] = area_max
    if date_start: params['date_start'] = date_start
    if date_end: params['date_end'] = date_end

    districts = parse_multi_value_option(district)
    if districts: params['district'] = districts

    class_codes = parse_multi_value_option(property_class_code)
    if class_codes: params['property_class_code'] = class_codes

    select_clause = build_select_clause(target_point=target_point)
    where_clause = build_where_clause(params)
    order_by_clause = build_order_by_clause(target_point=target_point)
    
    soql_query = f"SELECT {select_clause}"
    if where_clause:
        soql_query += f" WHERE {where_clause}"
    
    if order_by_clause:
        soql_query += f" ORDER BY {order_by_clause}"

    soql_query += f" LIMIT {limit} OFFSET {offset}"
    
    if verbose:
        click.echo(f"Executing SoQL: {soql_query}", err=True)
    
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
