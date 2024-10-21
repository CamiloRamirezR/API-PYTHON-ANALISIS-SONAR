import json
import uuid
from datetime import datetime, timezone, timedelta
from unittest import TestCase
from faker import Faker
from app import create_app
from db import db
from models import Post
from unittest.mock import patch


class TestDeletePost(TestCase):

    def setUp(self):
        super().setUp()
        app = create_app(database='sqlite:///:memory:')
        self.client = app.test_client()
        self.faker = Faker()
        self.app_ctx = app.app_context()
        self.app_ctx.push()
        db.create_all()

        # Parametros de prueba
        self.postId = "6225f5ac-687e-4e9a-8d95-405e2c94c125"
        # Crear publicaciones de prueba
        self.create_post()

    def create_post(self):
        post = Post(
            id=self.postId,
            routeId=str(uuid.uuid4()),
            userId=str(uuid.uuid4()),
            expireAt=datetime.now(timezone.utc) + timedelta(days=1),  # No expirado
            createdAt=datetime.now(timezone.utc)
        )
        db.session.add(post)
        db.session.commit()

    def tearDown(self):
        self.app_ctx.pop()
        del self.app_ctx

    def test_delete_post_no_token(self):
        response = self.client.delete(f'/posts/{self.postId}')
        self.assertEqual(response.status_code, 403)

    @patch('requests.get')
    def test_delete_post_invalid_token(self, mock_get):
        mock_get.return_value.status_code = 401
        response = self.client.delete(f'/posts/{self.postId}',
                                      headers={'Authorization': 'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)

    @patch('requests.get')
    def test_delete_post_success(self, mock_get):
        # Simulación de la respuesta del API de autenticación
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": str(uuid.uuid4())}

        response = self.client.delete(f'/posts/{self.postId}',
                                      headers={'Authorization': 'Bearer valid_token'})
        self.assertEqual(response.status_code, 200)

    @patch('requests.get')
    def test_delete_post_not_found(self, mock_get):
        # Simulación de la respuesta del API de autenticación
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": str(uuid.uuid4())}

        response = self.client.delete(f'/posts/{str(uuid.uuid4())}',
                                      headers={'Authorization': 'Bearer valid_token'})
        self.assertEqual(response.status_code, 404)

