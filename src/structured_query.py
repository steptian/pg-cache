from src.cache_manager import CacheManager
from src.db_client import PostgresClient
from src.config_loader import ConfigLoader
import hashlib
import json

class StructuredQuery:
    """
    结构化查询接口，支持多条件、字段选择、分页，并支持结果缓存与失效。
    """
    def __init__(self, cache_manager=None, db_client=None, config_loader=None):
        self.config = config_loader or ConfigLoader()
        self.no_db_mode = self.config.get_no_db_mode()
        self.cache = cache_manager or CacheManager()
        self.db = None if self.no_db_mode else (db_client or PostgresClient())

    def query(self, table, filters: dict, fields: list, limit=None, offset=None, cache_result=True, ttl=None):
        # 生成结构化查询缓存 key
        cache_key = self._make_cache_key(table, filters, fields, limit, offset)
        if cache_result:
            result = self.cache.get(table, cache_key, '__struct_query__')
            if result is not None:
                return result
        if self.no_db_mode:
            # 无源模式下仅查缓存，不查数据库
            return []
        # 构造 SQL
        where, params = self._build_where(filters)
        sql = f"SELECT {', '.join(fields)} FROM {table} {where}"
        if limit:
            sql += f" LIMIT {limit}"
        if offset:
            sql += f" OFFSET {offset}"
        rows = self.db.query(sql, params)
        if cache_result:
            self.cache.set(table, cache_key, '__struct_query__', rows, ttl)
        return rows

    def invalidate_query_cache(self, table):
        # 失效所有结构化查询缓存
        self.cache.invalidate(table)

    def _make_cache_key(self, table, filters, fields, limit, offset):
        key_obj = {
            'filters': filters,
            'fields': fields,
            'limit': limit,
            'offset': offset
        }
        key_str = json.dumps(key_obj, sort_keys=True)
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()

    def _build_where(self, filters):
        if not filters:
            return '', ()
        clauses = []
        params = []
        for k, v in filters.items():
            if isinstance(v, list):
                placeholders = ','.join(['%s'] * len(v))
                clauses.append(f"{k} IN ({placeholders})")
                params.extend(v)
            else:
                clauses.append(f"{k} = %s")
                params.append(v)
        where = 'WHERE ' + ' AND '.join(clauses)
        return where, tuple(params)

# 用法示例
if __name__ == '__main__':
    sq = StructuredQuery()
    print(sq.query('your_table', {'status': 1}, ['id', 'name'], limit=10)) 