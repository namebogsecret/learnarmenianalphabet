class Response:
    def __init__(self, json_data=None):
        self._data = json_data or {}
    def json(self):
        return self._data

async def post(*args, **kwargs):
    return Response()
