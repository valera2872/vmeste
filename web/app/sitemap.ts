import type { MetadataRoute } from "next";
import {
  problemPagePath,
  publishedProblemPages,
} from "../content/problem-pages";
import { SITE_URL, absoluteUrl } from "../lib/seo/site";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: `${SITE_URL}/`,
      changeFrequency: "weekly",
      priority: 1,
    },
    ...publishedProblemPages.map((page) => ({
      url: absoluteUrl(problemPagePath(page)),
      changeFrequency: "monthly" as const,
      priority: 0.8,
    })),
  ];
}
