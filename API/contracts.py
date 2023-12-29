from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TaskStatus(Enum):
    Pending = 0
    Success = 1
    Failed = 2


@dataclass
class Task:
    id: str
    type_id: str

    question: str
    user_hint: Optional[str]

    team_answer: Optional[str]
    status: TaskStatus
    points: int
    cost: int


@dataclass
class Round:
    id: str
    start_timestamp: datetime
    end_timestamp: datetime
    can_choose_type: bool


@dataclass
class Challenge:
    id: str
    title: Optional[str]
    description: Optional[str]
    rounds: list[Round]
