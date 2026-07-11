/// <reference types="vitest" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // 開発時は todo-api(:8080) へプロキシする
      "/api": "http://localhost:8080",
    },
  },
});
