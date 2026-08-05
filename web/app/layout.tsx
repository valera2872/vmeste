import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Вместе к цели",
  description:
    "Помогаем превратить важное намерение в ближайший посильный шаг.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
