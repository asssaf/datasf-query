def get_selected_fields(target_point=None, target_area=None, target_total_assessed_value=None, requested_fields=None):
    """Returns a list of field names/aliases to be included in the output."""
    default_fields = [
        "closed_roll_year",
        "property_location",
        "parcel_number",
        "assessor_neighborhood_code",
        "property_area",
        "number_of_bedrooms",
        "number_of_bathrooms",
        "current_sales_date",
        "property_class_code",
        "year_property_built",
        "assessed_improvement_value",
        "assessed_land_value",
        "the_geom",
        "number_of_rooms",
        "total_assessed_value"
    ]

    if requested_fields:
        fields_to_use = []
        for f in requested_fields:
            if f == "distance_from_target" and target_point is None:
                continue
            if f == "property_area_ratio" and target_area is None:
                continue
            if f == "total_assessed_value_ratio" and target_total_assessed_value is None:
                continue
            fields_to_use.append(f)
    else:
        fields_to_use = default_fields[:]
        if target_point:
            fields_to_use.append("distance_from_target")
        if target_area is not None:
            fields_to_use.append("property_area_ratio")
        if target_total_assessed_value is not None:
            fields_to_use.append("total_assessed_value_ratio")
        fields_to_use.sort()

    return fields_to_use

def build_select_clause(target_point=None, target_area=None, target_total_assessed_value=None, requested_fields=None):
    fields_to_use = get_selected_fields(target_point, target_area, target_total_assessed_value, requested_fields)

    select_parts = []
    for field in fields_to_use:
        if field == "distance_from_target":
            if target_point:
                lon, lat = target_point
                select_parts.append(f"distance_in_meters(`the_geom`, 'POINT ({lon} {lat})') AS distance_from_target")
        elif field == "property_area_ratio":
            if target_area is not None:
                select_parts.append(f"property_area / {target_area} AS property_area_ratio")
        elif field == "total_assessed_value_ratio":
            if target_total_assessed_value is not None:
                total_expr = "(coalesce(assessed_improvement_value, 0) + coalesce(assessed_land_value, 0) + coalesce(assessed_fixtures_value, 0))"
                select_parts.append(f"{total_expr} / {target_total_assessed_value} AS total_assessed_value_ratio")
        elif field == "total_assessed_value":
            select_parts.append("coalesce(assessed_improvement_value, 0) + coalesce(assessed_land_value, 0) + coalesce(assessed_fixtures_value, 0) AS total_assessed_value")
        else:
            select_parts.append(field)

    return ", ".join(select_parts)

def build_order_by_clause(target_point=None, target_area=None):
    order_parts = []
    if target_point:
        lon, lat = target_point
        order_parts.append(f"distance_in_meters(`the_geom`, 'POINT ({lon} {lat})')")

    if target_area is not None:
        order_parts.append(f"property_area / {target_area}")

    return ", ".join(order_parts) if order_parts else None

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
        districts = params['district']
        if isinstance(districts, list):
            quoted_districts = ", ".join([f'"{d}"' for d in districts])
            filters.append(f'caseless_one_of(assessor_neighborhood_district, {quoted_districts})')
        else:
            filters.append(f'caseless_one_of(assessor_neighborhood_district, "{districts}")')

    if 'property_class_code' in params:
        codes = params['property_class_code']
        if isinstance(codes, list):
            quoted_codes = ", ".join([f'"{c}"' for c in codes])
            filters.append(f'caseless_one_of(property_class_code, {quoted_codes})')
        else:
            filters.append(f'caseless_one_of(property_class_code, "{codes}")')

    if 'neighborhood_code' in params:
        codes = params['neighborhood_code']
        if isinstance(codes, list):
            quoted_codes = ", ".join([f'"{c}"' for c in codes])
            filters.append(f'caseless_one_of(assessor_neighborhood_code, {quoted_codes})')
        else:
            filters.append(f'caseless_one_of(assessor_neighborhood_code, "{codes}")')

    if 'roll_year' in params:
        val = params['roll_year']
        filters.append(f'closed_roll_year = "{val}"')
        
    return " AND ".join(filters)
