import pytest
import sys
import os

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from query_builder import build_select_clause, build_where_clause, build_order_by_clause

def test_build_select_clause():
    expected_fields = [
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
    select_clause = build_select_clause()
    # SoQL SELECT is a comma separated string
    fields = [f.strip() for f in select_clause.split(',')]
    assert set(fields) == set(expected_fields)

def test_build_select_clause_with_target():
    target_point = (-122.4194, 37.7749)
    select_clause = build_select_clause(target_point=target_point)
    assert "distance_in_meters(`the_geom`, 'POINT (-122.4194 37.7749)') AS distance_from_target" in select_clause

def test_build_order_by_clause_none():
    assert build_order_by_clause() is None

def test_build_order_by_clause_with_target():
    target_point = (-122.4194, 37.7749)
    assert build_order_by_clause(target_point=target_point) == "distance_from_target"

def test_build_where_clause_bedrooms():
    # According to spec, bedrooms 0 should generate 'number_of_bedrooms IN ("0.0")'
    params = {'bedrooms': '2'}
    where = build_where_clause(params)
    assert 'number_of_bedrooms IN ("2.0")' in where

def test_build_where_clause_bathrooms():
    params = {'bathrooms': '1.5'}
    where = build_where_clause(params)
    assert 'number_of_bathrooms IN ("1.5")' in where

def test_build_where_clause_parcel_number():
    params = {'parcel_number': '3776182'}
    where = build_where_clause(params)
    assert 'parcel_number = "3776182"' in where

def test_build_where_clause_both_numeric():
    params = {'bedrooms': '3', 'bathrooms': '2'}
    where = build_where_clause(params)
    assert 'number_of_bedrooms IN ("3.0")' in where
    assert 'number_of_bathrooms IN ("2.0")' in where
    assert ' AND ' in where

def test_build_where_clause_area_min():
    params = {'area_min': '500'}
    where = build_where_clause(params)
    assert 'property_area >= 500' in where

def test_build_where_clause_area_max():
    params = {'area_max': '1000'}
    where = build_where_clause(params)
    assert 'property_area <= 1000' in where

def test_build_where_clause_area_range():
    params = {'area_min': '500', 'area_max': '1000'}
    where = build_where_clause(params)
    assert 'property_area BETWEEN 500 AND 1000' in where

def test_build_where_clause_date_start():
    params = {'date_start': '2023-01-01'}
    where = build_where_clause(params)
    assert "current_sales_date >= '2023-01-01'::floating_timestamp" in where

def test_build_where_clause_date_end():
    params = {'date_end': '2023-12-31'}
    where = build_where_clause(params)
    assert "current_sales_date <= '2023-12-31'::floating_timestamp" in where

def test_build_where_clause_date_range():
    params = {'date_start': '2023-01-01', 'date_end': '2023-12-31'}
    where = build_where_clause(params)
    assert "current_sales_date BETWEEN '2023-01-01'::floating_timestamp AND '2023-12-31'::floating_timestamp" in where

def test_build_where_clause_district():
    params = {'district': '9'}
    where = build_where_clause(params)
    assert 'caseless_one_of(assessor_neighborhood_district, "9")' in where

def test_build_where_clause_roll_year():
    params = {'roll_year': '2021'}
    where = build_where_clause(params)
    assert 'closed_roll_year = "2021"' in where

def test_build_where_clause_combined():
    params = {
        'bedrooms': '2',
        'area_min': '500',
        'date_start': '2023-01-01',
        'district': '10'
    }
    where = build_where_clause(params)
    assert 'number_of_bedrooms IN ("2.0")' in where
    assert 'property_area >= 500' in where
    assert "current_sales_date >= '2023-01-01'::floating_timestamp" in where
    assert 'caseless_one_of(assessor_neighborhood_district, "10")' in where
    assert where.count(' AND ') == 3
