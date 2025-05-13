import psycopg2
import psycopg2.pool
import threading
from src.config_loader import ConfigLoader

class PostgresClient:
    """
    简单的 PostgreSQL 连接池客户端，支持单条和批量查询。
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        config = ConfigLoader().get_db_config()
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=config.get('minconn', 1),
            maxconn=config.get('maxconn', 10),
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        self._initialized = True

    def query(self, sql, params=None):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        finally:
            self.pool.putconn(conn)

    def query_one(self, sql, params=None):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchone()
        finally:
            self.pool.putconn(conn)

    def close(self):
        self.pool.closeall()

# 用法示例
if __name__ == '__main__':
    client = PostgresClient()
    print(client.query('SELECT 1')) 