import time
import unittest
from src.cache_manager import CacheManager

class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.cache = CacheManager()

    def tearDown(self):
        # 每次测试后 dump 缓存内容到文件
        self.cache.dump_cache_to_file('cache_dump_test_cache_manager.json')

    def test_set_get(self):
        self.cache.set('user', 1, 'name', 'Alice')
        self.assertEqual(self.cache.get('user', 1, 'name'), 'Alice')

    def test_ttl_expiry(self):
        self.cache.set('user', 2, 'name', 'Bob', ttl=1)
        time.sleep(1.1)
        self.assertIsNone(self.cache.get('user', 2, 'name'))

    def test_invalidate(self):
        self.cache.set('user', 3, 'name', 'Eve')
        self.cache.invalidate('user', 3, 'name')
        self.assertIsNone(self.cache.get('user', 3, 'name'))

    def test_hit_miss_stats(self):
        self.cache.set('user', 4, 'name', 'Tom')
        self.cache.get('user', 4, 'name')  # hit
        self.cache.get('user', 4, 'age')   # miss
        stats = self.cache.get_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)

    def test_multi_table_and_field(self):
        self.cache.set('user', 10, 'name', 'Zoe')
        self.cache.set('user', 10, 'age', 30)
        self.cache.set('order', 100, 'amount', 99.9)
        self.cache.set('order', 100, 'status', 'paid')
        self.assertEqual(self.cache.get('user', 10, 'name'), 'Zoe')
        self.assertEqual(self.cache.get('user', 10, 'age'), 30)
        self.assertEqual(self.cache.get('order', 100, 'amount'), 99.9)
        self.assertEqual(self.cache.get('order', 100, 'status'), 'paid')

    def test_batch_set(self):
        for i in range(5):
            self.cache.set('product', i, 'price', i * 10)
        for i in range(5):
            self.assertEqual(self.cache.get('product', i, 'price'), i * 10)

if __name__ == '__main__':
    unittest.main() 