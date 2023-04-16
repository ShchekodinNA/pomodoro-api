from .schemas import PomodoroSchemas, HistorySchemas
from .models import Pomodoro, PomodoroHistory
from .exceptions import HTTPException400, HTTPException409
from ..database import Base
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy.exc import DataError


class PomodoroCRUDAbstract(ABC):

    @abstractmethod
    def get_pomodoro_settings_by(self,
                                 id_: int | None = None,
                                 user_id: int | None = None
                                 ) -> PomodoroSchemas.ReadCreate:
        """
        Args:
            id (int | None, optional): first to check and return. Defaults to None. 
            user_id (int | None, optional): second to check and return. Defaults to None.
        """
        pass

    @abstractmethod
    def save_pomodoro_settings(self, pomodoro_scheme: PomodoroSchemas.Update) -> None:
        pass

    @abstractmethod
    def create_pomodoro_history(self, history_shceme: HistorySchemas.Create) -> None:
        pass


class PomodoroCRUDDB(PomodoroCRUDAbstract):

    def __init__(self, session: Session):
        self.session = session

    def get_pomodoro_settings_by(self,
                                 id_: int | None = None,
                                 user_id: int | None = None,
                                 ) -> PomodoroSchemas.ReadCreate:
        pomodoro_from_db = None
        if id_ is not None:
            pomodoro_from_db = self._get_pomodoro_by_id(id_)
        if user_id is not None and pomodoro_from_db is None:
            pomodoro_from_db = self._get_pomodoro_by_user_id(user_id)

        if pomodoro_from_db is None:
            raise HTTPException400

        pomodoro_dict = pomodoro_from_db.__dict__
        output_pomodor = PomodoroSchemas.ReadCreate(**pomodoro_dict)
        return output_pomodor

    def _get_pomodoro_by_id(self, id_: int):
        pomodoro_from_db = self.session.get(Pomodoro, id_)
        return pomodoro_from_db

    def _get_pomodoro_by_user_id(self, user_id: int):
        pomodoro_from_db = self.session.query(Pomodoro).filter(
            Pomodoro.user_id == user_id).first()
        if pomodoro_from_db is None:
            new_pomodoro_scheme = PomodoroSchemas.Update(user_id=user_id)
            pomodoro_from_db = self._create_new_pomodoro_from_scheme(
                new_pomodoro_scheme)
        return pomodoro_from_db

    def save_pomodoro_settings(self, pomodoro_scheme: PomodoroSchemas.Update) -> None:
        pomodoro_from_db = self._get_pomodoro_by_user_id(
            pomodoro_scheme.user_id)

        pomodoro_from_db = self._change_pomodoro_in_db_through_update_shceme(
            pomodoro_from_db, pomodoro_scheme)

        self._save_instance_in_db(pomodoro_from_db)

    def _create_new_pomodoro_from_scheme(self, pomodoro_create: PomodoroSchemas.Update) -> Pomodoro:
        pomodoro_dict_from_scheme = pomodoro_create.dict()
        new_pomodoro_in_db = Pomodoro(**pomodoro_dict_from_scheme)
        self._save_instance_in_db(new_pomodoro_in_db)
        return new_pomodoro_in_db

    def _save_instance_in_db(self, db_instance: Base) -> None:
        self.session.add(db_instance)
        try:
            self.session.flush()
        except DataError as exc:
            raise HTTPException409 from exc

    def _change_pomodoro_in_db_through_update_shceme(self,
                                                     db_instance: Pomodoro,
                                                     scheme: PomodoroSchemas.Update
                                                     ) -> Pomodoro:
        dict_scheme = scheme.dict()

        for key, value in dict_scheme.items():
            if value is not None:
                setattr(db_instance, key, value)
        return db_instance

    def create_pomodoro_history(self, history_shceme: HistorySchemas.Create) -> None:
        db_record = PomodoroHistory(**history_shceme.dict())
        