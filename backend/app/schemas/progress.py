from datetime import datetime

from pydantic import BaseModel


class ProgressUpdateResponse(BaseModel):
    course_id: int
    completed_lessons: list[str]
    updated_at: datetime


class CourseProgress(BaseModel):
    course_id: int
    course_title: str
    completed_count: int
    total_lessons: int
    completed_lessons: list[str]
