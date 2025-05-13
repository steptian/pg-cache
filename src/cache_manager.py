import time
import threading
from collections import defaultdict
import json

class CacheEntry:
    def __init__(self, value, expire_at=None):
        self.value = value
        self.expire_at = expire_at  # 绝对过期时间戳

    def is_expired(self):
        return self.expire_at is not None and time.time() > self.expire_at

class CacheManager:
    """
    支持表-字段-主键粒度的内存缓存，带 TTL 和命中率统计。
    结构: cache[table][key][field] = CacheEntry
    """
    def __init__(self):
        self.cache = defaultdict(lambda: defaultdict(dict))
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def set(self, table, key, field, value, ttl=None):
        expire_at = time.time() + ttl if ttl else None
        with self.lock:
            self.cache[table][key][field] = CacheEntry(value, expire_at)

    def get(self, table, key, field):
        with self.lock:
            entry = self.cache.get(table, {}).get(key, {}).get(field)
            if entry and not entry.is_expired():
                self.hits += 1
                return entry.value
            else:
                self.misses += 1
                # 过期则清理
                if entry:
                    del self.cache[table][key][field]
                return None

    def invalidate(self, table, key=None, field=None):
        with self.lock:
            if key is None:
                self.cache.pop(table, None)
            elif field is None:
                self.cache.get(table, {}).pop(key, None)
            else:
                self.cache.get(table, {}).get(key, {}).pop(field, None)

    def get_stats(self):
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total else 0
            return {
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate
            }

    def clear(self):
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def dump_cache(self):
        with self.lock:
            result = {}
            for table, keys in self.cache.items():
                result[table] = {}
                for key, fields in keys.items():
                    result[table][key] = {}
                    for field, entry in fields.items():
                        if not entry.is_expired():
                            result[table][key][field] = entry.value
            return result

    def dump_cache_to_file(self, filepath='cache_dump.json'):
        data = self.dump_cache()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# 用法示例
if __name__ == '__main__':
    cm = CacheManager()
    cm.set('user', 1, 'name', 'Alice', ttl=2)
    print('get:', cm.get('user', 1, 'name'))
    time.sleep(2.1)
    print('get after expire:', cm.get('user', 1, 'name'))
    print('stats:', cm.get_stats()) 