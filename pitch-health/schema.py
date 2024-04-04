from datetime import datetime
from enum import Enum
from typing import Optional
from bson import ObjectId

from pydantic import BaseModel, Field


class PitchLocation(BaseModel):
    city: str
    country: str


class TurfType(str, Enum):
    natural = 'natural'
    artificial = 'artificial'
    hybrid = 'hybrid'


class Pitch(BaseModel):
    id: Optional[ObjectId] = Field(alias='_id', default=None)
    name: str
    location: PitchLocation
    turf_type: TurfType
    last_maintenance_date: datetime
    next_scheduled_maintenance: datetime
    current_condition: int = Field(ge=1, le=10)
    replacement_date: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }