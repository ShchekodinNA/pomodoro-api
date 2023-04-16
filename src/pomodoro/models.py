from sqlalchemy import (Boolean, Column, Integer, String, ForeignKey, DateTime)
from datetime import datetime
from ..database import Base
from .constants import (
    STANDART_SHORT_R_DURATION,
    STANDART_SESSIONS,
    STANDART_WORK_DURATION,
    STARNDART_LONG_R_DURATION
)

class Pomodoro(Base):
    __tablename__ = 'pomodoro'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    short_rest_duration = Column(Integer, default=STANDART_SHORT_R_DURATION)
    long_rest_duration = Column(Integer, default=STARNDART_LONG_R_DURATION)
    work_duration = Column(Integer, default=STANDART_WORK_DURATION)
    number_of_sessions = Column(Integer, default=STANDART_SESSIONS)
    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )


class PomodoroHistory(Base):
    __tablename__ = 'history_of_pomodoro'
    __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True, index=True)
    utc_end = Column(DateTime, nullable=False, default=datetime.utcnow())
    duration_in_seconds = Column(Integer, nullable=False)

    pomodoro_id = Column(
        Integer,
        ForeignKey('pomodoro.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        unique=True
    )