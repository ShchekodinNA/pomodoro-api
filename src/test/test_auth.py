from unittest import TestCase
from src.auth.utils import UserCrud
from src.auth.schemas import UserSchemas
from src.auth.service import Authenticator
from pydantic.error_wrappers import ValidationError


class MockUserCrud(UserCrud):

    def __init__(self, mock_db: dict):
        self.mock_db = mock_db

    def get_user_by_username_to_auth(self, username: str) -> UserSchemas.AuthenticateUser:
        dict_user = self.mock_db.get(username, None)
        if dict_user is None:
            return None
        return_user = UserSchemas.AuthenticateUser(**dict_user)
        return return_user

    def get_user_by_username(self, username: str) -> UserSchemas.UserBase:
        pass
    
    def save_user(self, user_to_save: UserSchemas.AuthenticateUser) -> None:
        pass

class AuthTest(TestCase):
    def setUp(self) -> None:
        self.username1 = 'tester'
        self.password1 = 'mester'
        mock_db = {
            'tester': {
                'username': self.username1,
                'email': 'tester@email.com',
                'hashed_password': '$2b$12$PzNOqIVQ.TaqNNus94N9Zu76hH397sjxTmX9K3VgV2EJ1hoQC08iu',
                'is_active': True
            }
        }
        self.CRUD = MockUserCrud(mock_db=mock_db)
        self.authenticetor = Authenticator(self.CRUD)
        

    def test_correct_authenticate(self):
        authentication_result = self.authenticetor.get_auth_token_or_none(
            self.username1, self.password1)
        self.assertNotEqual(authentication_result, None)

    def test_incorrect_authentication(self):

        authentication_result = self.authenticetor.get_auth_token_or_none(
            self.username1, 'saass')
        self.assertEqual(authentication_result, None)

    def test_unexistsing_user(self):
        auth_result = self.authenticetor.get_auth_token_or_none(
            'Some_shit', self.password1)
        self.assertEqual(auth_result, None)
    
    def test_try_change_with_correct_password(self)
        new_password = UserSchemas.UpdateUserPassword(password=self.username1, new_password='test_new')
        self.authenticetor.change_user_password(update_user=)


class SchemaValidationTests(TestCase):

    def setUp(self) -> None:
        self.normal_email = 'correct@gmail.com'

    def test_incorrect_username_UserBase(self):
        with self.assertRaises(ValidationError):
            _ = UserSchemas.UserBase(username='!gggg g', email=self.normal_email)

    def test_correct_username_UserBase(self):
        _ = UserSchemas.UserBase(username='gsgagsaas', email=self.normal_email)
