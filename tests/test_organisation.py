# tests/test_organisation.py
import unittest
from app import create_app, db
from app.models import User, Organisation
from flask_jwt_extended import create_access_token

class OrganisationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.create_sample_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_sample_data(self):
        self.user = User(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='password',
            phone='1234567890'
        )
        db.session.add(self.user)
        db.session.commit()
        self.access_token = create_access_token(identity=self.user.id)

    def test_create_organisation(self):
        response = self.client.post('/api/organisations', json={
            'name': "John's New Organisation",
            'description': "This is John's new organisation."
        }, headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('Organisation created successfully', response.json['message'])

    def test_get_own_organisations(self):
        response = self.client.get('/api/organisations', headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('organisations', response.json['data'])

    def test_get_single_organisation(self):
        # Create an organisation
        response = self.client.post('/api/organisations', json={
            'name': "John's Another Organisation",
            'description': "This is another of John's organisations."
        }, headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        org_id = response.json['data']['orgId']

        # Get the created organisation
        response = self.client.get(f'/api/organisations/{org_id}', headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['data']['orgId'], org_id)

    def test_add_user_to_organisation(self):
        # Create another user
        another_user = User(
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            password='password',
            phone='0987654321'
        )
        db.session.add(another_user)
        db.session.commit()

        # Create an organisation
        response = self.client.post('/api/organisations', json={
            'name': "John's New Organisation",
            'description': "This is John's new organisation."
        }, headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        org_id = response.json['data']['orgId']

        # Add Jane to John's organisation
        response = self.client.post(f'/api/organisations/{org_id}/users', json={
            'userId': another_user.id
        }, headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('User added to organisation successfully', response.json['message'])

if __name__ == '__main__':
    unittest.main()
