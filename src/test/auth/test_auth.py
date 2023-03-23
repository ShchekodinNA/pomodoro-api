from unittest import TestCase
from src.auth.utils import UserCrud, secret_manager, UserDBCRUD
from src.auth.schemas import UserSchemas
from src.auth.service import Authenticator, AuthenticationToken
from src.auth.models import User
from src.auth.exceptions import HTTPException400
from src.main import app
from fastapi import HTTPException, status, Response
from pydantic.error_wrappers import ValidationError
from src.database import SessionLocal
from fastapi.testclient import TestClient


class MockUserCrud(UserCrud):

    def __init__(self, mock_db: dict):
        self.mock_db: dict = mock_db

    def get_user_hashed_password_from_username(self, username: str) -> UserSchemas.Get:
        user = self.mock_db.get(username, None)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        hashed_password = user.get('hashed_password')
        return hashed_password

    def get_user_by_username(self, username: str) -> UserSchemas.Get:
        pass

    def save_user(self, user_to_save: UserSchemas.Update) -> None:
        user = self.mock_db.get(user_to_save.username, None)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        for key, value in user_to_save.dict().items():
            if key in user:
                user[key] = value
        new_hash = secret_manager.hash_secret(user_to_save.password)
        user['hashed_password'] = new_hash
        self.mock_db[user['username']] = user


class AuthTest(TestCase):
    def setUp(self) -> None:
        self.username1 = 'tester'
        self.email1 = 'tester@email.com'
        self.plain_password1 = 'test_password'
        self.hashed_password1 = secret_manager.hash_secret(
            self.plain_password1)
        self.mock_db = {
            self.username1: {
                'username': self.username1,
                'email': self.email1,
                'hashed_password': self.hashed_password1,
                'is_active': True
            }
        }
        self.crud = MockUserCrud(mock_db=self.mock_db)
        self.authenticator = Authenticator(self.crud)

    def test_correct_authenticate(self):
        authentication_result = self.authenticator.get_auth_token_or_none(
            self.username1, self.plain_password1)
        self.assertNotEqual(authentication_result, None)

    def test_incorrect_authentication(self):
        try:
            authentication_result = self.authenticator.get_auth_token_or_none(
                self.username1, 'saass')
            raise TypeError('It must be unreacheble')
        except HTTPException as exc:
            self.assertEqual(exc.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unexistsing_user(self):
        try:
            auth_result = self.authenticator.get_auth_token_or_none(
                'Some_shit', self.plain_password1)
        except HTTPException as exc:
            self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)

    def test_try_change_with_correct_password(self):
        new_password_form = UserSchemas.FormPasswordChange(
            old_password=self.plain_password1, new_password='test_new')
        current_user = UserSchemas.Update(
            username=self.username1,
            email=self.email1,
            password=self.plain_password1,
            is_active=True,
            id=1
        )
        self.authenticator.change_user_password(
            new_password_form, current_user)

        current_user_from_db = self.mock_db[current_user.username]
        for key, value in current_user.dict().items():
            if key in current_user_from_db:
                self.assertEqual(value, current_user_from_db[key])
        self.assertNotEqual(
            current_user_from_db['hashed_password'], self.hashed_password1)


class TestDBCRUD(TestCase):
    def setUp(self) -> None:
        self.session = SessionLocal()
        self.crud = UserDBCRUD(self.session)
        self.user1 = User(
            username='someusername',
            email='some@email.com',
            hashed_password='does not matter',
            is_active=True
        )
        self.session.add(self.user1)
        self.session.flush()

    def tearDown(self) -> None:
        self.session.rollback()
        self.session.close()

    def test_get_user_by_username(self):
        retrived_user: UserSchemas.Get = self.crud.get_user_by_username(
            self.user1.username)

        inputed_dict = self.user1.__dict__
        for key, value in retrived_user.dict().items():
            if key in inputed_dict:
                self.assertEqual(value, inputed_dict[key])

    def test_get_user_by_username_incorrect(self):
        with self.assertRaises(HTTPException):
            retrived_user: UserSchemas.Get = self.crud.get_user_by_username(
                'NOT EXISTENT SHIT')

    def test_get_hashed_password(self):
        hashed_password: str = self.crud.get_user_hashed_password_from_username(
            self.user1.username)
        self.assertEqual(self.user1.hashed_password, hashed_password)

    def test_get_hashed_password_incorrect(self):
        with self.assertRaises(HTTPException):
            hahed_password: str = self.crud.get_user_hashed_password_from_username(
                'NOT EXISTENT SHIT')

    def test_update_user(self):
        username = self.user1.username
        user_scheme_to_save = UserSchemas.Update(**self.user1.__dict__)
        new_email = 'new@mail.ru'
        user_scheme_to_save.email = new_email
        self.crud.save_user(user_scheme_to_save)
        updated_user = self.crud.get_user_by_username(
            user_scheme_to_save.username)
        self.assertEqual(updated_user.email, new_email)


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
        recived_token = AuthenticationToken(**dict_response)

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
        response = self.client.post(
            '/authorization',
            params={'token': auntif_token.access_token},
            data={
                "old_password": self.plain_password1,
                "new_password": "new_password"
            }, headers={
                'accept': 'application/json',
                'Content-Type': 'application/json',
            })
        raise Exception('Not ready')

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
