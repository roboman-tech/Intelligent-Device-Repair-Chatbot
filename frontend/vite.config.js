import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    // Stable HMR when something rewrites "localhost" (avoids blank/error client pages).
    hmr: { host: "127.0.0.1", protocol: "ws", clientPort: 5173 },
    // Do not rely on Cursor’s embedded preview — use open-in-system-browser.cmd or Edge/Chrome.
    open: false,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
