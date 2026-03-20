import pytest
import sys
import os

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from query_builder import build_select_clause

def test_build_select_clause():
    expected_fields = [
        "closed_roll_year",
        "property_location",
        "parcel_number",
        "assessor_neighborhood_district",
        "property_area",
        "number_of_bedrooms",
        "number_of_bathrooms",
        "current_sales_date"
    ]
    select_clause = build_select_clause()
    # SoQL SELECT is a comma separated string
    fields = [f.strip() for f in select_clause.split(',')]
    assert set(fields) == set(expected_fields)
