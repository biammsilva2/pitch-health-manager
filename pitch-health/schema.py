from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PitchLocation(BaseModel):
    city: str
    country: str


class TurfType(str, Enum):
    natural = 'natural'
    artificial = 'artificial'
    hybrid = 'hybrid'


class Pitch(BaseModel):
    name: str
    location: PitchLocation
    turf_type: TurfType
    last_maintenance_date: datetime
    next_scheduled_maintenance: datetime
    current_condition: int = Field(ge=1, le=10)
    replacement_date: datetime
