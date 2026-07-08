import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // 開発時は backend(:8000)へプロキシする
      "/api": "http://localhost:8000",
      "/healthz": "http://localhost:8000",
    },
  },
});
