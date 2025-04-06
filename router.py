import asyncio
from datetime import datetime, timedelta
from threading import Thread, Event
from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from models import Photo
from utils import start_face_recognition, get_db_session

templates = Jinja2Templates(directory="templates")
router = APIRouter()
stop_event = Event()
new_photo_event = Event()


@router.get('/', description="Корневой эндпоинт со статической страницей", summary="Main page",
            response_class=HTMLResponse, response_description="Возвращает HTML страницу с фотографиями")
def index(request: Request, db: Session = Depends(get_db_session)):
    photos = db.query(Photo).all()
    photo_urls = [photo.url for photo in photos]
    return templates.TemplateResponse("index.html", {"request": request, 'photo_urls': photo_urls})


@router.post("/start-recognition", description="Запустить захват видеопотока и распознавание лиц",
             summary="Start face recognition")
def recognition(db: Session = Depends(get_db_session)):
    face_recognition_process = Thread(target=start_face_recognition, args=[db, stop_event, new_photo_event])
    face_recognition_process.start()
    return {'message': "Face recognition is started!"}


@router.post('/stop-recognition', description="Остановить захват видеопотока и распознавание лиц",
             summary="Stop face recognition")
def stop_recognition():
    stop_event.set()
    return {'message': "Face recognition is stopped!"}


@router.get("/date-filter", description="Получить фотографии за определенный период",
            summary="Get photos by date period", response_model=list[str], response_description="Список URL фотографий")
def get_photos_by_date(start_date: str, end_date: str, db: Session = Depends(get_db_session)):
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    photos = db.query(Photo).filter(Photo.created_at.between(start, end)).limit(10).all()
    return {"photos": [photo.url for photo in photos]}


@router.get("/photos", description="Получить все фотографии", summary="Get all photos",
            response_model=list[str], response_description="Список URL фотографий")
def get_photos(db: Session = Depends(get_db_session)):
    photos = db.query(Photo).all()
    return {"photo_urls": [photo.url for photo in photos]}


@router.get("/sse", include_in_schema=False, description="Служебный эдпоинт для SSE на главной странице")
async def message_stream(request: Request):
    async def event_generator():
        count = 0
        while True:
            if new_photo_event.is_set():
                count += 1
                yield f"data: NEW FACES{count}\n\n"
                new_photo_event.clear()
            if await request.is_disconnected():
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
