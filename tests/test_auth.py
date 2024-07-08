# tests/auth.spec.py
import unittest
from app import create_app, db
from app.models import User, Organisation

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user(self):
        response = self.client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password',
            'phone': '1234567890'
        })
        self.assertEqual(response.status_code, 201)

    def test_login_user(self):
        self.client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password',
            'phone': '1234567890'
        })
        response = self.client.post('/auth/login', json={
            'email': 'john@example.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
