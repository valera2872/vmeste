import type { MetadataRoute } from "next";
import { SITE_BASE_PATH, SITE_ORIGIN, SITE_URL } from "../lib/seo/site";

export const dynamic = "force-static";

export default function robots(): MetadataRoute.Robots {
  const base = SITE_BASE_PATH || "";

  return {
    rules: [
      {
        userAgent: "*",
        allow: `${base}/`,
        disallow: [
          `${base}/cabinet/`,
          `${base}/cabinet/*`,
          `${base}/*?*`,
        ],
      },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_ORIGIN,
  };
}
