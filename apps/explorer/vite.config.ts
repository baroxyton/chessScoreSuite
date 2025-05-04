import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
  resolve: {
    alias: {
      chessboard2: path.resolve(
        __dirname,
        "node_modules/@chrisoakman/chessboard2/dist/chessboard2.min.mjs",
      ),
    },
  },
});
