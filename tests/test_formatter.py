import sys
import os
import json

# Add the root directory to sys.path to allow importing from the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from formatter import format_json, format_table

def test_format_valid_json():
    input_text = '{"key": "value", "list": [1, 2, 3]}'
    expected_output = json.dumps({"key": "value", "list": [1, 2, 3]}, indent=2)
    assert format_json(input_text) == expected_output

def test_format_invalid_json():
    input_text = 'Invalid JSON text'
    assert format_json(input_text) == input_text

def test_format_empty_input():
    assert format_json('') == ''

def test_format_none_input():
    assert format_json(None) == None

def test_format_table_valid():
    data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    input_text = json.dumps(data)
    # 2 chars for 'id', 5 for 'name'
    # Row: '1  | Alice'
    #      '2  | Bob  '
    output = format_table(input_text)
    assert "id | name" in output
    assert "1  | Alice" in output
    assert "2  | Bob  " in output

def test_format_table_missing_field_in_first_row():
    # Field 'age' is missing in the first row but present in the second
    data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob", "age": "30"}
    ]
    input_text = json.dumps(data)
    output = format_table(input_text)
    # Even without explicit columns, it should discover 'age' from the second row
    assert "id | name  | age" in output
    assert "1  | Alice |    " in output
    assert "2  | Bob   | 30 " in output

def test_format_table_explicit_columns():
    # Explicitly requested 'age' even though it's missing in all data
    data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    input_text = json.dumps(data)
    columns = ["id", "name", "age"]
    output = format_table(input_text, columns=columns)
    assert "id | name  | age" in output
    assert "1  | Alice |    " in output
    assert "2  | Bob   |    " in output

def test_format_table_explicit_columns_order():
    # User specifies columns in a specific order
    data = [
        {"id": "1", "name": "Alice"}
    ]
    input_text = json.dumps(data)
    columns = ["name", "id"]
    output = format_table(input_text, columns=columns)
    # The order should match the 'columns' list
    assert "name  | id" in output
    assert "Alice | 1 " in output

def test_format_table_not_list():
    input_text = '{"key": "value"}'
    assert format_table(input_text) == "No data found or invalid format for table."

def test_format_table_invalid_json():
    input_text = "Invalid JSON"
    assert format_table(input_text) == input_text
