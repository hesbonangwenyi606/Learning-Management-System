import { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import type { Role } from "../types";

export function ProtectedRoute({
  children,
  role,
}: {
  children: ReactNode;
  role?: Role;
}) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (role && user.role !== role) {
    return <Navigate to="/catalog" replace />;
  }

  return <>{children}</>;
}
