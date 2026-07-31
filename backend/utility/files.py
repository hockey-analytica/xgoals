import json

def read(filepath: str):
    with open(filepath) as file:
        return json.load(file)