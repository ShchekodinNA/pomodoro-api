from unittest import TestCase
from src.pomodoro.utils import PomodoroCRUDDB
from src.pomodoro.schemas import PomodoroSchemas, HistorySchemas
from src.pomodoro.models import Pomodoro, PomodoroHistory
from src.pomodoro import constants
from src.database import SessionLocal
from src.auth.models import User
from fastapi import HTTPException, status


class TestDBCRUD(TestCase):
    def setUp(self) -> None:
        self.session = SessionLocal()
        self.user1 = User(
            username='someusername',
            email='some@email.com',
            hashed_password='does not matter',
            is_active=True
        )
        self.user2 = User(
            username='second',
            email='other@email.com',
            hashed_password='does_not_matter',
            is_active=True,
        )
        self.session.add(self.user1)
        self.session.add(self.user2)
        self.session.flush()
        self.pomodoro1 = Pomodoro(
            user_id=self.user1.id
        )
        self.session.add(self.pomodoro1)
        self.pomodoro1_history_record1 = PomodoroHistory(
            pomodoro_id=self.pomodoro1.id,
            duration_in_seconds=1000,
        )
        self.session.add(self.pomodoro1_history_record1)
        self.crud = PomodoroCRUDDB(self.session)
        self.session.flush()

    def tearDown(self) -> None:
        self.session.rollback()
        self.session.close()

    def test_get_pomodoro_by_id(self):
        pomodoro = self.crud.get_pomodoro_settings_by(self.pomodoro1.id)

        self.assertIsInstance(pomodoro, PomodoroSchemas.ReadCreate)
        self._check_recived_pomodoro_and_db_instance(self.pomodoro1, pomodoro)

    def test_get_pomodoro_by_user_id(self):
        pomodoro = self.crud.get_pomodoro_settings_by(user_id=self.user1.id)

        self.assertIsInstance(pomodoro, PomodoroSchemas.ReadCreate)
        self._check_recived_pomodoro_and_db_instance(self.pomodoro1, pomodoro)

    def test_get_pomodoro_by_wrong_id(self):
        try:
            _ = self.crud.get_pomodoro_settings_by(99999999999)
            raise TypeError('Cant go here')
        except HTTPException as exc:
            self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_pomodoro_by_wrong_user_id(self):
        try:
            _ = self.crud.get_pomodoro_settings_by(user_id=99999999999)
            raise TypeError('Cant go here')
        except HTTPException as exc:
            self.assertEqual(exc.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_get_pomodoro_and_automatic_creation(self):
        pomodoro = self.crud.get_pomodoro_settings_by(user_id=self.user2.id)

        self.assertEqual(pomodoro.long_rest_duration,
                         constants.STARNDART_LONG_R_DURATION)
        self.assertEqual(pomodoro.short_rest_duration,
                         constants.STANDART_SHORT_R_DURATION)
        self.assertEqual(pomodoro.work_duration,
                         constants.STANDART_WORK_DURATION)
        self.assertEqual(pomodoro.number_of_sessions,
                         constants.STANDART_SESSIONS)

    def test_save_pomodoro_wich_exists(self):
        pomodoro_scheme = PomodoroSchemas.Update(**self.pomodoro1.__dict__)
        pomodoro_scheme.long_rest_duration = 55
        pomodoro_scheme.short_rest_duration = 22
        pomodoro_scheme.work_duration = 55
        pomodoro_scheme.number_of_sessions = 9
        self.crud.save_pomodoro_settings(pomodoro_scheme)

        recived_pomodoro = self.crud.get_pomodoro_settings_by(
            user_id=pomodoro_scheme.user_id)

        self._check_recived_pomodoro_and_db_instance(
            self.pomodoro1, recived_pomodoro)

        self._compare_schemas(recived_pomodoro, pomodoro_scheme)

    def test_save_pomodoro_wich_not_exists(self):
        pomodoro_scheme = PomodoroSchemas.Update(
            user_id=self.user2.id, long_rest_duration=5, short_rest_duration=11)

        self.crud.save_pomodoro_settings(pomodoro_scheme)

        recived_pomodoro = self.crud.get_pomodoro_settings_by(
            user_id=self.user2.id)

        self._compare_schemas(pomodoro_scheme, recived_pomodoro)
        
    def test_pomodoro_history_creation(self):
        history_scheme = HistorySchemas.Create(user_id=self.user1, duration_in_seconds=900)
        self.crud.create_pomodoro_history()

    def _check_recived_pomodoro_and_db_instance(
        self,
        db_pomodoro_instance: Pomodoro,
        recived_pomodoro: PomodoroSchemas.ReadCreate
    ):
        inputed_dict = db_pomodoro_instance.__dict__
        recived_dict = recived_pomodoro.dict()

        for key, value in recived_dict.items():
            self.assertEqual(value, inputed_dict[key])

    def _compare_schemas(self, first_scheme, second_scheme):
        dict_first = first_scheme.dict()
        dict_second = second_scheme.dict()

        for key, value in dict_first.items():
            if key in dict_second:
                self.assertEqual(value, dict_second[key])

        for key, value in dict_second.items():
            if key in dict_first:
                self.assertEqual(value, dict_first[key])
