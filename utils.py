from threading import Event
import os
import cv2
from datetime import datetime
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Photo

output_img_path = os.path.join(os.getcwd(), 'output_img')


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_image(frame, db, new_photo_event: Event):
    photo_name = datetime.now().strftime("%d%m%Y_%H%M%S") + ".png"
    abs_path = os.path.join(output_img_path, photo_name)
    cv2.imwrite(abs_path, frame)
    url = "http://127.0.0.1:8000/photos/%s" % photo_name
    photo = Photo(path=abs_path, name=photo_name, url=url)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    new_photo_event.set()


# Main face recognition function
def start_face_recognition(db: Session, shutdown_event: Event, new_photo_event: Event):
    face_cascade_path = os.path.dirname(cv2.__file__) + \
                        "/data/haarcascade_frontalface_alt2.xml"
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    DURATION = 5
    video_capture = cv2.VideoCapture(0)
    quite = False
    while True:
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                              minSize=(60, 60), flags=cv2.CASCADE_SCALE_IMAGE)
        start_time = datetime.now()
        diff = (datetime.now() - start_time).seconds
        while diff <= DURATION and len(faces) > 0:
            ret, frame = video_capture.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray,
                                                  scaleFactor=1.1,
                                                  minNeighbors=5,
                                                  minSize=(60, 60),
                                                  flags=cv2.CASCADE_SCALE_IMAGE)
            cv2.putText(frame, str(diff), (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imshow("Frame", frame)
            k = cv2.waitKey(5)
            if k & 0xFF == ord("r"):  # reset the timer
                break
            if k & 0xFF == ord("q"):  # quit all
                quite = True
                break
            diff = (datetime.now() - start_time).seconds
        if diff > DURATION:
            save_image(frame, db, new_photo_event)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(5) & 0xFF == ord("q") or quite or shutdown_event.is_set():
            cv2.destroyAllWindows()
            shutdown_event.clear()
            break
