/**
 * App コンポーネントの受入基準テスト。
 * fetch をモックして API との連携を検証する。
 */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

const SAMPLE_ID = "12345678-1234-5678-1234-567812345678";
const SAMPLE_TODO = {
  id: SAMPLE_ID,
  title: "買い物に行く",
  is_completed: false,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};
const COMPLETED_TODO = { ...SAMPLE_TODO, is_completed: true };

function makeFetchMock(
  responses: Array<{ body: unknown; ok?: boolean; status?: number }>,
): ReturnType<typeof vi.fn> {
  let callIndex = 0;
  const mock = vi.fn().mockImplementation(() => {
    const r = responses[callIndex] ?? responses[responses.length - 1];
    callIndex++;
    return Promise.resolve({
      ok: r.ok ?? true,
      status: r.status ?? 200,
      json: () => Promise.resolve(r.body),
    });
  });
  return mock;
}

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});

afterEach(() => {
  vi.unstubAllGlobals();
});

// ---- 受入基準1: 一覧画面で TODO のタイトルと完了状態が表示される ----

describe("受入基準1: 一覧表示", () => {
  it("保存済み TODO のタイトルが表示される", async () => {
    vi.stubGlobal(
      "fetch",
      makeFetchMock([{ body: { items: [SAMPLE_TODO] } }]),
    );
    render(<App />);
    await screen.findByText("買い物に行く");
  });

  it("未完了状態が表示される", async () => {
    vi.stubGlobal(
      "fetch",
      makeFetchMock([{ body: { items: [SAMPLE_TODO] } }]),
    );
    render(<App />);
    await screen.findByText("未完了");
  });

  it("完了済み TODO の完了状態が表示される", async () => {
    vi.stubGlobal(
      "fetch",
      makeFetchMock([{ body: { items: [COMPLETED_TODO] } }]),
    );
    render(<App />);
    await screen.findByText("完了");
  });
});

// ---- 受入基準2: 追加フォームから妥当な TODO を送信でき、成功後に一覧へ反映される ----

describe("受入基準2: TODO 追加", () => {
  it("フォームから追加すると POST され、一覧に反映される", async () => {
    const newTodo = { ...SAMPLE_TODO, id: "new-id", title: "新しいタスク" };
    vi.stubGlobal(
      "fetch",
      makeFetchMock([
        { body: { items: [] } },          // 初回一覧取得
        { body: newTodo, status: 201 },   // POST 追加
        { body: { items: [newTodo] } },   // 追加後の一覧再取得
      ]),
    );

    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("list", { name: "TODOリスト" });

    await user.type(screen.getByLabelText("新しい TODO"), "新しいタスク");
    await user.click(screen.getByRole("button", { name: "追加" }));

    await screen.findByText("新しいタスク");
    expect(vi.mocked(fetch)).toHaveBeenCalledWith("/api/v1/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "新しいタスク" }),
    });
  });
});

// ---- 受入基準3: 完了操作を画面から実行でき、成功後に一覧へ反映される ----

describe("受入基準3: TODO 完了", () => {
  it("完了ボタンを押すと PATCH され、一覧が完了状態に更新される", async () => {
    vi.stubGlobal(
      "fetch",
      makeFetchMock([
        { body: { items: [SAMPLE_TODO] } },   // 初回一覧取得
        { body: COMPLETED_TODO },              // PATCH 完了更新
        { body: { items: [COMPLETED_TODO] } }, // 完了後の一覧再取得
      ]),
    );

    const user = userEvent.setup();
    render(<App />);

    const completeButton = await screen.findByRole("button", {
      name: "完了にする",
    });
    await user.click(completeButton);

    await waitFor(() => {
      expect(screen.queryByRole("button", { name: "完了にする" })).toBeNull();
    });
    expect(screen.getByText("完了")).toBeDefined();
    expect(vi.mocked(fetch)).toHaveBeenCalledWith(
      `/api/v1/todos/${SAMPLE_ID}/complete`,
      { method: "PATCH" },
    );
  });
});

// ---- 受入基準4: API 失敗時に画面上でエラーメッセージが表示される ----

describe("受入基準4: エラー表示", () => {
  it("一覧取得失敗時にエラーメッセージが表示される", async () => {
    vi.stubGlobal(
      "fetch",
      makeFetchMock([{ body: null, ok: false, status: 503 }]),
    );
    render(<App />);
    await screen.findByRole("alert");
    expect(screen.getByRole("alert").textContent).toContain("失敗");
  });

  it("追加失敗時にエラーメッセージが表示される", async () => {
    vi.stubGlobal(
      "fetch",
      makeFetchMock([
        { body: { items: [] } },              // 初回一覧取得は成功
        { body: null, ok: false, status: 400 }, // POST は失敗
      ]),
    );

    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("list", { name: "TODOリスト" });

    await user.type(screen.getByLabelText("新しい TODO"), "テスト");
    await user.click(screen.getByRole("button", { name: "追加" }));

    await screen.findByRole("alert");
    expect(screen.getByRole("alert").textContent).toContain("失敗");
  });

  it("完了更新失敗時にエラーメッセージが表示される", async () => {
    vi.stubGlobal(
      "fetch",
      makeFetchMock([
        { body: { items: [SAMPLE_TODO] } },     // 初回一覧取得
        { body: null, ok: false, status: 404 }, // PATCH は失敗
      ]),
    );

    const user = userEvent.setup();
    render(<App />);

    const completeButton = await screen.findByRole("button", {
      name: "完了にする",
    });
    await user.click(completeButton);

    await screen.findByRole("alert");
    expect(screen.getByRole("alert").textContent).toContain("失敗");
  });
});
