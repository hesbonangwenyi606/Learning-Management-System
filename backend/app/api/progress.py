from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_learner
from app.db.mongo import get_mongo_db
from app.db.sql import get_db
from app.models.course import Course
from app.models.user import User
from app.schemas.progress import CourseProgress, ProgressUpdateResponse
from app.services.courses import get_course_or_404
from app.services.progress import mark_lesson_completed

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("/{course_id}/lessons/{lesson_id}/complete", response_model=ProgressUpdateResponse)
def complete_lesson(course_id: int, lesson_id: str, db: Session = Depends(get_db), learner: User = Depends(require_learner)):
    mongo_db = get_mongo_db()
    course = get_course_or_404(db, course_id)
    try:
        updated = mark_lesson_completed(mongo_db=mongo_db, db=db, learner=learner, course=course, lesson_id=lesson_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProgressUpdateResponse(**updated)


@router.get("/me", response_model=list[CourseProgress])
def get_my_progress(db: Session = Depends(get_db), learner: User = Depends(require_learner)):
    mongo_db = get_mongo_db()
    courses = {course.id: course for course in db.scalars(select(Course)).all()}
    progress_map = {
        entry["course_id"]: entry for entry in mongo_db.progress.find({"user_id": learner.id})
    }
    progress_items: list[CourseProgress] = []
    for course in courses.values():
        content = mongo_db.course_contents.find_one({"course_id": course.id}) or {"lessons": []}
        entry = progress_map.get(course.id, {})
        progress_items.append(
            CourseProgress(
                course_id=course.id,
                course_title=course.title,
                completed_count=len(entry.get("completed_lessons", [])),
                total_lessons=len(content["lessons"]),
                completed_lessons=entry.get("completed_lessons", []),
            )
        )
    return progress_items
