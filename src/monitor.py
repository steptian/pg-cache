from src.cache_manager import CacheManager
import logging

class CacheMonitor:
    """
    监控与可观测性：采集命中率、回源次数、缓存空间等指标，支持异常日志输出。
    """
    def __init__(self, cache_manager=None):
        self.cache = cache_manager or CacheManager()
        self.logger = logging.getLogger('pg-cache')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.back_source_count = 0

    def log_back_source(self):
        self.back_source_count += 1
        self.logger.info('回源数据库次数累计: %d', self.back_source_count)

    def get_metrics(self):
        stats = self.cache.get_stats()
        return {
            'cache_hits': stats['hits'],
            'cache_misses': stats['misses'],
            'cache_hit_rate': stats['hit_rate'],
            'back_source_count': self.back_source_count
        }

    def log_exception(self, msg, exc=None):
        if exc:
            self.logger.error('%s: %s', msg, exc)
        else:
            self.logger.error('%s', msg)

# 用法示例
if __name__ == '__main__':
    monitor = CacheMonitor()
    monitor.log_back_source()
    print(monitor.get_metrics())
    try:
        raise ValueError('test')
    except Exception as e:
        monitor.log_exception('异常示例', e) 