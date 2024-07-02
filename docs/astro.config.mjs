import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

import cloudflare from "@astrojs/cloudflare";
import { pluginLineNumbers } from "@expressive-code/plugin-line-numbers";

// https://astro.build/config
export default defineConfig({
  integrations: [
    starlight({
      title: "Composable Graphs",
      social: {
        github:
          "https://github.com/truevoid-development/dagster-composable-graphs",
      },
      sidebar: [
        { label: "Overview", link: "/overview" },
        {
          label: "Guides",
          autogenerate: { directory: "guides" },
        },
      ],
      pagination: false,
      expressiveCode: {
        plugins: [pluginLineNumbers()],
        defaultProps: {
          showLineNumbers: true,
        },
      },
    }),
  ],
  output: "hybrid",
  adapter: cloudflare({
    imageService: "passthrough",
    platformProxy: { enabled: true },
  }),
  vite: {
    ssr: {
      // This should be removed once Starlight's SSR support is released
      external: ["node:url", "node:path", "node:child_process", "node:fs"],
    },
  },
});
