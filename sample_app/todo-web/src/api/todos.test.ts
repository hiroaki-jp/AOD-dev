/**
 * 受入基準5: フロントエンドが todo-api の contract のみを前提に通信していること。
 * fetch をモックして各 API 関数が正しいエンドポイント・メソッドを呼ぶことを検証する。
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { completeTodo, createTodo, listTodos } from "./todos";

const SAMPLE_TODO = {
  id: "12345678-1234-5678-1234-567812345678",
  title: "Test TODO",
  is_completed: false,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

function mockFetch(body: unknown, ok = true, status = 200): void {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      status,
      json: () => Promise.resolve(body),
    }),
  );
}

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});

afterEach(() => {
  vi.unstubAllGlobals();
});

// ---- 受入基準5: contract エンドポイントのみを呼ぶ ----

describe("listTodos", () => {
  it("受入基準5: GET /api/v1/todos を呼ぶ", async () => {
    mockFetch({ items: [SAMPLE_TODO] });
    await listTodos();
    expect(vi.mocked(fetch)).toHaveBeenCalledWith("/api/v1/todos");
  });

  it("受入基準1: items 配列を含むレスポンスを返す", async () => {
    mockFetch({ items: [SAMPLE_TODO] });
    const result = await listTodos();
    expect(result.items).toHaveLength(1);
    expect(result.items[0].title).toBe("Test TODO");
    expect(result.items[0].is_completed).toBe(false);
  });

  it("受入基準4: APIエラー時に例外を投げる", async () => {
    mockFetch(null, false, 503);
    await expect(listTodos()).rejects.toThrow("Failed to list todos: 503");
  });
});

describe("createTodo", () => {
  it("受入基準5: POST /api/v1/todos を title 付きで呼ぶ", async () => {
    mockFetch(SAMPLE_TODO, true, 201);
    await createTodo("Test TODO");
    expect(vi.mocked(fetch)).toHaveBeenCalledWith("/api/v1/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "Test TODO" }),
    });
  });

  it("受入基準2: 作成済み TODO を返す", async () => {
    mockFetch(SAMPLE_TODO, true, 201);
    const result = await createTodo("Test TODO");
    expect(result.title).toBe("Test TODO");
    expect(result.is_completed).toBe(false);
  });

  it("受入基準4: APIエラー時に例外を投げる", async () => {
    mockFetch(null, false, 400);
    await expect(createTodo("")).rejects.toThrow("Failed to create todo: 400");
  });
});

describe("completeTodo", () => {
  it("受入基準5: PATCH /api/v1/todos/{id}/complete を呼ぶ", async () => {
    const completed = { ...SAMPLE_TODO, is_completed: true };
    mockFetch(completed);
    await completeTodo(SAMPLE_TODO.id);
    expect(vi.mocked(fetch)).toHaveBeenCalledWith(
      `/api/v1/todos/${SAMPLE_TODO.id}/complete`,
      { method: "PATCH" },
    );
  });

  it("受入基準3: 完了状態の TODO を返す", async () => {
    const completed = { ...SAMPLE_TODO, is_completed: true };
    mockFetch(completed);
    const result = await completeTodo(SAMPLE_TODO.id);
    expect(result.is_completed).toBe(true);
  });

  it("受入基準4: 存在しない TODO は例外を投げる", async () => {
    mockFetch(null, false, 404);
    await expect(completeTodo("unknown-id")).rejects.toThrow(
      "Failed to complete todo: 404",
    );
  });
});
