import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Вместе к цели — начать, продолжить и вернуться",
  description:
    "Не просто список дел: превратите важное намерение в ближайший посильный шаг, начните без регистрации и продолжайте без наказания за остановки.",
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
