import json
import pickle

from cachetools import TTLCache
from redis import Redis

from .config import bunny_config


class BunnyCache:
    def __init__(self, redis_client: Redis, ttl: int = 600, maxsize: int = 128):
        """
        使用 cachetools 和 redis 实现缓存

        Args:
            redis_client: redis 客户端实例
            ttl: 缓存过期时间（秒），默认为 600 秒
            maxsize: 最大缓存条目数，默认为 128
        """
        self.redis_client = redis_client
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key):
        """
        获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存值，如果缓存不存在或已过期，则返回 None
        """
        # 优先从内存缓存中获取
        value = self.cache.get(key)
        if value is not None:
            return value

        # 从 Redis 中获取
        serialized_value = self.redis_client.get(key)
        if serialized_value is None:
            return None

        # 反序列化并更新内存缓存
        try:
            value = self._deserialize(serialized_value)
            self.cache[key] = value
            return value
        except Exception:
            # 如果反序列化失败，删除 Redis 中的缓存
            self.redis_client.delete(key)
            return None

    def set(self, key, value, ttl=None):
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 缓存过期时间（秒），如果为 None，则使用初始化时设置的 ttl
        """
        # 更新内存缓存
        self.cache[key] = value

        # 序列化并存储到 Redis 中
        serialized_value = self._serialize(value)
        if ttl is None:
            self.redis_client.set(key, serialized_value)
        else:
            self.redis_client.setex(key, ttl, serialized_value)

    def delete(self, key):
        """
        删除缓存

        Args:
            key: 缓存键
        """
        self.cache.pop(key, None)
        self.redis_client.delete(key)

    def _serialize(self, value):
        """
        序列化值，优先使用 JSON，如果失败则使用 pickle

        Args:
            value: 要序列化的值

        Returns:
            序列化后的字节串
        """
        try:
            return json.dumps(value).encode('utf-8')
        except (TypeError, OverflowError):
            return pickle.dumps(value)

    def _deserialize(self, serialized_value):
        """
        反序列化值，优先尝试 JSON，如果失败则尝试 pickle

        Args:
            serialized_value: 序列化后的字节串

        Returns:
            反序列化后的值
        """
        try:
            return json.loads(serialized_value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                return pickle.loads(serialized_value)
            except pickle.UnpicklingError:
                raise ValueError('Failed to deserialize value with both JSON and pickle')


bunny_cache = BunnyCache(
    Redis(
        host=bunny_config.redis_host,
        port=bunny_config.redis_port,
        db=bunny_config.redis_db,
        password=bunny_config.redis_password,
    )
)
