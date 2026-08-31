#!/usr/bin/env python3
import unittest
import json
from app import app, db_query, init_db

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        init_db()
    
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def test_api_health(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_api_platform(self):
        response = self.client.get('/api/platform')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('platform', data)

if __name__ == '__main__':
    unittest.main()