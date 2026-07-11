/**
 * todo-api contract のみを前提とした API クライアント。
 * Base path は /api/v1 (openapi_summary.md の contract に準拠)。
 */

const BASE = "/api/v1";

export interface Todo {
  id: string;
  title: string;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TodoListResponse {
  items: Todo[];
}

export async function listTodos(): Promise<TodoListResponse> {
  const res = await fetch(`${BASE}/todos`);
  if (!res.ok) {
    throw new Error(`Failed to list todos: ${res.status}`);
  }
  return res.json() as Promise<TodoListResponse>;
}

export async function createTodo(title: string): Promise<Todo> {
  const res = await fetch(`${BASE}/todos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) {
    throw new Error(`Failed to create todo: ${res.status}`);
  }
  return res.json() as Promise<Todo>;
}

export async function completeTodo(id: string): Promise<Todo> {
  const res = await fetch(`${BASE}/todos/${id}/complete`, {
    method: "PATCH",
  });
  if (!res.ok) {
    throw new Error(`Failed to complete todo: ${res.status}`);
  }
  return res.json() as Promise<Todo>;
}
