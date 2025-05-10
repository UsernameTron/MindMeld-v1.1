import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';
// @ts-expect-error: No types for rollup-plugin-filesize
import filesize from 'rollup-plugin-filesize';

export default defineConfig({
  plugins: [
    tsconfigPaths(),
    // Bundle size monitoring
    filesize(),
  ],
});
