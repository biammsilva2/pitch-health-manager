from datetime import datetime
from enum import Enum
from typing import Optional, Any
from bson import ObjectId

from pydantic import BaseModel, Field
from pydantic_core import core_schema
from loguru import logger

from pitch_health.dal import update_pitch_db


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")

        return ObjectId(value)


class PitchLocation(BaseModel):
    city: str
    country: str


class TurfType(str, Enum):
    natural = 'natural'
    artificial = 'artificial'
    hybrid = 'hybrid'


class Pitch(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    name: str
    location: PitchLocation
    turf_type: TurfType
    last_maintenance_date: datetime
    next_scheduled_maintenance: Optional[datetime] = None
    current_condition: int = Field(ge=1, le=10)
    replacement_date: datetime
    need_to_change_turf: bool = False
    pitch_analyzed_last: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str
        }

    def update_points(self, points):
        new_points = self.current_condition + points
        if new_points > 10:
            new_points = 10
        elif new_points < 1:
            new_points = 1
        logger.info(f'Pitch: {self.id} - points updated from ' +
                    f'{self.current_condition} to {new_points}')
        self.current_condition = new_points

    def save(self):
        update_pitch_db(
            filter={'_id': ObjectId(self.id)},
            update={'$set': self.model_dump()}
        )
        data = self.model_dump(mode='json')
        logger.info(f'Pitch: {self.id} - saved. Data: {str(data)}')
