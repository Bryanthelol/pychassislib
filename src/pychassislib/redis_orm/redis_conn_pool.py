import redis
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RedisConnPool:
    host: str = field(default='localhost')
    port: int = field(default=6379)
    db: int = field(default=0)
    password: str = field(default='')
    decode_responses: bool = field(default=True)

    @property
    def client(self):
        redis_pool_params = dict(host=self.host, port=self.port, db=self.db, decode_responses=self.decode_responses)
        if self.password:
            redis_pool_params['password'] = self.password
        redis_pool = redis.ConnectionPool(**redis_pool_params)
        client = redis.StrictRedis(connection_pool=redis_pool)
        return client
