# Data access layer
from typing import List

from .database import db


def find_all_pitches(**kwargs) -> List[dict]:
    return db.pitches.find(**kwargs)


def find_one_pitch(**kwargs) -> dict:
    return db.pitches.find_one(**kwargs)


def update_pitch_db(**kwargs) -> dict:
    return db.pitches.find_one_and_update(**kwargs)


def delete_pitch_db(**kwargs):
    db.pitches.find_one_and_delete(**kwargs)


def insert_pitch_db(**kwargs):
    db.pitches.insert_one(**kwargs)
