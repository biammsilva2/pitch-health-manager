from typing import List

from fastapi import APIRouter

from .database import db
from .schema import Pitch


pitches_router = APIRouter(
    prefix='/pitch'
)


@pitches_router.get('')
async def list_pitches() -> List[Pitch]:
    pitches = []
    for pitch in db.pitches.find():
        pitches.append(Pitch(**pitch))
    return pitches


@pitches_router.post('')
async def create_user(pitch: Pitch) -> Pitch:
    if hasattr(pitch, 'id'):
        delattr(pitch, 'id')
    ret = db.pitches.insert_one(pitch.model_dump(by_alias=True))
    pitch.id = ret.inserted_id
    return pitch
