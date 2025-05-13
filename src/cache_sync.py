from src.cache_manager import CacheManager
from src.db_client import PostgresClient
from src.config_loader import ConfigLoader
import threading

class CacheSync:
    """
    回源与同步层：未命中自动回源，支持批量同步和进度记录。
    """
    def __init__(self, cache_manager=None, db_client=None, config_loader=None):
        self.config = config_loader or ConfigLoader()
        self.no_db_mode = self.config.get_no_db_mode()
        self.cache = cache_manager or CacheManager()
        self.db = None if self.no_db_mode else (db_client or PostgresClient())
        self.sync_progress = {}  # {table: last_synced_key}
        self.lock = threading.RLock()

    def get_with_fallback(self, table, key, field):
        value = self.cache.get(table, key, field)
        if value is not None:
            return value
        if self.no_db_mode:
            return None
        # 回源
        cache_conf = self._get_cache_conf(table)
        if not cache_conf or field not in cache_conf['fields']:
            return None
        sql = f"SELECT {field} FROM {table} WHERE {cache_conf['key_field']} = %s"
        row = self.db.query_one(sql, (key,))
        if row:
            value = row[0]
            ttl = cache_conf.get('ttl')
            self.cache.set(table, key, field, value, ttl)
            return value
        return None

    def batch_sync(self, table, key_range=None):
        """
        批量同步指定表的缓存，key_range: (start, end) 或 None 表示全量。
        """
        cache_conf = self._get_cache_conf(table)
        if not cache_conf:
            return 0
        if self.no_db_mode:
            # 无源模式下不做任何同步，仅返回0
            with self.lock:
                self.sync_progress[table] = key_range[1] if key_range else 'ALL'
            return 0
        key_field = cache_conf['key_field']
        fields = ','.join(cache_conf['fields'])
        sql = f"SELECT {key_field},{fields} FROM {table}"
        params = ()
        if key_range:
            sql += f" WHERE {key_field} >= %s AND {key_field} <= %s"
            params = (key_range[0], key_range[1])
        rows = self.db.query(sql, params)
        count = 0
        ttl = cache_conf.get('ttl')
        for row in rows:
            key = row[0]
            for idx, field in enumerate(cache_conf['fields']):
                value = row[idx+1]
                self.cache.set(table, key, field, value, ttl)
            count += 1
        with self.lock:
            self.sync_progress[table] = key_range[1] if key_range else 'ALL'
        return count

    def get_sync_progress(self, table):
        with self.lock:
            return self.sync_progress.get(table)

    def _get_cache_conf(self, table):
        for conf in self.config.get_cache_config():
            if conf['table'] == table:
                return conf
        return None

# 用法示例
if __name__ == '__main__':
    cs = CacheSync()
    print(cs.get_with_fallback('your_table', 1, 'field1'))
    print(cs.batch_sync('your_table'))
    print(cs.get_sync_progress('your_table')) 