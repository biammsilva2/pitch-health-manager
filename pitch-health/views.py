from typing import List
from bson import ObjectId

from fastapi import APIRouter
from pymongo import ReturnDocument

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
async def create_pitch(pitch: Pitch) -> Pitch:
    if hasattr(pitch, 'id'):
        delattr(pitch, 'id')
    ret = db.pitches.insert_one(pitch.model_dump(by_alias=True))
    pitch.id = ret.inserted_id
    return pitch


@pitches_router.patch('{pitch_id}')
async def update_pitch(pitch_id: str, pitch_dict: dict) -> Pitch:
    result = db.pitches.find_one_and_update(
        filter={'_id': ObjectId(pitch_id)},
        update={'$set': pitch_dict},
        return_document=ReturnDocument.AFTER
    )
    return Pitch(**result)


@pitches_router.delete('{pitch_id}', status_code=204)
async def delete_pitch(pitch_id: str) -> None:
    db.pitches.find_one_and_delete(
        filter={'_id': ObjectId(pitch_id)}
    )
