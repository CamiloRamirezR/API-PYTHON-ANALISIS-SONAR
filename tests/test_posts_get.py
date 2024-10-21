import json
import uuid
from datetime import datetime, timezone, timedelta
from unittest import TestCase
from faker import Faker
from app import create_app
from db import db
from models import Post
from unittest.mock import patch, MagicMock


class TestGetPosts(TestCase):

    def setUp(self):
        super().setUp()
        app = create_app(database='sqlite:///:memory:')
        self.client = app.test_client()
        self.faker = Faker()
        self.app_ctx = app.app_context()
        self.app_ctx.push()
        db.create_all()

        # Parametros de prueba
        self.route = str(uuid.uuid4())
        self.owner = str(uuid.uuid4())
        # Crear publicaciones de prueba
        self.create_post()

    def create_post(self):
        post = [
            Post(id=str(uuid.uuid4()), routeId=str(uuid.uuid4()), userId=str(uuid.uuid4()),
                 expireAt=datetime.now(timezone.utc) + timedelta(days=1),  # No expirado
                 createdAt=datetime.now(timezone.utc)),
            Post(id=str(uuid.uuid4()), routeId=str(uuid.uuid4()), userId=str(uuid.uuid4()),
                 expireAt=datetime.now(timezone.utc) - timedelta(days=1),  # Expirado
                 createdAt=datetime.now(timezone.utc) - timedelta(days=2)),
            Post(id=str(uuid.uuid4()), routeId=self.route, userId=str(uuid.uuid4()),
                 expireAt=datetime.now(timezone.utc) + timedelta(days=1),  # No expirado
                 createdAt=datetime.now(timezone.utc)),
            Post(id=str(uuid.uuid4()), routeId=str(uuid.uuid4()), userId=self.owner,
                 expireAt=datetime.now(timezone.utc) + timedelta(days=1),  # No expirado
                 createdAt=datetime.now(timezone.utc)),
        ]
        for post in post:
            db.session.add(post)
        db.session.commit()

    def tearDown(self):
        self.app_ctx.pop()
        del self.app_ctx

    @patch('requests.get')
    def test_get_post_no_filters(self, mock_get):
        # Simulación de la respuesta del API de autenticación
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": str(uuid.uuid4())}

        response = self.client.get('/posts', headers={'Authorization': 'Bearer valid_token'})
        self.assertEqual(response.status_code, 200)
        # Verifica que devuelvan datos en el formato esperado
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    @patch('requests.get')
    def test_get_post_by_route(self, mock_get):
        test_route_id = self.route

        # Simulación de la respuesta del API de autenticación
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": str(uuid.uuid4())}

        response = self.client.get(f'/posts?route={test_route_id}', headers={'Authorization': 'Bearer valid_token'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(all(post['routeId'] == test_route_id for post in data))

    @patch('requests.get')
    def test_get_post_by_owner(self, mock_get):
        test_owner_id = self.owner

        # Simulación de la respuesta del API de autenticación
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": str(uuid.uuid4())}

        response = self.client.get(f'/posts?owner={test_owner_id}', headers={'Authorization': 'Bearer valid_token'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(all(post['userId'] == test_owner_id for post in data))

    @patch('requests.get')
    def test_get_post_by_expired(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": str(uuid.uuid4())}

        # Filtrar por publicaciones no expiradas
        response = self.client.get('/posts?expire=false', headers={'Authorization': 'Bearer valid_token'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # Asegúrate de que expireAt sea un datetime aware antes de comparar
        self.assertTrue(all(
            datetime.fromisoformat(post['expireAt']).replace(tzinfo=timezone.utc) > datetime.now(timezone.utc) for post
            in data))