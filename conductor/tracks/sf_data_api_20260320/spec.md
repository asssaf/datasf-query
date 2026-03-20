# Specification: SF Data API Specialized Query

## Overview
Modify the existing CLI application to target the San Francisco Data API (Socrata) for property data. The CLI will provide user-friendly flags to build complex SoQL (Socrata Query Language) queries, specifically targeting the `wv5m-vpq2` resource.

## Functional Requirements
- **Target API**: Set the default base URL to `https://data.sfgov.org` and the endpoint to `/resource/wv5m-vpq2.json`.
- **Command Update**: Replace the generic `query` command with a specialized version that builds a `$query` parameter.
- **Query Builder Flags**:
    - `--bedrooms <n>`: Filters `number_of_bedrooms` (e.g., `IN ("0.0")`).
    - `--bathrooms <n>`: Filters `number_of_bathrooms` (e.g., `IN ("1.0")`).
    - `--area-min <n>` / `--area-max <n>`: Filters `property_area` using `BETWEEN ... AND ...`.
    - `--date-start <YYYY-MM-DD>` / `--date-end <YYYY-MM-DD>`: Filters `current_sales_date` using `BETWEEN ... :: floating_timestamp AND ...`.
    - `--district <n>`: Filters `assessor_neighborhood_district` (e.g., using `caseless_one_of` or equality).
- **SoQL Construction**: Automatically generate the `SELECT` clause with the standard set of fields (closed_roll_year, property_location, parcel_number, etc.) and the `WHERE` clause based on the provided flags.
- **Output Formatting**: Maintain support for JSON and Pretty-printed Table output.
- **No Authentication**: The endpoint does not require an API key for public data.

## Non-Functional Requirements
- **Secure Communication**: Ensure all requests use HTTPS.
- **Error Handling**: Provide clear error messages for invalid query parameters or network failures.

## Acceptance Criteria
- Running the CLI with `--bedrooms 0` generates a `$query` containing `number_of_bedrooms IN ("0.0")`.
- Running with `--area-min 450 --area-max 700` generates a `$query` containing `property_area BETWEEN 450 AND 700`.
- Running with date flags generates the correct `floating_timestamp` syntax.
- The CLI successfully retrieves data from `data.sfgov.org`.
