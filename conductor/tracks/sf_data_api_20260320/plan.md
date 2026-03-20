# Implementation Plan - SF Data API Integration

## Phase 1: API Client Configuration [checkpoint: c22fe52]
- [x] Task: Update API Client Default Configuration [1f09543]
    - [x] Create test verifying the default Base URL is `https://data.sfgov.org` and endpoint is `/resource/wv5m-vpq2.json` [1f09543]
    - [x] Update `api_client.py` to use the new defaults [1f09543]
- [x] Task: Conductor - User Manual Verification 'Phase 1: API Client Configuration' (Protocol in workflow.md) [c22fe52]

## Phase 2: SoQL Query Builder Logic
- [x] Task: Implement SoQL `SELECT` Clause Generation [e07084c]
    - [x] Create `tests/test_query_builder.py` [e07084c]
    - [x] Test `build_select_clause` returns the full list of required fields (e.g., `closed_roll_year`, `property_location`, etc.) [e07084c]
    - [x] Implement `build_select_clause` function [e07084c]
- [x] Task: Implement SoQL `WHERE` Clause - Numeric Filters [f6044ff]
    - [x] Test `build_where_clause` correctly formats bedrooms/bathrooms (e.g., `number_of_bedrooms IN ("2.0")`) [f6044ff]
    - [x] Implement logic for `--bedrooms` and `--bathrooms` [f6044ff]
- [x] Task: Implement SoQL `WHERE` Clause - Range Filters [9c93715]
    - [x] Test `build_where_clause` correctly formats area ranges (e.g., `property_area BETWEEN 500 AND 1000`) [9c93715]
    - [x] Implement logic for `--area-min` and `--area-max` [9c93715]
- [ ] Task: Implement SoQL `WHERE` Clause - Date Filters
    - [ ] Test `build_where_clause` correctly formats dates with `floating_timestamp` cast
    - [ ] Implement logic for `--date-start` and `--date-end`
- [ ] Task: Implement SoQL `WHERE` Clause - District Filter
    - [ ] Test `build_where_clause` correctly formats district (e.g., `caseless_one_of(assessor_neighborhood_district, "9")`)
    - [ ] Implement logic for `--district`
- [ ] Task: Conductor - User Manual Verification 'Phase 2: SoQL Query Builder Logic' (Protocol in workflow.md)

## Phase 3: CLI Integration
- [ ] Task: Update CLI Command and Options in `main.py`
    - [ ] Test that the CLI accepts the new flags (`--bedrooms`, `--area-min`, etc.)
    - [ ] Refactor `main.py` to replace the generic `query` command options with the new specific flags
- [ ] Task: Connect CLI to Query Builder
    - [ ] Test that the CLI correctly invokes the query builder and passes the result to the API client
    - [ ] Implement the glue logic in `main.py`
- [ ] Task: Conductor - User Manual Verification 'Phase 3: CLI Integration' (Protocol in workflow.md)

## Phase 4: Output & Final Polish
- [ ] Task: Verify and Polish Output Formatting
    - [ ] Verify JSON output structure with the new data schema
    - [ ] Verify Table output formatting (ensure columns align and headers are readable)
    - [ ] Update `formatter.py` if necessary to handle the SF Data schema elegantly
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Output & Final Polish' (Protocol in workflow.md)
