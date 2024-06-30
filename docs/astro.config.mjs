import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

import cloudflare from "@astrojs/cloudflare";

// https://astro.build/config
export default defineConfig({
  integrations: [starlight({
    title: "Dagster Composable Graphs",
    social: {
      github:
        "https://github.com/truevoid-development/dagster-composable-graphs",
    },
    sidebar: [{
      label: "Guides",
      items: [
        {
          label: "Getting Started",
          link: "/guides/example/",
        },
      ],
    }, {
      label: "Reference",
      autogenerate: {
        directory: "reference",
      },
    }],
  })],
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
