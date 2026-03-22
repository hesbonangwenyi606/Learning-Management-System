from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.activity import router as activity_router
from app.api.auth import router as auth_router
from app.api.courses import router as course_router
from app.api.progress import router as progress_router
from app.core.config import get_settings
from app.db.mongo import get_mongo_db
from app.db.sql import Base, SessionLocal, engine
from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseCreate, LessonCreate
from app.services.auth import ensure_default_admin
from app.services.courses import add_lesson, create_course

settings = get_settings()


def seed_demo_course(db, mongo_db) -> None:
    admin = db.scalar(select(User).where(User.email == settings.admin_email.lower()))
    has_courses = db.scalar(select(Course.id))
    if not admin or has_courses:
        return

    course = create_course(
        db,
        payload=CourseCreate(
            title="Broadcast Journalism Essentials",
            description=(
                "An introductory editorial workflow course covering story planning, research, "
                "script preparation, and studio-ready delivery."
            ),
            category="Media Production",
        ),
        admin=admin,
    )
    add_lesson(
        mongo_db=mongo_db,
        db=db,
        course=course,
        payload=LessonCreate(
            title="Editorial planning fundamentals",
            content_type="text",
            content=(
                "Start each bulletin with a clear rundown, define the lead story, assign owners, "
                "and align the script with verified sources before production starts."
            ),
        ),
        admin=admin,
    )
    add_lesson(
        mongo_db=mongo_db,
        db=db,
        course=course,
        payload=LessonCreate(
            title="Studio presentation reference",
            content_type="video",
            content="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ),
        admin=admin,
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_default_admin(db, email=settings.admin_email, password=settings.admin_password)
        mongo_db = get_mongo_db()
        mongo_db.course_contents.create_index("course_id", unique=True)
        mongo_db.progress.create_index([("course_id", 1), ("user_id", 1)], unique=True)
        seed_demo_course(db, mongo_db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(course_router, prefix=settings.api_prefix)
app.include_router(progress_router, prefix=settings.api_prefix)
app.include_router(activity_router, prefix=settings.api_prefix)


@app.get("/health")
def health_check():
    return {"status": "ok"}
