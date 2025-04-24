import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
export default defineConfig({
	plugins: [vue()],
	resolve: {
		alias: [
			{
				find: "@",
				replacement: fileURLToPath(new URL("./src", import.meta.url)),
			},
			{
				find: "@types",
				replacement: fileURLToPath(new URL("./src/types.ts", import.meta.url)),
			},
			{
				find: /^pdfjs-dist$/,
				replacement: "pdfjs-dist/legacy/build/pdf.mjs",
			},
		],
	},
	server: {
		host: "0.0.0.0",
		port: 5001,
	},
	envDir: "../../",
	css: {
		preprocessorOptions: {
			scss: {
				api: "modern-compiler",
				quietDeps: true,
				silenceDeprecations: ["import"],
				additionalData: `@import "@/assets/scss/_variables.scss";@import "@/assets/scss/_mixins.scss";`,
			},
		},
	},
});
