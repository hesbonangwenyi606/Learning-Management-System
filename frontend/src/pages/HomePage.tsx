import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <section className="hero">
      <div>
        <p className="eyebrow">Minimal LMS Prototype</p>
        <h1>Teach, track, and audit learning in one focused workflow.</h1>
        <p className="hero-copy">
          This prototype supports two roles. Admins publish courses and lessons; learners browse the
          catalog, complete lessons, and monitor progress. Every important action is logged.
        </p>
        <div className="hero-actions">
          <Link className="primary-button" to="/login">
            Login
          </Link>
          <Link className="secondary-button" to="/register">
            Create learner account
          </Link>
        </div>
      </div>
      <aside className="hero-card">
        <h2>Demo credentials</h2>
        <p>
          Admin email: <strong>admin@kbc-lms.local</strong>
        </p>
        <p>
          Admin password: <strong>Admin123!</strong>
        </p>
        <small>Change these through backend environment variables for deployment.</small>
      </aside>
    </section>
  );
}
