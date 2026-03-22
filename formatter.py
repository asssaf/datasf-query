import json

def format_json(response_text):
    """Attempt to parse and pretty-print JSON response text."""
    try:
        data = json.loads(response_text)
        return json.dumps(data, indent=2)
    except (json.JSONDecodeError, TypeError):
        # If not JSON, return original text
        return response_text

def format_table(response_text, columns=None):
    """Format the JSON response as a pretty-printed table."""
    try:
        data = json.loads(response_text)
        if not isinstance(data, list) or not data:
            return "No data found or invalid format for table."
        
        # Determine columns
        if columns is None:
            # If columns not provided, collect all unique keys from all rows
            # but preserve order from first row encountered
            columns = []
            seen = set()
            for item in data:
                for key in item.keys():
                    if key not in seen:
                        columns.append(key)
                        seen.add(key)
        
        if not columns:
            return "No columns found to display."

        # Calculate max width for each column
        widths = {col: len(col) for col in columns}
        for item in data:
            for col in columns:
                val = str(item.get(col, ""))
                widths[col] = max(widths[col], len(val))
        
        # Create header
        header = " | ".join(col.ljust(widths[col]) for col in columns)
        separator = "-+-".join("-" * widths[col] for col in columns)
        
        lines = [header, separator]
        
        # Create rows
        for item in data:
            row = " | ".join(str(item.get(col, "")).ljust(widths[col]) for col in columns)
            lines.append(row)
            
        return "\n".join(lines)
    except (json.JSONDecodeError, TypeError):
        return response_text
