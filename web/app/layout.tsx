import type { Metadata, Viewport } from "next";
import "./globals.css";
import { SITE_URL } from "../lib/seo/site";
import { PwaRegister } from "./pwa-register";

const basePath = process.env.GITHUB_ACTIONS === "true" ? "/vmeste" : "";

export const metadata: Metadata = {
  metadataBase: new URL(`${SITE_URL}/`),
  title: "Вместе к цели — начать, продолжить и вернуться",
  description:
    "Не просто список дел: превратите важное намерение в ближайший посильный шаг, начните без регистрации и продолжайте без наказания за остановки.",
  applicationName: "Вместе к цели",
  alternates: {
    canonical: `${SITE_URL}/`,
  },
  openGraph: {
    type: "website",
    siteName: "Вместе к цели",
    locale: "ru_RU",
    url: `${SITE_URL}/`,
    title: "Вместе к цели — начать, продолжить и вернуться",
    description:
      "Превратите важное намерение в ближайший посильный шаг и начните без регистрации.",
  },
  manifest: `${basePath}/manifest.webmanifest`,
  icons: {
    icon: [
      {
        url: `${basePath}/icons/icon-192.svg`,
        type: "image/svg+xml",
        sizes: "192x192",
      },
      {
        url: `${basePath}/icons/icon-512.svg`,
        type: "image/svg+xml",
        sizes: "512x512",
      },
    ],
    apple: `${basePath}/icons/icon-192.svg`,
  },
  appleWebApp: {
    capable: true,
    title: "Вместе к цели",
    statusBarStyle: "black-translucent",
  },
};

export const viewport: Viewport = {
  themeColor: "#153b35",
  colorScheme: "light",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body>
        {children}
        <PwaRegister />
      </body>
    </html>
  );
}
