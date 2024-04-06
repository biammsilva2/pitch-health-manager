from typing import List
from bson import ObjectId
from datetime import datetime

from fastapi import APIRouter
from pymongo import ReturnDocument

from .database import db
from .schema import Pitch
from .services import PitchHealth


pitches_router = APIRouter(
    prefix='/pitch'
)


@pitches_router.get('')
async def list_pitches() -> List[Pitch]:
    pitches = []
    for pitch_dict in db.pitches.find():
        pitch = Pitch(**pitch_dict)

        # Every listing of pitches, the application will check
        # the health of all pitches that need checking
        pitch_was_analyzed_today = False
        if pitch.pitch_analyzed_last is not None:
            pitch_was_analyzed_today = \
                pitch.pitch_analyzed_last.date() == datetime.now().date()
        if not pitch.need_to_change_turf and pitch_was_analyzed_today:
            PitchHealth.check_turf_health(pitch)
            pitch.save()
        pitches.append(pitch)
    return pitches


@pitches_router.post('')
async def create_pitch(pitch: Pitch) -> Pitch:
    if hasattr(pitch, 'id'):
        delattr(pitch, 'id')
    ret = db.pitches.insert_one(pitch.model_dump(by_alias=True))
    pitch.id = ret.inserted_id
    return pitch


@pitches_router.patch('/{pitch_id}')
async def update_pitch(pitch_id: str, pitch_dict: dict) -> Pitch:
    result = db.pitches.find_one_and_update(
        filter={'_id': ObjectId(pitch_id)},
        update={'$set': pitch_dict},
        return_document=ReturnDocument.AFTER
    )
    return Pitch(**result)


@pitches_router.delete('/{pitch_id}', status_code=204)
async def delete_pitch(pitch_id: str) -> None:
    db.pitches.find_one_and_delete(
        filter={'_id': ObjectId(pitch_id)}
    )


@pitches_router.get('/{pitch_id}/analyze')
async def analyze_pitch(pitch_id: str) -> Pitch:
    pitch_db = db.pitches.find_one(
        filter={'_id': ObjectId(pitch_id)}
    )
    pitch = PitchHealth.check_turf_health(Pitch(**pitch_db))
    pitch.save()
    return pitch


@pitches_router.get('/{pitch_id}/maintenance/done')
async def do_maintenance(pitch_id: str) -> Pitch:
    pitch = db.pitches.find_one(
        filter={'_id': ObjectId(pitch_id)}
    )
    return PitchHealth.do_maintenance(Pitch(**pitch))


@pitches_router.get('/{pitch_id}/turf/changed')
async def change_turf(pitch_id: str) -> Pitch:
    pitch_db = db.pitches.find_one(
        filter={'_id': ObjectId(pitch_id)}
    )
    pitch = PitchHealth.change_turf(Pitch(**pitch_db))
    pitch.save()
    return pitch


@pitches_router.get('/maintenance/needed')
async def get_all_pitches_that_needs_maintenance() -> List[Pitch]:
    pitches = db.pitches.find(
        filter={'next_scheduled_maintenance': {'$ne': None}}
    )
    return [Pitch(**pitch) for pitch in pitches]


@pitches_router.get('/turf/replacement/needed')
async def get_all_pitches_that_needs_turf_replacement() -> List[Pitch]:
    pitches = db.pitches.find(
        filter={'need_to_change_turf': True}
    )
    return [Pitch(**pitch) for pitch in pitches]
