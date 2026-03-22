from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.mongo import get_mongo_db
from app.db.sql import get_db
from app.models.course import Course
from app.models.user import User
from app.schemas.course import (
    CourseCreate,
    CourseDetail,
    CourseListItem,
    CourseUpdate,
    LessonCreate,
    LessonResponse,
    LessonUpdate,
)
from app.services.courses import (
    add_lesson,
    create_course,
    delete_course,
    delete_lesson,
    get_course_or_404,
    update_course,
    update_lesson,
)

router = APIRouter(prefix="/courses", tags=["courses"])


def serialize_course(course: Course, mongo_db) -> CourseListItem:
    content = mongo_db.course_contents.find_one({"course_id": course.id}) or {"lessons": []}
    return CourseListItem(
        id=course.id,
        title=course.title,
        description=course.description,
        category=course.category,
        created_at=course.created_at,
        created_by=course.creator.full_name,
        lesson_count=len(content["lessons"]),
    )


@router.get("", response_model=list[CourseListItem])
def list_courses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    mongo_db = get_mongo_db()
    courses = db.scalars(select(Course).order_by(Course.created_at.desc())).all()
    return [serialize_course(course, mongo_db) for course in courses]


@router.get("/mine", response_model=list[CourseListItem])
def list_my_courses(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    mongo_db = get_mongo_db()
    courses = db.scalars(
        select(Course).where(Course.created_by_id == admin.id).order_by(Course.created_at.desc())
    ).all()
    return [serialize_course(course, mongo_db) for course in courses]


@router.post("", response_model=CourseListItem, status_code=201)
def create_course_endpoint(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    mongo_db = get_mongo_db()
    course = create_course(db, payload=payload, admin=admin)
    return serialize_course(course, mongo_db)


@router.put("/{course_id}", response_model=CourseListItem)
def update_course_endpoint(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    mongo_db = get_mongo_db()
    course = get_course_or_404(db, course_id)
    if course.created_by_id != admin.id:
        raise HTTPException(status_code=403, detail="You can only update your own courses")
    updated = update_course(db, course=course, payload=payload, admin=admin)
    return serialize_course(updated, mongo_db)


@router.delete("/{course_id}", status_code=204)
def delete_course_endpoint(course_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    mongo_db = get_mongo_db()
    course = get_course_or_404(db, course_id)
    if course.created_by_id != admin.id:
        raise HTTPException(status_code=403, detail="You can only delete your own courses")
    delete_course(mongo_db=mongo_db, db=db, course=course, admin=admin)


@router.get("/{course_id}", response_model=CourseDetail)
def get_course_detail(course_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    mongo_db = get_mongo_db()
    course = get_course_or_404(db, course_id)
    course_item = serialize_course(course, mongo_db)
    content = mongo_db.course_contents.find_one({"course_id": course.id}) or {"lessons": []}
    lessons = [LessonResponse(**lesson) for lesson in sorted(content["lessons"], key=lambda item: item["order"])]
    return CourseDetail(**course_item.model_dump(), lessons=lessons)


@router.post("/{course_id}/lessons", response_model=LessonResponse, status_code=201)
def add_lesson_endpoint(
    course_id: int,
    payload: LessonCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    mongo_db = get_mongo_db()
    course = get_course_or_404(db, course_id)
    if course.created_by_id != admin.id:
        raise HTTPException(status_code=403, detail="You can only add lessons to your own courses")
    lesson = add_lesson(mongo_db=mongo_db, db=db, course=course, payload=payload, admin=admin)
    return LessonResponse(**lesson)


@router.put("/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson_endpoint(
    course_id: int,
    lesson_id: str,
    payload: LessonUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    mongo_db = get_mongo_db()
    course = get_course_or_404(db, course_id)
    if course.created_by_id != admin.id:
        raise HTTPException(status_code=403, detail="You can only edit lessons in your own courses")
    lesson = update_lesson(
        mongo_db=mongo_db,
        db=db,
        course=course,
        lesson_id=lesson_id,
        payload=payload,
        admin=admin,
    )
    return LessonResponse(**lesson)


@router.delete("/{course_id}/lessons/{lesson_id}", status_code=204)
def delete_lesson_endpoint(
    course_id: int,
    lesson_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    mongo_db = get_mongo_db()
    course = get_course_or_404(db, course_id)
    if course.created_by_id != admin.id:
        raise HTTPException(status_code=403, detail="You can only delete lessons in your own courses")
    delete_lesson(mongo_db=mongo_db, db=db, course=course, lesson_id=lesson_id, admin=admin)
