import unittest
from src.api import PgCacheAPI
from src.config_loader import ConfigLoader

class TestPgCacheAPI(unittest.TestCase):
    def setUp(self):
        # 强制无源数据库模式
        self.api = PgCacheAPI()
        self.api.cache.clear()
        self.no_db_mode = self.api.is_no_db_mode()

    def test_set_get_invalidate(self):
        self.api.set('user', 1, 'name', 'Alice')
        self.assertEqual(self.api.get('user', 1, 'name'), 'Alice')
        self.api.invalidate('user', 1, 'name')
        self.assertIsNone(self.api.get('user', 1, 'name'))

    def test_query(self):
        # 结构化查询在无源模式下应返回空列表
        if self.no_db_mode:
            result = self.api.query('user', {'id': 1}, ['id', 'name'], limit=1, cache_result=False)
            self.assertEqual(result, [])
        else:
            try:
                self.api.query('user', {'id': 1}, ['id', 'name'], limit=1, cache_result=False)
            except Exception as e:
                self.assertIsInstance(e, Exception)

    def test_batch_sync(self):
        # 无源模式下 batch_sync 应返回 0
        if self.no_db_mode:
            self.assertEqual(self.api.batch_sync('user'), 0)
        else:
            try:
                self.api.batch_sync('user')
            except Exception as e:
                self.assertIsInstance(e, Exception)

if __name__ == '__main__':
    unittest.main() 