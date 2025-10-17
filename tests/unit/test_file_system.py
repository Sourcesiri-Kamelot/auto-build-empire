#!/usr/bin/env python3
import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tools.file_system import write_file, read_file

class TestFileSystem(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_write_and_read_file(self):
        test_path = os.path.join(self.temp_dir, "test.txt")
        test_content = "Hello, World!"
        
        # Test write
        result = write_file(test_path, test_content)
        self.assertTrue(result["success"])
        self.assertEqual(result["path"], test_path)
        
        # Test read
        read_result = read_file(test_path)
        self.assertTrue(read_result["success"])
        self.assertEqual(read_result["content"], test_content)

    def test_write_creates_directories(self):
        nested_path = os.path.join(self.temp_dir, "nested", "dir", "test.txt")
        
        result = write_file(nested_path, "test")
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(nested_path))

if __name__ == '__main__':
    unittest.main()
