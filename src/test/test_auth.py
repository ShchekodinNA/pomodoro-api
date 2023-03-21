from unittest import TestCase
from src.auth.utils import UserCrud, secret_manager, UserDBCRUD
from src.auth.schemas import UserSchemas
from src.auth.service import Authenticator
from fastapi import HTTPException, status
from pydantic.error_wrappers import ValidationError
from ..database import SessionLocal


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
        self.password1 = 'mester'
        self.email1 = 'tester@email.com'
        self.hashedpass1 = '$2b$12$PzNOqIVQ.TaqNNus94N9Zu76hH397sjxTmX9K3VgV2EJ1hoQC08iu'
        self.mock_db = {
            self.username1: {
                'username': self.username1,
                'email': self.email1,
                'hashed_password': self.hashedpass1,
                'is_active': True
            }
        }
        self.crud = MockUserCrud(mock_db=self.mock_db)
        self.authenticator = Authenticator(self.crud)

    def test_correct_authenticate(self):
        authentication_result = self.authenticator.get_auth_token_or_none(
            self.username1, self.password1)
        self.assertNotEqual(authentication_result, None)

    def test_incorrect_authentication(self):

        authentication_result = self.authenticator.get_auth_token_or_none(
            self.username1, 'saass')
        self.assertEqual(authentication_result, None)

    def test_unexistsing_user(self):
        try:
            auth_result = self.authenticator.get_auth_token_or_none(
                'Some_shit', self.password1)
        except HTTPException as exc:
            self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)

    def test_try_change_with_correct_password(self):
        new_password_form = UserSchemas.FormPasswordChange(
            old_password=self.password1, new_password='test_new')
        current_user = UserSchemas.Update(
            username=self.username1,
            email=self.email1,
            password=self.password1,
            is_active=True,
            id=1
        )
        self.authenticator.change_user_password(new_password_form, current_user)
        
        current_user_from_db = self.mock_db[current_user.username]
        for key, value in current_user.dict().items():
            if key in current_user_from_db:
                self.assertEqual(value, current_user_from_db[key])
        self.assertNotEqual(current_user_from_db['hashed_password'], self.hashedpass1)


class TestDBCRUD(TestCase):
    def setUp(self) -> None:
        self.session = SessionLocal()
        self.crud = UserDBCRUD(self.session)
        
    def tearDown(self) -> None:
        self.session.close()