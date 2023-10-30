import unittest

from app import create_app, db
from app.models.user import UserModel
from app.models.room import RoomModel


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

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
        user = UserModel(username="testuser", password="testpass")
        user.save_to_db()

        res = self.client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "testpass",
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("access_token", data)

    def test_bad_user_login(self):
        user = UserModel(username="testuser", password="testpass")
        user.save_to_db()

        res = self.client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "1234",
            },
        )
        self.assertEqual(res.status_code, 401)

    def test_create_room(self):
        user = UserModel(username="testuser", password="testpass")
        user.save_to_db()
        token = user.get_token()

        res = self.client.post(
            "/rooms",
            json={"name": "room1"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(res.status_code, 201)

    def test_create_rooms_with_same_name(self):
        user = UserModel(username="testuser", password="testpass")
        user.save_to_db()
        token = user.get_token()

        room = RoomModel(name="test_room", user_id=user.id)
        room.save_to_db()

        res = self.client.post(
            "/rooms",
            json={"name": "test_room"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(res.status_code, 400)

    def test_create_device(self):
        user = UserModel(username="testuser", password="testpass")
        user.save_to_db()
        token = user.get_token()

        room = RoomModel(name="test_room", user_id=user.id)
        room.save_to_db()

        res = self.client.post(
            "/devices",
            json={"name": "test_device", "room_id": room.id},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(res.status_code, 201)
