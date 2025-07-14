import re, json
from collections import defaultdict

def parse_nested_formdata(flat_data):
    """
    Convert flat keys like postQuestions[0][question] to nested dicts/lists.
    """
    result = {}
    pattern = re.compile(r'^([^\[]+)((?:\[\w*\])*)$')

    for flat_key, value in flat_data.items():
        match = pattern.match(flat_key)
        if not match:
            result[flat_key] = value
            continue

        key, path = match.groups()
        path = re.findall(r'\[(\w*)\]', path)

        cursor = result
        for i, p in enumerate([key] + path):
            is_last = (i == len(path))
            if p.isdigit():
                p = int(p)
                if not isinstance(cursor, list):
                    cursor = []  # create a new list if not exists
                    result[key] = cursor
                while len(cursor) <= p:
                    cursor.append({})
                if is_last:
                    cursor[p] = value
                else:
                    if not isinstance(cursor[p], dict):
                        cursor[p] = {}
                    cursor = cursor[p]
            else:
                if is_last:
                    cursor.setdefault(p, value)
                else:
                    cursor = cursor.setdefault(p, {})
    return result

def serialize(value):
    if hasattr(value, 'read') and hasattr(value, 'name'):
        return f"<file: {value.name}>"
    elif isinstance(value, list):
        return [serialize(v) for v in value]
    elif isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}
    return value

def print_formdata_content(formdata):
    """
    Use parse_nested_formdata() to convert flat FormData,
    serialize it, and print as valid JSON.
    Files are shown by filename to avoid JSON errors.
    """
    if not formdata:
        print("No form data provided.")
        return

    # Step 1: Reconstruct nested dict from flat keys
    nested_data = parse_nested_formdata(formdata)

    # Step 2: Safely serialize any file objects
    safe_data = serialize(nested_data)

    # Step 3: Print as pretty JSON
    print("Form Data Content:")
    print(json.dumps(safe_data, indent=2))