const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";

export async function apiRequest<T>(
  path: string,
  options: {
    method?: HttpMethod;
    token?: string | null;
    body?: unknown;
  } = {},
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Unexpected API error" }));
    throw new Error(payload.detail || "Request failed");
  }

  return response.json() as Promise<T>;
}
