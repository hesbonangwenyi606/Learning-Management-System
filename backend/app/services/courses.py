from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseCreate, LessonCreate
from app.services.audit import record_audit_log


def create_course(db: Session, *, payload: CourseCreate, admin: User) -> Course:
    course = Course(
        title=payload.title.strip(),
        description=payload.description.strip(),
        category=payload.category.strip(),
        created_by_id=admin.id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    record_audit_log(
        db,
        action="create_course",
        entity_type="course",
        entity_id=str(course.id),
        details={"title": course.title, "category": course.category},
        user=admin,
    )
    return course


def get_course_or_404(db: Session, course_id: int) -> Course:
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


def add_lesson(*, mongo_db, db: Session, course: Course, payload: LessonCreate, admin: User) -> dict:
    collection = mongo_db.course_contents
    existing = collection.find_one({"course_id": course.id})
    order = len(existing["lessons"]) + 1 if existing else 1
    lesson = {
        "lesson_id": str(uuid4()),
        "title": payload.title.strip(),
        "content_type": payload.content_type,
        "content": payload.content.strip(),
        "order": order,
    }
    if existing:
        collection.update_one({"course_id": course.id}, {"$push": {"lessons": lesson}})
    else:
        collection.insert_one(
            {
                "course_id": course.id,
                "updated_at": datetime.now(timezone.utc),
                "lessons": [lesson],
            }
        )
    record_audit_log(
        db,
        action="add_lesson",
        entity_type="lesson",
        entity_id=lesson["lesson_id"],
        details={"course_id": course.id, "title": lesson["title"]},
        user=admin,
    )
    return lesson


def update_course(db: Session, *, course: Course, payload: CourseCreate, admin: User) -> Course:
    course.title = payload.title.strip()
    course.description = payload.description.strip()
    course.category = payload.category.strip()
    db.add(course)
    db.commit()
    db.refresh(course)
    record_audit_log(
        db,
        action="update_course",
        entity_type="course",
        entity_id=str(course.id),
        details={"title": course.title, "category": course.category},
        user=admin,
    )
    return course


def delete_course(*, mongo_db, db: Session, course: Course, admin: User) -> None:
    mongo_db.course_contents.delete_one({"course_id": course.id})
    mongo_db.progress.delete_many({"course_id": course.id})
    record_audit_log(
        db,
        action="delete_course",
        entity_type="course",
        entity_id=str(course.id),
        details={"title": course.title},
        user=admin,
    )
    db.delete(course)
    db.commit()


def update_lesson(*, mongo_db, db: Session, course: Course, lesson_id: str, payload, admin: User) -> dict:
    content = mongo_db.course_contents.find_one({"course_id": course.id}) or {"lessons": []}
    lessons = content["lessons"]
    target = next((lesson for lesson in lessons if lesson["lesson_id"] == lesson_id), None)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    target.update(
        {
            "title": payload.title.strip(),
            "content_type": payload.content_type,
            "content": payload.content.strip(),
        }
    )
    mongo_db.course_contents.update_one({"course_id": course.id}, {"$set": {"lessons": lessons}})
    record_audit_log(
        db,
        action="update_lesson",
        entity_type="lesson",
        entity_id=lesson_id,
        details={"course_id": course.id, "title": target["title"]},
        user=admin,
    )
    return target


def delete_lesson(*, mongo_db, db: Session, course: Course, lesson_id: str, admin: User) -> None:
    content = mongo_db.course_contents.find_one({"course_id": course.id}) or {"lessons": []}
    lessons = content["lessons"]
    next_lessons = [lesson for lesson in lessons if lesson["lesson_id"] != lesson_id]
    if len(next_lessons) == len(lessons):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    for index, lesson in enumerate(next_lessons, start=1):
        lesson["order"] = index
    mongo_db.course_contents.update_one({"course_id": course.id}, {"$set": {"lessons": next_lessons}})
    mongo_db.progress.update_many({"course_id": course.id}, {"$pull": {"completed_lessons": lesson_id}})
    record_audit_log(
        db,
        action="delete_lesson",
        entity_type="lesson",
        entity_id=lesson_id,
        details={"course_id": course.id},
        user=admin,
    )
