import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { CourseDetail, ProgressItem } from "../types";

export function CourseDetailPage() {
  const { id } = useParams();
  const { token, user } = useAuth();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [progress, setProgress] = useState<ProgressItem[]>([]);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (!token || !id) {
      return;
    }
    Promise.all([
      apiRequest<CourseDetail>(`/courses/${id}`, { token }),
      user?.role === "learner" ? apiRequest<ProgressItem[]>("/progress/me", { token }) : Promise.resolve([]),
    ])
      .then(([courseResponse, progressResponse]) => {
        setCourse(courseResponse);
        setProgress(progressResponse);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load course"));
  }, [token, id, user?.role]);

  const completedLessons = useMemo(() => {
    if (!course) {
      return new Set<string>();
    }
    const match = progress.find((item) => item.course_id === course.id);
    return new Set(match?.completed_lessons || []);
  }, [course, progress]);

  async function completeLesson(lessonId: string) {
    if (!token || !course) {
      return;
    }
    setStatus("");
    try {
      await apiRequest(`/progress/${course.id}/lessons/${lessonId}/complete`, {
        method: "POST",
        token,
      });
      const updated = await apiRequest<ProgressItem[]>("/progress/me", { token });
      setProgress(updated);
      setStatus("Lesson marked as completed");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update progress");
    }
  }

  if (!course) {
    return <p>Loading course...</p>;
  }

  return (
    <section className="stack-lg">
      <div className="detail-hero">
        <div>
          <p className="eyebrow">{course.category}</p>
          <h1>{course.title}</h1>
          <p>{course.description}</p>
        </div>
        <div className="stat-card">
          <strong>{course.lesson_count}</strong>
          <span>Lessons</span>
          {user?.role === "learner" && (
            <small>
              {completedLessons.size}/{course.lesson_count} completed
            </small>
          )}
        </div>
      </div>
      {error && <p className="error-text">{error}</p>}
      {status && <p className="success-text">{status}</p>}
      <div className="stack">
        {course.lessons.map((lesson) => (
          <article key={lesson.lesson_id} className="lesson-card">
            <div className="lesson-card__header">
              <div>
                <span className="pill">{lesson.content_type}</span>
                <h2>{lesson.order}. {lesson.title}</h2>
              </div>
              {user?.role === "learner" && (
                <button
                  className="secondary-button"
                  disabled={completedLessons.has(lesson.lesson_id)}
                  onClick={() => completeLesson(lesson.lesson_id)}
                >
                  {completedLessons.has(lesson.lesson_id) ? "Completed" : "Mark complete"}
                </button>
              )}
            </div>
            {lesson.content_type === "video" ? (
              <a href={lesson.content} target="_blank" rel="noreferrer">
                Open video resource
              </a>
            ) : (
              <p>{lesson.content}</p>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
