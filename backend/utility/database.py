from sqlalchemy import create_engine, text, URL
from sqlalchemy.exc import SQLAlchemyError
from utility.files import read
from datetime import datetime
import os

ENGINE = create_engine(URL.create(drivername="postgresql+psycopg2", username=os.getenv("USER"), password=os.getenv("PASS"), host=os.getenv("HOST"), port=os.getenv("PORT"), database=os.getenv("NAME")))
CONFIG = read(filepath='config.json')

def select(configuration: str, query: str = None, params: dict = None):
    if query is None:
        config = CONFIG[configuration]
        query = config["query"]
    
    connection = ENGINE.connect().execution_options(stream_results=True)
    return connection.execute(text(query), params)

def execute(data: list[dict], configuration: str):
    error = False
    timestamp = datetime.now().astimezone()
    config = CONFIG[configuration]
    action = config["action"]
    target = f'"{config["schema"]}"."{config["table"]}"'
    keys = config["keys"]
    features = config["features"]
    excludes = config["excludes"]
    metadata = {"created_source": configuration, "created_timestamp": timestamp, "modified_source": configuration, "modified_timestamp": timestamp}

    if not len(data):
        print(f"No data found in {configuration}")
        error = True
        return error
    
    if action == "append":
        query = append(target=target, features=features)
    elif action == "update":
        query = update(target=target, keys=keys, features=features)
    elif action == "upsert":
        query = upsert(target=target, keys=keys, features=features, excludes=excludes)
    elif action == "delete":
        query = delete(target=target, keys=keys, features=features)
    else: 
        error = True
        return error
    
    try:
        with ENGINE.begin() as connection:
            connection.execute(text(query), [dict(record) | metadata for record in data if all(record.get(key) is not None for key in keys)])
    except SQLAlchemyError as message:
        error = True
        print(f"Error:\n{message}")
    
    return error

def append(target: str, features: dict[str, str]):
    columns = [f'"{key}"' for key in features.keys()]
    values = [f"CAST(:{key} AS {val})" for key, val in features.items()]
    insert_clause = f'INSERT INTO {target} ({", ".join(columns)})'
    values_clause = f'VALUES ({", ".join(values)})'

    return '\n'.join([insert_clause, values_clause])

def update(target: str, keys: list[str], features: dict[str, str]):
    values = [f'"{key}" = CAST(:{key} AS {val})' for key, val in features.items() if key not in keys]
    filters = [f'"{key}" = CAST(:{key} AS {val})' for key, val in features.items() if key in keys]
    update_clause = f'UPDATE {target}'
    set_clause = f'SET {',\n\t'.join(values)}'
    where_clause = f'WHERE {' AND '.join(filters)}'

    return '\n'.join([update_clause, set_clause, where_clause])

def upsert(target: str, keys: list[str], features: dict[str, str], excludes: list[str]):
    columns = [f'"{key}"' for key in features.keys()]
    values = [f"CAST(:{key} AS {val})" for key, val in features.items()]
    updates = [f'"{feat}" = EXCLUDED."{feat}"' for feat in features.keys() if feat not in keys and feat not in excludes]
    keys = [f'"{key}"' for key in keys]
    insert_clause = f'INSERT INTO {target} ({", ".join(columns)})'
    values_clause = f'VALUES ({", ".join(values)})'
    conflict_claues = f'ON CONFLICT ({", ".join(keys)}) DO UPDATE SET\n\t{",\n\t".join(updates)}'

    return '\n'.join([insert_clause, values_clause, conflict_claues])

def delete(target: str, keys: list[str], features: dict[str, str]):
    filters = [f'"{key}" = CAST(:{key} AS {val})' for key, val in features.items() if key in keys]
    update_clause = f'DELETE FROM {target}'
    where_clause = f'WHERE {', '.join(filters)}'

    return '\n'.join([update_clause, where_clause])