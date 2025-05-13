from src.cache_manager import CacheManager
from src.config_loader import ConfigLoader

class CacheConsistency:
    """
    一致性保障层：写操作时同步更新/失效缓存，支持手动/自动失效。
    """
    def __init__(self, cache_manager=None, config_loader=None):
        self.cache = cache_manager or CacheManager()
        self.config = config_loader or ConfigLoader()

    def update_and_sync(self, table, key, field, value, ttl=None):
        """
        写操作时同步更新缓存。
        """
        self.cache.set(table, key, field, value, ttl)

    def invalidate_on_write(self, table, key, field=None):
        """
        写操作时失效缓存（可选字段级或主键级）。
        """
        self.cache.invalidate(table, key, field)

    def manual_invalidate(self, table, key=None, field=None):
        """
        手动失效缓存（支持表/主键/字段级）。
        """
        self.cache.invalidate(table, key, field)

    # 预留自动失效接口（如 CDC/触发器集成）
    def auto_invalidate(self, table, key, field=None):
        self.invalidate_on_write(table, key, field)

# 用法示例
if __name__ == '__main__':
    cc = CacheConsistency()
    cc.update_and_sync('your_table', 1, 'field1', 'new_value', ttl=60)
    cc.invalidate_on_write('your_table', 1, 'field1')
    cc.manual_invalidate('your_table', 1) 