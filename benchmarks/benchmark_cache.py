import time
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from cache_manager import CacheManager

def benchmark_set_get(n=10000):
    cache = CacheManager()
    start = time.time()
    for i in range(n):
        cache.set('bench', i, 'value', f'value_{i}', ttl=60)
    set_time = time.time() - start

    start = time.time()
    for i in range(n):
        cache.get('bench', i, 'value')
    get_time = time.time() - start

    print(f'Set {n} times, total: {set_time:.4f}s, avg: {set_time/n*1000:.4f}ms')
    print(f'Get {n} times, total: {get_time:.4f}s, avg: {get_time/n*1000:.4f}ms')

    # 导出缓存内容
    cache.dump_cache_to_file('cache_dump_benchmark.json')

if __name__ == '__main__':
    benchmark_set_get(100000) 