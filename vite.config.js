import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig(({ mode }) => {
  const isStreamlit = mode === "streamlit";

  return {
    base: "./",
    plugins: [react(), ...(isStreamlit ? [viteSingleFile()] : [])],
    build: {
      outDir: isStreamlit ? "streamlit_app/frontend" : "dist",
      emptyOutDir: true,
      assetsInlineLimit: isStreamlit ? Number.MAX_SAFE_INTEGER : 4096,
      cssCodeSplit: !isStreamlit,
    },
  };
});

