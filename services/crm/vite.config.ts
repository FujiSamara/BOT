import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [vue()],
	resolve: {
		alias: {
			"@": fileURLToPath(new URL("./src", import.meta.url)),
			"@types": fileURLToPath(new URL("./src/types.ts", import.meta.url)),
		},
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
