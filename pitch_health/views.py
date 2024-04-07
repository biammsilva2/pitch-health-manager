from typing import List
from bson import errors, ObjectId

from fastapi import APIRouter, Response
from loguru import logger
from pymongo import ReturnDocument

from .schema import Pitch
from .services import PitchHealth
from .dal import find_all_pitches, find_one_pitch, \
    update_pitch_db, delete_pitch_db, insert_pitch_db


pitches_router = APIRouter(
    prefix='/pitch'
)


@pitches_router.get('')
async def list_pitches() -> List[Pitch]:
    pitches = []
    for pitch_dict in find_all_pitches():
        pitch = Pitch(**pitch_dict)

        # Every listing of pitches, the application will check
        # the health of all pitches that need checking
        PitchHealth.check_turf_health(pitch)
        pitch.save()
        pitches.append(pitch)
    return pitches


@pitches_router.post('')
async def create_pitch(pitch: Pitch) -> Pitch:
    if hasattr(pitch, 'id'):
        delattr(pitch, 'id')
    ret = insert_pitch_db(pitch.model_dump(by_alias=True))
    pitch.id = ret.inserted_id
    return pitch


@pitches_router.patch('/{pitch_id}')
async def update_pitch(pitch_id: str, pitch_dict: dict) -> Pitch:
    try:
        result = update_pitch_db(
            filter={'_id': ObjectId(pitch_id)},
            update={'$set': pitch_dict},
            return_document=ReturnDocument.AFTER
        )
        logger.info(f'Pitch: {pitch_id} - saved. Data: {str(pitch_dict)}')
    except errors.InvalidId:
        return Response(content='Item not found', status_code=404)
    else:
        return Pitch(**result)


@pitches_router.delete('/{pitch_id}', status_code=204)
async def delete_pitch(pitch_id: str) -> None:
    try:
        delete_pitch_db(
            filter={'_id': ObjectId(pitch_id)}
        )
        logger.info(f'Pitch: {pitch_id} - deleted')
    except errors.InvalidId:
        return Response(content='Item not found', status_code=404)


@pitches_router.get('/{pitch_id}/analyze')
async def analyze_pitch(pitch_id: str) -> Pitch:
    pitch_db = find_one_pitch(
        filter={'_id': ObjectId(pitch_id)}
    )
    pitch = PitchHealth.check_turf_health(Pitch(**pitch_db))
    pitch.save()
    return pitch


@pitches_router.get('/{pitch_id}/maintenance/done')
async def do_maintenance(pitch_id: str) -> Pitch:
    pitch = find_one_pitch(
        filter={'_id': ObjectId(pitch_id)}
    )
    return PitchHealth.do_maintenance(Pitch(**pitch))


@pitches_router.get('/{pitch_id}/turf/changed')
async def change_turf(pitch_id: str) -> Pitch:
    pitch_db = find_one_pitch(
        filter={'_id': ObjectId(pitch_id)}
    )
    pitch = PitchHealth.change_turf(Pitch(**pitch_db))
    pitch.save()
    return pitch


@pitches_router.get('/maintenance/needed')
async def get_all_pitches_that_needs_maintenance() -> List[Pitch]:
    pitches = find_all_pitches(
        filter={'next_scheduled_maintenance': {'$ne': None}}
    )
    return [Pitch(**pitch) for pitch in pitches]


@pitches_router.get('/turf/replacement/needed')
async def get_all_pitches_that_needs_turf_replacement() -> List[Pitch]:
    pitches = find_all_pitches(
        filter={'need_to_change_turf': True}
    )
    return [Pitch(**pitch) for pitch in pitches]
