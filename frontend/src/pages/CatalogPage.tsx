import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Course } from "../types";

export function CatalogPage() {
  const { token, user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      return;
    }
    apiRequest<Course[]>("/courses", { token })
      .then(setCourses)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load courses"));
  }, [token]);

  return (
    <section className="stack-lg">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Course Catalog</p>
          <h1>{user?.role === "admin" ? "Published learning paths" : "Browse available courses"}</h1>
        </div>
      </div>
      {error && <p className="error-text">{error}</p>}
      <div className="card-grid">
        {courses.map((course) => (
          <article key={course.id} className="course-card">
            <div className="course-card__meta">
              <span>{course.category}</span>
              <span>{course.lesson_count} lessons</span>
            </div>
            <h2>{course.title}</h2>
            <p>{course.description}</p>
            <div className="course-card__footer">
              <small>By {course.created_by}</small>
              <Link to={`/courses/${course.id}`}>View course</Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
