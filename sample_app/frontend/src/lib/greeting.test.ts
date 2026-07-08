import { describe, expect, it } from "vitest";
import { greeting } from "./greeting";

describe("greeting", () => {
  it("名前を含む挨拶を返す", () => {
    expect(greeting("sample-app")).toBe("Hello, sample-app");
  });
});
