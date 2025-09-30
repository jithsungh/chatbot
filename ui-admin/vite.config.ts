import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 5173, // let Vite use its default port
    allowedHosts: ["fulsome-unmonopolising-mariela.ngrok-free.dev"],
    proxy: {
      "/api": {
        target: process.env.VITE_API_URL || "http://localhost:8000", // backend server
        changeOrigin: true,
        secure: false,
      },
    },
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
