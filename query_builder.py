def build_select_clause():
    fields = [
        "closed_roll_year",
        "property_location",
        "parcel_number",
        "assessor_neighborhood_district",
        "property_area",
        "number_of_bedrooms",
        "number_of_bathrooms",
        "current_sales_date"
    ]
    return ", ".join(fields)
