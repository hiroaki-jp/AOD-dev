import { useCallback, useEffect, useState } from "react";
import { type Todo, completeTodo, createTodo, listTodos } from "./api/todos";

export function App(): JSX.Element {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadTodos = useCallback(async () => {
    try {
      const data = await listTodos();
      setTodos(data.items);
      setError(null);
    } catch {
      setError("TODO の読み込みに失敗しました");
    }
  }, []);

  useEffect(() => {
    void loadTodos();
  }, [loadTodos]);

  const handleAdd = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmed = newTitle.trim();
    if (!trimmed) return;

    setIsSubmitting(true);
    try {
      await createTodo(trimmed);
      setNewTitle("");
      setError(null);
      await loadTodos();
    } catch {
      setError("TODO の追加に失敗しました");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleComplete = async (id: string) => {
    try {
      await completeTodo(id);
      setError(null);
      await loadTodos();
    } catch {
      setError("TODO の完了更新に失敗しました");
    }
  };

  return (
    <main>
      <h1>TODO リスト</h1>

      {error !== null && <p role="alert">{error}</p>}

      <form onSubmit={handleAdd}>
        <label htmlFor="new-todo-title">新しい TODO</label>
        <input
          id="new-todo-title"
          type="text"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="タイトルを入力"
        />
        <button type="submit" disabled={isSubmitting}>
          追加
        </button>
      </form>

      <ul aria-label="TODOリスト">
        {todos.map((todo) => (
          <li key={todo.id}>
            <span>{todo.title}</span>
            <span aria-label={`状態: ${todo.is_completed ? "完了" : "未完了"}`}>
              {todo.is_completed ? "完了" : "未完了"}
            </span>
            {!todo.is_completed && (
              <button
                type="button"
                onClick={() => handleComplete(todo.id)}
              >
                完了にする
              </button>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}
