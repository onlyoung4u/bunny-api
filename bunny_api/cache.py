import json
import pickle
from abc import ABC, abstractmethod
from typing import Any, Optional

from cachetools import TTLCache
from redis import Redis

from .config import BUNNY_CONFIG


class Cache(ABC):
    """缓存基类"""

    @abstractmethod
    def get(self, key: str) -> Any:
        """获取缓存"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """删除缓存"""
        pass


class MemoryCache(Cache):
    """内存缓存"""

    def __init__(self, maxsize: int = 128):
        """
        初始化内存缓存

        Args:
            maxsize: 最大缓存条目数，默认为 128
        """
        self.permanent_cache = {}  # 永久缓存
        self.ttl_cache = TTLCache(maxsize=maxsize, ttl=float('inf'))  # 临时缓存

    def get(self, key: str) -> Any:
        # 优先从永久缓存获取
        value = self.permanent_cache.get(key)
        if value is not None:
            return value

        # 从临时缓存获取
        return self.ttl_cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if ttl is None:
            self.permanent_cache[key] = value
        else:
            self.ttl_cache.timer = ttl
            self.ttl_cache[key] = value

    def delete(self, key: str) -> None:
        self.permanent_cache.pop(key, None)
        self.ttl_cache.pop(key, None)


class RedisCache(Cache):
    """Redis 缓存"""

    def __init__(self, redis_client: Redis):
        """
        初始化 Redis 缓存

        Args:
            redis_client: Redis 客户端实例
        """
        self.redis_client = redis_client

    def get(self, key: str) -> Any:
        serialized_value = self.redis_client.get(key)
        if serialized_value is None:
            return None

        try:
            return self._deserialize(serialized_value)
        except Exception:
            self.redis_client.delete(key)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        serialized_value = self._serialize(value)
        if ttl is None:
            self.redis_client.set(key, serialized_value)
        else:
            self.redis_client.setex(key, ttl, serialized_value)

    def delete(self, key: str) -> None:
        self.redis_client.delete(key)

    def _serialize(self, value: Any) -> bytes:
        """序列化值，优先使用 JSON，如果失败则使用 pickle"""
        try:
            return json.dumps(value).encode('utf-8')
        except (TypeError, OverflowError):
            return pickle.dumps(value)

    def _deserialize(self, serialized_value: bytes) -> Any:
        """反序列化值，优先尝试 JSON，如果失败则尝试 pickle"""
        try:
            return json.loads(serialized_value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                return pickle.loads(serialized_value)
            except pickle.UnpicklingError:
                raise ValueError('Failed to deserialize value with both JSON and pickle')


class BunnyCache:
    def __init__(self, redis_client: Redis, maxsize: int = 128):
        """
        使用内存和 Redis 实现多级缓存

        Args:
            redis_client: Redis 客户端实例
            maxsize: 最大内存缓存条目数，默认为 128
        """
        self.memory_cache = MemoryCache(maxsize=maxsize)
        self.redis_cache = RedisCache(redis_client)

    def get(self, key: str) -> Any:
        """获取缓存,优先从内存获取,不存在则从 Redis 获取"""
        # 优先从内存缓存中获取
        value = self.memory_cache.get(key)
        if value is not None:
            return value

        # 从 Redis 中获取
        value = self.redis_cache.get(key)
        if value is not None:
            self.memory_cache.set(key, value)
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """同时设置内存和 Redis 缓存"""
        self.memory_cache.set(key, value, ttl)
        self.redis_cache.set(key, value, ttl)

    def delete(self, key: str) -> None:
        """同时删除内存和 Redis 缓存"""
        self.memory_cache.delete(key)
        self.redis_cache.delete(key)

    def get_memory(self, key: str) -> Any:
        """仅从内存获取缓存"""
        return self.memory_cache.get(key)

    def set_memory(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """仅设置内存缓存"""
        self.memory_cache.set(key, value, ttl)

    def delete_memory(self, key: str) -> None:
        """仅删除内存缓存"""
        self.memory_cache.delete(key)

    def get_redis(self, key: str) -> Any:
        """仅从 Redis 获取缓存"""
        return self.redis_cache.get(key)

    def set_redis(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """仅设置 Redis 缓存"""
        self.redis_cache.set(key, value, ttl)

    def delete_redis(self, key: str) -> None:
        """仅删除 Redis 缓存"""
        self.redis_cache.delete(key)


bunny_cache = BunnyCache(
    Redis(
        host=BUNNY_CONFIG.redis_host,
        port=BUNNY_CONFIG.redis_port,
        db=BUNNY_CONFIG.redis_db,
        password=BUNNY_CONFIG.redis_password,
    )
)
