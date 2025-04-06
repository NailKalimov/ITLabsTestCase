from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from db import Base, engine
import router

app = FastAPI(title="ITLabs",
              description="Тестовое задание от компании ITLabs.\n\nПриложение на python с web-интерфейсом"
                          "для управления видеозахватом с камеры на сервере, распознаванием человека в кадре"
                          " и сохранением фотографий распознанных лиц\n\nСтек: opencv-python, fastapi",
              version="1.0")

Base.metadata.create_all(bind=engine)
print("Tables Created successfully")

# Include user router
app.include_router(router.router)
app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount("/photos", StaticFiles(directory="output_img"), name="photos")
