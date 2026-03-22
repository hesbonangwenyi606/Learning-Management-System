export type Role = "admin" | "learner";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: Role;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  category: string;
  created_at: string;
  created_by: string;
  lesson_count: number;
}

export interface Lesson {
  lesson_id: string;
  title: string;
  content_type: "text" | "video";
  content: string;
  order: number;
}

export interface CourseDetail extends Course {
  lessons: Lesson[];
}

export interface ProgressItem {
  course_id: number;
  course_title: string;
  completed_count: number;
  total_lessons: number;
  completed_lessons: string[];
}

export interface Activity {
  id: number;
  user_email: string | null;
  role: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  details: string;
  occurred_at: string;
}
