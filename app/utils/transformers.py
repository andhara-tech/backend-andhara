def transform_keys(data: dict, field_map: dict) -> dict:
    """
    Transforms the keys of a dictionary according to a given field map.
    Args:
        data (dict): Entry dictionary.
        field_map (dict): Dictionary that maps original keys to new keys.
    Returns:
        dict: New dictionary with transformed keys.
    """
    return {field_map[key]: value for key, value in data.items() if key in field_map}
  
  
def transform_keys_reverse(data: dict, field_map: dict) -> dict:
    """
    Transforms the keys of a dictionary using the inverse mapping of the given field map.
    Args:
        data (dict): Entry dictionary.
        field_map (dict): Diccionario que mapea llaves en español a inglés.
    Returns:
        dict: New dictionary with converted keys (English to Spanish).
    """
    reverse_map = {v: k for k, v in field_map.items()}
    return {reverse_map[key]: value for key, value in data.items() if key in reverse_map}