import json
import uuid
from datetime import datetime, timezone, timedelta
from unittest import TestCase
from faker import Faker
from app import create_app
from db import db
from models import Post
from unittest.mock import patch, MagicMock


class TestCreatePost(TestCase):
    def setUp(self):
        app = create_app(database='sqlite:///:memory:')
        self.client = app.test_client()
        self.faker = Faker()
        self.app_ctx = app.app_context()
        self.app_ctx.push()

    def tearDown(self):
        self.app_ctx.pop()
        del self.app_ctx

    @patch('requests.get')  # Simula llamada al API de usuarios
    def test_create_post_success(self, mock_get):
        # Simulación de la respuesta del API de autenticación
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": str(uuid.uuid4())}

        # Datos de prueba para la publicación
        data = {
            'routeId': str(uuid.uuid4()),
            'expireAt': (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }

        # Envío de la solicitud POST
        response = self.client.post('/posts', data=json.dumps(data),
                                    headers={'Authorization': 'Bearer token', 'Content-Type': 'application/json'})

        # Verificación de la respuesta
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', json.loads(response.data))

    @patch('requests.get')
    def test_create_post_invalid_token(self, mock_get):
        mock_get.return_value.status_code = 401

        # Datos de prueba para la publicación
        data = {
            'routeId': str(uuid.uuid4()),
            'expireAt': (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }

        response = self.client.post('/posts', data=json.dumps(data), headers={'Authorization': 'Bearer invalid_token',
                                                                              'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)

    def test_create_post_missing_token(self):
        # Datos de prueba para la publicación
        data = {
            'routeId': str(uuid.uuid4()),
            'expireAt': (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }

        response = self.client.post('/posts', data=json.dumps(data), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 403)

    @patch('requests.get')
    def test_create_post_bad_request(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": str(uuid.uuid4())}

        # Datos de prueba para la publicación
        data = {
            'routeId': str(uuid.uuid4()),
            'expireAt': (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        }

        response = self.client.post('/posts', data=json.dumps(data), headers={'Authorization': 'Bearer token',
                                                                              'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 412)

