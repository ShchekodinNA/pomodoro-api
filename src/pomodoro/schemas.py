from pydantic import BaseModel, Field
from .constants import (
    MAX_LONG_DURATION,
    MIN_LONG_DURATION,
    STARNDART_LONG_R_DURATION,
    MAX_SHORT_DURATION,
    MIN_SHORT_DURATION,
    STANDART_SHORT_R_DURATION,
    MIN_WORK_DURATION,
    MAX_WORK_DURATION,
    STANDART_WORK_DURATION,
    MAX_SESSIONS,
    MIN_SESSIONS,
    STANDART_SESSIONS,
)
long_rest_dur = Field(ge=MIN_LONG_DURATION, le=MAX_LONG_DURATION, default=STARNDART_LONG_R_DURATION)
short_rest_dur = Field(ge=MIN_SHORT_DURATION, le=MAX_SHORT_DURATION, default=STANDART_SHORT_R_DURATION)
work_duration = Field(ge=MIN_WORK_DURATION, le=MAX_WORK_DURATION, default=STANDART_WORK_DURATION)
numb_of_sessions = Field(ge=MIN_SESSIONS, le=MAX_SESSIONS, default=STANDART_SESSIONS)


class PomodoroSchemas:
    class ReadCreate(BaseModel):
        id: int
        user_id: int
        short_rest_duration: int = short_rest_dur
        long_rest_duration: int = long_rest_dur
        work_duration: int = work_duration
        number_of_sessions: int = numb_of_sessions

    class Delete(BaseModel):
        id: int

    class Update(BaseModel):
        user_id: int
        short_rest_duration: int = short_rest_dur
        long_rest_duration: int = long_rest_dur
        work_duration: int = work_duration
        number_of_sessions: int = numb_of_sessions

class HistorySchemas:
    class Create(BaseModel):
        user_id: int
        duration_in_seconds: int
        