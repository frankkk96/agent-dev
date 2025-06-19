import redis


class Redis:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.redis = redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            ssl=True
        )
