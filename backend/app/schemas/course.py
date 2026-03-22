from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10, max_length=3000)
    category: str = Field(min_length=2, max_length=120)


class CourseUpdate(CourseCreate):
    pass


class LessonCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    content_type: Literal["text", "video"]
    content: str = Field(min_length=3, max_length=8000)


class LessonUpdate(LessonCreate):
    pass


class LessonResponse(BaseModel):
    lesson_id: str
    title: str
    content_type: Literal["text", "video"]
    content: str
    order: int


class CourseListItem(BaseModel):
    id: int
    title: str
    description: str
    category: str
    created_at: datetime
    created_by: str
    lesson_count: int


class CourseDetail(CourseListItem):
    lessons: list[LessonResponse]
