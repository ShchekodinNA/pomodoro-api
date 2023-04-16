from unittest import TestCase
from src.auth.utils import UserCrud, secret_manager
from src.auth.schemas import UserSchemas
from src.auth.service import Authenticator
from fastapi import HTTPException, status


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

    def create_user(self, user_to_create: UserSchemas.Create) -> None:
        pass

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
        self.new_password1 = 'new_password'
        self.hashed_new_password1 = secret_manager.hash_secret(
            self.plain_password1
        )
        self.crud = MockUserCrud(mock_db=self.mock_db)
        self.authenticator = Authenticator(self.crud)

    def test_correct_authenticate(self):
        authentication_result = self.authenticator.get_auth_token_or_none(
            self.username1, self.plain_password1)
        self.assertNotEqual(authentication_result, None)

    def test_incorrect_authentication(self):
        try:
            _ = self.authenticator.get_auth_token_or_none(
                self.username1, 'saass')
            raise TypeError('It must be unreacheble')
        except HTTPException as exc:
            self.assertEqual(exc.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unexistsing_user(self):
        try:
            _ = self.authenticator.get_auth_token_or_none(
                'Some_shit', self.plain_password1)
        except HTTPException as exc:
            self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)

    def test_try_change_with_correct_password(self):
        new_password_form = UserSchemas.FormPasswordChange(
            old_password=self.plain_password1, new_password=self.new_password1)
        current_user = self._user1_get_scheme()
        self.authenticator.change_user_password(
            new_password_form, current_user)

        current_user_from_db = self.mock_db[current_user.username]
        for key, value in current_user.dict().items():
            if key in current_user_from_db:
                self.assertEqual(value, current_user_from_db[key])
        self.assertNotEqual(
            current_user_from_db['hashed_password'], self.hashed_password1)

    def test_try_change_with_incorrect_input_password(self):
        new_password_form = UserSchemas.FormPasswordChange(
            old_password='shitggasa', new_password=self.new_password1)
        current_user = self._user1_get_scheme()
        try:
            self.authenticator.change_user_password(
                new_password_form, current_user)
            raise TypeError('It should not work')
        except HTTPException as exc:
            self.assertEqual(exc.status_code, status.HTTP_401_UNAUTHORIZED)
        current_user_from_db = self.mock_db[current_user.username]
        self.assertEqual(
            current_user_from_db['hashed_password'], self.hashed_password1)

    def _user1_get_scheme(self) -> UserSchemas.Get:
        return UserSchemas.Get(
            username=self.username1,
            email=self.email1,
            is_active=True,
            id=1
        )

    def test_try_change_with_similar_passwords(self):
        new_password_form = UserSchemas.FormPasswordChange(
            old_password=self.plain_password1, new_password=self.plain_password1)
        current_user = self._user1_get_scheme()
        try:
            self.authenticator.change_user_password(
                new_password_form, current_user)
            raise TypeError('It should not work')
        except HTTPException as exc:
            self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)
        current_user_from_db = self.mock_db[current_user.username]
        self.assertEqual(
            current_user_from_db['hashed_password'], self.hashed_password1)

    def _user1_get_scheme(self) -> UserSchemas.Get:
        return UserSchemas.Get(
            username=self.username1,
            email=self.email1,
            is_active=True,
            id=1
        )

