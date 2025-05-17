class Connection:
    row_factory = None
    async def cursor(self):
        return self
    async def execute(self, *args, **kwargs):
        return None
    async def executescript(self, *args, **kwargs):
        return None
    async def commit(self):
        return None
    async def rollback(self):
        return None
    async def close(self):
        return None

async def connect(path):
    return Connection()

Row = dict
