from .database import select, execute, CONFIG
from datetime import datetime

class Table:
    def __init__(self, key: str, limit: int = 100000):
        self.status = False
        self.prefix = None
        self.limit = limit
        self.key = key
        self.logs = {}

    def request(self, params: dict = None):
        self.start = datetime.now().astimezone()
        self.response = select(configuration=self.key, params=params)

    def digest(self):
        self.data = self.response.mappings().fetchmany(size=self.limit)

    def transform(self):
        config = CONFIG[self.key]
        self.logs.update({'execution': f"{self.prefix}_{self.key}" if self.prefix else self.key, 'target': f'{config["schema"]}.{config["table"]}', 'date': self.start.date(), 'start': self.start})
        try:
            while self.data:
                self.status = self.status or execute(data=self.data, configuration=self.key)
                self.digest()
        finally:
            self.response.close()
        self.logs.update({'status': self.status, 'end': datetime.now().astimezone()})
        execute(data=[self.logs], configuration='logs')

REGISTRY: dict[str, Table] = {}