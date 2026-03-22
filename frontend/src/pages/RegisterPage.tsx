import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function RegisterPage() {
  const navigate = useNavigate();
  const { register, loading } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await register({ full_name: fullName, email, password });
      navigate("/catalog");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    }
  }

  return (
    <section className="auth-card">
      <h1>Learner Registration</h1>
      <form className="stack" onSubmit={onSubmit}>
        <label>
          Full name
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} minLength={2} required />
        </label>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={8} required />
        </label>
        {error && <p className="error-text">{error}</p>}
        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Creating account..." : "Register"}
        </button>
      </form>
    </section>
  );
}
