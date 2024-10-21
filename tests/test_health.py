from unittest import TestCase
from app import create_app


class TestHealthCheck(TestCase):
    def setUp(self):
        app = create_app(database='sqlite:///:memory:')
        self.client = app.test_client()

        self.app_ctx = app.app_context()
        self.app_ctx.push()

    def tearDown(self):
        self.app_ctx.pop()
        del self.app_ctx

    def test_ping(self):
        # Call API
        result_ping = self.client.get(
            "/posts/ping",
        )

        # Verify status code
        self.assertEqual(result_ping.status_code, 200)

        # Verify response
        self.assertEqual(b'pong', result_ping.get_data())
