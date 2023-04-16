from unittest import TestCase
from src.auth.utils import secret_manager
from src.auth.service import AuthenticationToken
from src.auth.models import User
from src.main import app
from fastapi import status, Response
from src.database import SessionLocal
from fastapi.testclient import TestClient


class TestEndpoints(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.session = SessionLocal()
        self.plain_password1 = 'doesmatter'
        self.hashed_password1 = secret_manager.hash_secret(
            self.plain_password1)
        self.user1 = User(
            username='someusername',
            email='some@email.com',
            hashed_password=self.hashed_password1,
            is_active=True
        )
        self.session.add(self.user1)
        self.session.commit()

    def tearDown(self) -> None:
        self.session.delete(self.user1)
        self.session.commit()
        self.session.close()

    def test_authenticate(self):
        response = self._auntificate(self.user1.username, self.plain_password1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dict_response = response.json()
        _ = AuthenticationToken(**dict_response)

    def test_authenticate_incorrect(self):
        response = self._auntificate(self.user1.username, 'NO no')
        self.assertTrue(response.is_error)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_existent_user(self):
        response = self._auntificate('blahgassfas saas', 'NO no')
        self.assertTrue(response.is_error)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_password(self):
        auntif_token: AuthenticationToken = self._get_auntification_token(
            self.user1.username, self.plain_password1)
        _ = self.client.post(
            '/authorization/update_password',
            params={'token': auntif_token.access_token},
            data={
                "old_password": self.plain_password1,
                "new_password": "new_password"
            }, headers={
                'accept': 'application/json',
                'Content-Type': 'application/json',
            })

    def _get_auntification_token(self, username: str, password: str) -> AuthenticationToken:
        response = self._auntificate(username, password)
        resp_load = response.json()
        token = AuthenticationToken(**resp_load)
        return token

    def _auntificate(self, username: str, password: str) -> Response:
        response = self.client.post(
            '/authorization',
            data={
                'username': username,
                'password': password,
                'grant_type': 'password'
            },
            headers={"content-type": "application/x-www-form-urlencoded"}
        )
        return response
