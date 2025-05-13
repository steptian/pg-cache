import os
import yaml

class ConfigLoader:
    """
    统一加载和管理数据库与缓存策略配置。
    """
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), '..', 'config')
        self.db_config = None
        self.cache_config = None
        self.no_db_mode = False
        self.load_configs()

    def load_configs(self):
        self.db_config = self._load_yaml('db.yaml').get('postgres', {})
        cache_yaml = self._load_yaml('cache.yaml')
        self.cache_config = cache_yaml.get('cache', [])
        self.no_db_mode = cache_yaml.get('no_db_mode', False)

    def _load_yaml(self, filename):
        path = os.path.join(self.config_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def get_db_config(self):
        return self.db_config

    def get_cache_config(self):
        return self.cache_config

    def get_no_db_mode(self):
        return self.no_db_mode

    def reload(self):
        self.load_configs()

# 用法示例
if __name__ == '__main__':
    loader = ConfigLoader()
    print('DB配置:', loader.get_db_config())
    print('缓存配置:', loader.get_cache_config())
    print('无源数据库模式:', loader.get_no_db_mode()) 