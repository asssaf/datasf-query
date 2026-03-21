def build_select_clause(target_point=None):
    fields = [
        "closed_roll_year",
        "property_location",
        "parcel_number",
        "assessor_neighborhood_district",
        "property_area",
        "number_of_bedrooms",
        "number_of_bathrooms",
        "current_sales_date",
        "property_class_code",
        "year_property_built",
        "assessed_improvement_value",
        "assessed_land_value",
        "the_geom",
        "number_of_rooms"
    ]
    if target_point:
        lon, lat = target_point
        fields.append(f"distance_in_meters(`the_geom`, 'POINT ({lon} {lat})') AS distance_from_target")
    return ", ".join(fields)

def build_order_by_clause(target_point=None):
    if target_point:
        return "distance_from_target"
    return None

def build_where_clause(params):
    filters = []
    
    if 'bedrooms' in params:
        val = float(params['bedrooms'])
        filters.append(f'number_of_bedrooms IN ("{val}")')
    
    if 'bathrooms' in params:
        val = float(params['bathrooms'])
        filters.append(f'number_of_bathrooms IN ("{val}")')

    if 'parcel_number' in params:
        val = params['parcel_number']
        filters.append(f'parcel_number = "{val}"')

    area_min = params.get('area_min')
    area_max = params.get('area_max')
    
    if area_min and area_max:
        filters.append(f'property_area BETWEEN {area_min} AND {area_max}')
    elif area_min:
        filters.append(f'property_area >= {area_min}')
    elif area_max:
        filters.append(f'property_area <= {area_max}')

    date_start = params.get('date_start')
    date_end = params.get('date_end')
    
    if date_start and date_end:
        filters.append(f"current_sales_date BETWEEN '{date_start}'::floating_timestamp AND '{date_end}'::floating_timestamp")
    elif date_start:
        filters.append(f"current_sales_date >= '{date_start}'::floating_timestamp")
    elif date_end:
        filters.append(f"current_sales_date <= '{date_end}'::floating_timestamp")

    if 'district' in params:
        district = params['district']
        filters.append(f'caseless_one_of(assessor_neighborhood_district, "{district}")')

    if 'roll_year' in params:
        val = params['roll_year']
        filters.append(f'closed_roll_year = "{val}"')
        
    return " AND ".join(filters)
