import unittest
import os
import shutil
import pandas as pd
from datetime import datetime
from app.utils.data_cache_manager import DataCacheManager

class TestDataCacheManager(unittest.TestCase):
    def setUp(self):
        """测试前创建临时缓存目录"""
        self.test_cache_dir = 'test_cache'
        self.cache_manager = DataCacheManager(self.test_cache_dir)
        
    def tearDown(self):
        """测试后清理临时缓存目录"""
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
            
    def test_cache_operations(self):
        """测试基本的缓存操作"""
        # 创建测试数据
        test_data = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        # 测试写入缓存
        self.cache_manager.write_cache('test', 'test_id', test_data)
        cache_path = self.cache_manager._get_cache_path('test', 'test_id')
        self.assertTrue(os.path.exists(cache_path))
        
        # 测试读取缓存
        cached_data = self.cache_manager.read_cache('test', 'test_id')
        pd.testing.assert_frame_equal(test_data, cached_data)
        
        # 测试缓存有效性检查
        self.assertTrue(self.cache_manager.is_cache_valid(cache_path))
        
    def test_get_or_update(self):
        """测试获取或更新缓存的功能"""
        test_data = pd.DataFrame({'col1': [1, 2, 3]})
        counter = {'calls': 0}
        
        def mock_data_fetcher():
            counter['calls'] += 1
            return test_data
        
        # 首次获取数据（应该调用fetcher）
        result1 = self.cache_manager.get_or_update(
            'test', 'test_id', mock_data_fetcher
        )
        pd.testing.assert_frame_equal(test_data, result1)
        self.assertEqual(counter['calls'], 1)
        
        # 再次获取（应该使用缓存）
        result2 = self.cache_manager.get_or_update(
            'test', 'test_id', mock_data_fetcher
        )
        pd.testing.assert_frame_equal(test_data, result2)
        self.assertEqual(counter['calls'], 1)  # fetcher不应该被再次调用

if __name__ == '__main__':
    unittest.main()