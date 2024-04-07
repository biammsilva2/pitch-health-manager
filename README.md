# Pitch Health Manager

## Description

This application was made to check whether a pitch needs a:
- Turf replacement;
- Pitch maintenance;

On this application you will be able to:
- Register a new pitch;
- Update a pitch;
- Retrieve a pitch;
- Delete a pitch;
- Retrieve pitches that need maintenance;
- Retieve pitches that need a replacement;
- Analyze a single pitch

## Tech Stack

- Python
- FastAPI
- MongoDB
- Docker

## Tech choices

- Log: loguru
- API for retrieving weather information: Visual Crossing
- database connector: pymongo
- Package manager: Pipenv

## URLs

- When running on docker-compose this app will run on http://localhost:8000
- The API docs can be found on:
    - http://localhost:8000/redoc for API description
    - http://localhost:8000/docs for interactive endpoints


## How to set up

You will need docker installed on your machine, on root directory run

    $ docker-compose up mongodb fastapi

You will need to add your api key on `VISUAL_CROSSING_API_KEY` environment variable. You can create your key on: https://www.visualcrossing.com/

## How to run tests

    $ docker-compose test
