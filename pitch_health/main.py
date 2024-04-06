from fastapi import FastAPI

from .views import pitches_router


app = FastAPI()
app.include_router(pitches_router)
