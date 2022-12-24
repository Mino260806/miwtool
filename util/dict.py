def inverse_dict(dictionary: dict, supplier):
    result = dict()
    for key, value in dictionary.items():
        if not isinstance(value, dict):
            result[supplier(value)] = key
        else:
            result[key] = inverse_dict(value)
    return result
