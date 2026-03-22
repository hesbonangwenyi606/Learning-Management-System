import { FormEvent, useEffect, useMemo, useState } from "react";

import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Activity, Course } from "../types";

export function AdminPage() {
  const { token } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [error, setError] = useState("");
  const [courseForm, setCourseForm] = useState({ title: "", description: "", category: "" });
  const [lessonForm, setLessonForm] = useState({
    courseId: "",
    title: "",
    content_type: "text",
    content: "",
  });

  async function loadAdminData() {
    if (!token) {
      return;
    }
    try {
      const [myCourses, logs] = await Promise.all([
        apiRequest<Course[]>("/courses/mine", { token }),
        apiRequest<Activity[]>("/activities", { token }),
      ]);
      setCourses(myCourses);
      setActivities(logs);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load admin data");
    }
  }

  useEffect(() => {
    loadAdminData();
  }, [token]);

  async function createCourse(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setError("");
    try {
      await apiRequest("/courses", { method: "POST", token, body: courseForm });
      setCourseForm({ title: "", description: "", category: "" });
      await loadAdminData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create course");
    }
  }

  async function addLesson(event: FormEvent) {
    event.preventDefault();
    if (!token || !lessonForm.courseId) {
      return;
    }
    setError("");
    try {
      await apiRequest(`/courses/${lessonForm.courseId}/lessons`, {
        method: "POST",
        token,
        body: {
          title: lessonForm.title,
          content_type: lessonForm.content_type,
          content: lessonForm.content,
        },
      });
      setLessonForm({ courseId: "", title: "", content_type: "text", content: "" });
      await loadAdminData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add lesson");
    }
  }

  const recentActivities = useMemo(() => activities.slice(0, 10), [activities]);

  return (
    <section className="admin-grid">
      <div className="panel stack">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Admin Workspace</p>
            <h1>Course authoring</h1>
          </div>
        </div>
        {error && <p className="error-text">{error}</p>}
        <form className="stack" onSubmit={createCourse}>
          <h2>Create course</h2>
          <label>
            Title
            <input
              value={courseForm.title}
              onChange={(e) => setCourseForm((prev) => ({ ...prev, title: e.target.value }))}
              minLength={3}
              required
            />
          </label>
          <label>
            Category
            <input
              value={courseForm.category}
              onChange={(e) => setCourseForm((prev) => ({ ...prev, category: e.target.value }))}
              minLength={2}
              required
            />
          </label>
          <label>
            Description
            <textarea
              value={courseForm.description}
              onChange={(e) => setCourseForm((prev) => ({ ...prev, description: e.target.value }))}
              minLength={10}
              required
            />
          </label>
          <button className="primary-button" type="submit">
            Create course
          </button>
        </form>
        <form className="stack" onSubmit={addLesson}>
          <h2>Add lesson</h2>
          <label>
            Course
            <select
              value={lessonForm.courseId}
              onChange={(e) => setLessonForm((prev) => ({ ...prev, courseId: e.target.value }))}
              required
            >
              <option value="">Select a course</option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Lesson title
            <input
              value={lessonForm.title}
              onChange={(e) => setLessonForm((prev) => ({ ...prev, title: e.target.value }))}
              minLength={3}
              required
            />
          </label>
          <label>
            Content type
            <select
              value={lessonForm.content_type}
              onChange={(e) => setLessonForm((prev) => ({ ...prev, content_type: e.target.value }))}
            >
              <option value="text">Text</option>
              <option value="video">Video</option>
            </select>
          </label>
          <label>
            Content body / URL
            <textarea
              value={lessonForm.content}
              onChange={(e) => setLessonForm((prev) => ({ ...prev, content: e.target.value }))}
              minLength={3}
              required
            />
          </label>
          <button className="secondary-button" type="submit">
            Add lesson
          </button>
        </form>
      </div>
      <div className="panel stack">
        <h2>My Courses</h2>
        <div className="stack">
          {courses.map((course) => (
            <article key={course.id} className="mini-card">
              <strong>{course.title}</strong>
              <span>{course.category}</span>
              <small>{course.lesson_count} lessons</small>
            </article>
          ))}
        </div>
        <h2>Recent Activity</h2>
        <div className="stack">
          {recentActivities.map((activity) => (
            <article key={activity.id} className="mini-card">
              <strong>{activity.action}</strong>
              <span>{activity.user_email || "system"}</span>
              <small>{new Date(activity.occurred_at).toLocaleString()}</small>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
