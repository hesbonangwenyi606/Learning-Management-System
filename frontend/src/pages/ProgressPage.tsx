import { useEffect, useState } from "react";

import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { ProgressItem } from "../types";

export function ProgressPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<ProgressItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      return;
    }
    apiRequest<ProgressItem[]>("/progress/me", { token })
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load progress"));
  }, [token]);

  return (
    <section className="stack-lg">
      <div className="section-heading">
        <div>
          <p className="eyebrow">My Progress</p>
          <h1>Lesson completion by course</h1>
        </div>
      </div>
      {error && <p className="error-text">{error}</p>}
      <div className="stack">
        {items.map((item) => {
          const width = item.total_lessons ? (item.completed_count / item.total_lessons) * 100 : 0;
          return (
            <article key={item.course_id} className="progress-card">
              <div className="progress-card__header">
                <h2>{item.course_title}</h2>
                <strong>
                  {item.completed_count}/{item.total_lessons}
                </strong>
              </div>
              <div className="progress-bar">
                <span style={{ width: `${width}%` }} />
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
