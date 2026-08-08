const DEFAULT_SITE_URL = "https://valera2872.github.io/vmeste";

export const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL?.trim() || DEFAULT_SITE_URL
).replace(/\/$/, "");

export const SITE_ORIGIN = new URL(SITE_URL).origin;
export const SITE_BASE_PATH = new URL(SITE_URL).pathname.replace(/\/$/, "");

export function absoluteUrl(pathname: string): string {
  const normalized = pathname.startsWith("/") ? pathname : `/${pathname}`;
  return `${SITE_URL}${normalized}`;
}
