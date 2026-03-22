from datetime import datetime, timezone

from app.models.course import Course
from app.models.user import User
from app.services.audit import record_audit_log


def mark_lesson_completed(*, mongo_db, db, learner: User, course: Course, lesson_id: str) -> dict:
    progress_collection = mongo_db.progress
    content = mongo_db.course_contents.find_one({"course_id": course.id}) or {"lessons": []}
    lesson_ids = {lesson["lesson_id"] for lesson in content["lessons"]}
    if lesson_id not in lesson_ids:
        raise ValueError("Lesson not found for this course")

    progress = progress_collection.find_one({"course_id": course.id, "user_id": learner.id})
    completed = set(progress["completed_lessons"]) if progress else set()
    completed.add(lesson_id)
    updated_at = datetime.now(timezone.utc)
    progress_collection.update_one(
        {"course_id": course.id, "user_id": learner.id},
        {
            "$set": {"updated_at": updated_at},
            "$setOnInsert": {"course_id": course.id, "user_id": learner.id, "quiz_scores": []},
            "$addToSet": {"completed_lessons": lesson_id},
        },
        upsert=True,
    )
    record_audit_log(
        db,
        action="complete_lesson",
        entity_type="progress",
        entity_id=f"{course.id}:{lesson_id}",
        details={"course_id": course.id, "lesson_id": lesson_id},
        user=learner,
    )
    return {"course_id": course.id, "completed_lessons": sorted(completed), "updated_at": updated_at}
