import json
import uuid
from datetime import datetime, timezone
from unittest import TestCase
from faker import Faker
from app import create_app
from db import db
from models import Post


class TestReset(TestCase):
    def setUp(self):
        app = create_app(database='sqlite:///:memory:')
        self.client = app.test_client()
        self.faker = Faker()
        self.app_ctx = app.app_context()
        self.app_ctx.push()

    def tearDown(self):
        self.app_ctx.pop()
        del self.app_ctx

    def test_reset_database(self):
        # Add 5 posts to database
        for _ in range(5):
            new_post = Post(
                id=str(uuid.uuid4()),
                routeId=str(uuid.uuid4()),
                userId=str(uuid.uuid4()),
                expireAt=datetime(1970, 1, 1, tzinfo=timezone.utc),
                createdAt=self.faker.past_datetime().replace(tzinfo=timezone.utc)
            )
            db.session.add(new_post)
        db.session.commit()

        # Call API
        result = self.client.post(
            "/posts/reset",
            data=''
        )

        # Verify status code
        self.assertEqual(result.status_code, 200)

        resp = json.loads(result.get_data())

        # Verify response
        self.assertIn("msg", resp)
