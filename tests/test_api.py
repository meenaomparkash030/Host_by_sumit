#!/usr/bin/env python3
import unittest
import json
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_health(self):
        r = self.client.get('/api/health')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_platform(self):
        r = self.client.get('/api/platform')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn('platform', data)
        self.assertIn('version', data)

if __name__ == '__main__':
    unittest.main()