from unittest import TestCase
from src.auth.utils import secret_manager, UserDBCRUD
from src.auth.schemas import UserSchemas
from src.auth.models import User
from fastapi import HTTPException, status
from src.database import SessionLocal


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
            _ = self.crud.get_user_by_username(
                'NOT EXISTENT SHIT')

    def test_get_hashed_password(self):
        hashed_password: str = self.crud.get_user_hashed_password_from_username(
            self.user1.username)
        self.assertEqual(self.user1.hashed_password, hashed_password)

    def test_get_hashed_password_incorrect(self):
        with self.assertRaises(HTTPException):
            _ = self.crud.get_user_hashed_password_from_username(
                'NOT EXISTENT SHIT')

    def test_update_user(self):
        user_scheme_to_save = UserSchemas.Update(**self.user1.__dict__)
        new_email = 'new@mail.ru'
        user_scheme_to_save.email = new_email
        self.crud.save_user(user_scheme_to_save)
        updated_user = self.crud.get_user_by_username(
            user_scheme_to_save.username)
        self.assertEqual(updated_user.email, new_email)

    def test_create_user(self):
        user_to_create = UserSchemas.Create(
            username='newuser',
            email='new@user.com',
            password='newpassword'
        )
        self.crud.create_user(user_to_create)
        saved_user = self.crud.get_user_by_username(user_to_create.username)
        saved_hashed_password = self.crud.get_user_hashed_password_from_username(
            user_to_create.username)

        inputed_dict = user_to_create.dict()
        for key, value in saved_user.dict(exclude={'id'}).items():
            if key in inputed_dict:
                self.assertEqual(value, inputed_dict[key])
        self.assertTrue(secret_manager.is_secret_correct(
            saved_hashed_password, user_to_create.password))

    def test_create_dublicate_user(self):
        user_to_create = UserSchemas.Create(
            username='newufsafs',
            email='ns@bs.com',
            password='newsfafas'
        )
        self.crud.create_user(user_to_create)
        try:
            self.crud.create_user(user_to_create)
            raise TypeError('Cant go here')
        except HTTPException as exc:
            self.assertEqual(exc.status_code, status.HTTP_409_CONFLICT)
