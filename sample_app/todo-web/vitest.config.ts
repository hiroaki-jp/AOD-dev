import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// vitest 専用設定。tsconfig.json の include 対象外のため tsc は検査しない。
// @vitejs/plugin-react は vitest が内包する vite@5 と互換性がある。
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
  },
});
