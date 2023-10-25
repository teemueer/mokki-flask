import unittest
from app import create_app, db
from app.models.user import UserModel


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        user = UserModel(username="admin", password="password")
        user.save_to_db()
        res = self.client.post(
            "/login", json={"username": "admin", "password": "password"}
        )
        self.token = res.get_json()["access_token"]

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        res = self.client.post(
            "/register",
            json={
                "username": "testuser",
                "password": "testpass",
            },
        )
        self.assertEqual(res.status_code, 201)
        user = UserModel.find_by_username("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")

    def test_user_login(self):
        res = self.client.post(
            "/login",
            json={
                "username": "admin",
                "password": "password",
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("access_token", data)

    def test_bad_user_login(self):
        res = self.client.post(
            "/login",
            json={
                "username": "admin",
                "password": "1234",
            },
        )
        self.assertEqual(res.status_code, 401)

