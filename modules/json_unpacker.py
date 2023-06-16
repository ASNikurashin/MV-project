import json

def get_mode(path=r'../current_mode.json'):
    with open(path, 'r', encoding='utf-8') as f:
        settings = json.load(f)

    return settings

