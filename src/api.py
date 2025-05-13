from src.cache_manager import CacheManager
from src.cache_sync import CacheSync
from src.cache_consistency import CacheConsistency
from src.structured_query import StructuredQuery
from src.config_loader import ConfigLoader

class PgCacheAPI:
    """
    对外统一 API 层，封装所有核心功能。
    """
    def __init__(self):
        self.config = ConfigLoader()
        self.no_db_mode = self.config.get_no_db_mode()
        self.cache = CacheManager()
        self.sync = CacheSync(self.cache, config_loader=self.config)
        self.consistency = CacheConsistency(self.cache, config_loader=self.config)
        self.structured_query = StructuredQuery(self.cache, config_loader=self.config)

    # 基础缓存操作
    def get(self, table, key, field):
        return self.cache.get(table, key, field)

    def set(self, table, key, field, value, ttl=None):
        self.cache.set(table, key, field, value, ttl)

    def invalidate(self, table, key=None, field=None):
        self.cache.invalidate(table, key, field)

    # 回源与同步
    def get_with_fallback(self, table, key, field):
        return self.sync.get_with_fallback(table, key, field)

    def batch_sync(self, table, key_range=None):
        return self.sync.batch_sync(table, key_range)

    def get_sync_progress(self, table):
        return self.sync.get_sync_progress(table)

    # 一致性保障
    def update_and_sync(self, table, key, field, value, ttl=None):
        self.consistency.update_and_sync(table, key, field, value, ttl)

    def invalidate_on_write(self, table, key, field=None):
        self.consistency.invalidate_on_write(table, key, field)

    def manual_invalidate(self, table, key=None, field=None):
        self.consistency.manual_invalidate(table, key, field)

    # 结构化查询
    def query(self, table, filters, fields, limit=None, offset=None, cache_result=True, ttl=None):
        return self.structured_query.query(table, filters, fields, limit, offset, cache_result, ttl)

    def invalidate_query_cache(self, table):
        self.structured_query.invalidate_query_cache(table)

    def is_no_db_mode(self):
        return self.no_db_mode

# 用法示例
if __name__ == '__main__':
    api = PgCacheAPI()
    print('无源数据库模式:', api.is_no_db_mode())
    # 示例：api.get('your_table', 1, 'field1')
    # 示例：api.query('your_table', {'status': 1}, ['id', 'name'], limit=10) 