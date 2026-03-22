import { ReactNode } from "react";
import { Link, NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand">
          <span>KBC</span>
          <strong>Learning Orbit</strong>
        </Link>
        <nav className="nav">
          {user ? (
            <>
              <NavLink to="/catalog">Catalog</NavLink>
              {user.role === "learner" && <NavLink to="/progress">My Progress</NavLink>}
              {user.role === "admin" && <NavLink to="/admin">Admin</NavLink>}
              <button className="ghost-button" onClick={logout}>
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login">Login</NavLink>
              <NavLink to="/register">Register</NavLink>
            </>
          )}
        </nav>
      </header>
      <main className="page">{children}</main>
    </div>
  );
}
